import os
import re
import subprocess
import time
import concurrent.futures

# ==========================================
# CONFIGURATION
# ==========================================
# Path to the directory containing joern-scan, or leave as "" if joern-scan is in your system PATH
JOERN_DIRECTORY = "" 
# The command to execute Joern. (If you require sudo in your env, change to "sudo joern-scan")
JOERN_CMD = "joern-scan" 
# ==========================================


def EnsureDirectories(inputDir, outputDir):
    """
    Ensures the input and output directories exist and checks
    if 'True' and 'False' subdirectories are present in the input directory.
    """
    os.makedirs(inputDir, exist_ok=True)
    os.makedirs(outputDir, exist_ok=True)

    trueDir = os.path.join(inputDir, "True")
    falseDir = os.path.join(inputDir, "False")

    if not os.path.exists(trueDir) or not os.path.exists(falseDir):
        raise ValueError(f"The directory '{inputDir}' must contain 'True' and 'False' subdirectories.")

    return trueDir, falseDir

def ToFile(data, filePath):
    """Writes data to the specified file, handling nested lists and all types of input."""
    if not data:
        print(f"No data to write to {filePath}")
        with open(filePath, 'w') as f: 
            pass
        return

    flat_data = []

    def flatten(item):
        if isinstance(item, list):
            for sub_item in item:
                flatten(sub_item)
        else:
            flat_data.append(str(item))

    for item in data:
        flatten(item)

    with open(filePath, 'w') as f:
        f.write("\n".join(flat_data))

    print(f"Results saved to {filePath}")


def JouernRun(query, filePath):
    """
    Runs the joern-scan tool with the target query on the target file.
    Returns only the lines matching 'Result:'.
    
    Args:
        query(str): target query
        filePath(str): target path

    return:
        results(list)
    """
    try:
        # Build the command string
        cmd = f"{JOERN_CMD} --names {query} {filePath}"
        if JOERN_DIRECTORY:
             cmd = f"./{JOERN_CMD} --names {query} {filePath}"
             
        output = subprocess.run(
            cmd,
            shell=True,
            cwd=JOERN_DIRECTORY if JOERN_DIRECTORY else None,
            capture_output=True,
            text=True,
            check=True, 
            timeout=300 # 5-minute timeout per scan
        )
    except subprocess.CalledProcessError as e:
        print(f"Error while running joern-scan on {filePath}: {e.stderr or e.stdout or e}")
        return []
    except subprocess.TimeoutExpired:
        print(f"Timeout while running joern-scan on {filePath}")
        return []

    results = []
    if output.stdout:
        results = re.findall(r"^Result:.*", output.stdout, re.MULTILINE)

    return results

def EvalScore(trueResultsPath, falseResultsPath):
    """
    Evaluates the results and calculates performance metrics 
    (TP, TN, FP, FN, Precision, Recall, Accuracy, F1-Score).

    Logic:
    For trueResultsPath:
      - If the file block has at least one "Result:" line -> TP
      - If the file block has no "Result:" line -> FN
    For falseResultsPath:
      - If the file block has any "Result:" line -> FP
      - If the file block has no "Result:" line -> TN
    """
    def process_file_blocks(results_text):
        file_blocks = []
        block = []
        lines = [line for line in results_text.split("\n") if line.strip()]
        if not lines:
            return []

        for line in lines:
            if line.startswith("Results of file:"):
                if block: 
                    file_blocks.append(block)
                block = [line] 
            elif line.startswith("------------------------------"):
                if block:
                    block.append(line)
                    file_blocks.append(block)
                    block = []
            elif block: 
                block.append(line)
        if block: 
            file_blocks.append(block)
        return file_blocks

    def count_results(file_blocks):
        result_count = {"has_results": 0, "no_results": 0}
        for block in file_blocks:
            if not block: continue
            has_result = any("Result:" in line for line in block)
            if has_result:
                result_count["has_results"] += 1
            else:
                result_count["no_results"] += 1
        return result_count

    try:
        with open(trueResultsPath, 'r') as f:
            trueResultsText = f.read()
    except FileNotFoundError:
        trueResultsText = ""

    try:
        with open(falseResultsPath, 'r') as f:
            falseResultsText = f.read()
    except FileNotFoundError:
        falseResultsText = ""

    true_file_blocks = process_file_blocks(trueResultsText)
    false_file_blocks = process_file_blocks(falseResultsText)

    true_counts = count_results(true_file_blocks)
    false_counts = count_results(false_file_blocks)

    TP = true_counts["has_results"]
    FN = true_counts["no_results"]
    FP = false_counts["has_results"]
    TN = false_counts["no_results"]

    precision = TP / (TP + FP) if (TP + FP) != 0 else 0
    recall = TP / (TP + FN) if (TP + FN) != 0 else 0
    accuracy = (TP + TN) / (TP + TN + FP + FN) if (TP + TN + FP + FN) != 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) != 0 else 0

    results_summary = (
        f"True Positives (TP): {TP}\n"
        f"False Negatives (FN): {FN}\n"
        f"False Positives (FP): {FP}\n"
        f"True Negatives (TN): {TN}\n"
        f"Total True Samples: {TP + FN}\n"
        f"Total False Samples: {FP + TN}\n"
        f"Precision: {precision * 100:.2f}%\n"
        f"Recall: {recall * 100:.2f}%\n"
        f"Accuracy: {accuracy * 100:.2f}%\n"
        f"F1-Score: {f1_score:.2f}\n"
    )

    return results_summary

def parser(query, inputDir, outputDir, max_workers=None):
    """
    Scans files in the specified input directory with Joern-scan using a query,
    utilizing a ThreadPool for concurrent scanning.
    
    Args:
        query (str): The query to run on the code files.
        inputDir (str): The directory containing the input files.
        outputDir (str): The directory where results will be saved.
        max_workers (int, optional): Max number of threads. Defaults to os.cpu_count().
    Returns: None
    """
    if max_workers is None:
        max_workers = os.cpu_count() or 4 

    print(f"Using up to {max_workers} threads for Joern scans.")
    truePath, falsePath = EnsureDirectories(inputDir, outputDir)

    tasks_to_submit = []
    true_files_original_order = []
    
    for code_filename in sorted(os.listdir(truePath)): 
        codePath = os.path.join(truePath, code_filename)
        if os.path.isfile(codePath):
            tasks_to_submit.append({'path': codePath, 'label': 'TRUE', 'original_filename': code_filename})
            true_files_original_order.append(codePath)

    false_files_original_order = []
    for code_filename in sorted(os.listdir(falsePath)): 
        codePath = os.path.join(falsePath, code_filename)
        if os.path.isfile(codePath):
            tasks_to_submit.append({'path': codePath, 'label': 'FALSE', 'original_filename': code_filename})
            false_files_original_order.append(codePath)

    if not tasks_to_submit:
        print("No files found to scan in True or False directories.")
        return

    scan_outputs = {} 

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_taskinfo = {
            executor.submit(JouernRun, query, task_info['path']): task_info
            for task_info in tasks_to_submit
        }
        print(f"Submitted {len(future_to_taskinfo)} scan tasks to the thread pool.")

        for i, future in enumerate(concurrent.futures.as_completed(future_to_taskinfo)):
            task_info = future_to_taskinfo[future]
            codePath = task_info['path']
            try:
                scan_result_lines = future.result() 
                scan_outputs[codePath] = scan_result_lines
                print(f"({i+1}/{len(future_to_taskinfo)}) Completed scan for: {codePath}")
            except Exception as exc:
                print(f"Scan for {codePath} generated an exception: {exc}")
                scan_outputs[codePath] = [f"Error during scan: {exc}"] 

    TrueResults, FalseResults = [], []

    for codePath in true_files_original_order:
        TrueResults.append(f"Results of file: {codePath} TrueLabel TRUE")
        TrueResults.extend(scan_outputs.get(codePath, ["Error: Scan results not found."]))
        TrueResults.append("-" * 30)

    for codePath in false_files_original_order:
        FalseResults.append(f"Results of file: {codePath} TrueLabel FALSE")
        FalseResults.extend(scan_outputs.get(codePath, ["Error: Scan results not found."]))
        FalseResults.append("-" * 30)

    cwe_id = os.path.basename(os.path.normpath(inputDir))
    trueResultsPath = os.path.join(inputDir, f'{cwe_id}-True-Results.txt')
    falseResultsPath = os.path.join(inputDir, f'{cwe_id}-False-Results.txt')
    
    ToFile(TrueResults, trueResultsPath)
    ToFile(FalseResults, falseResultsPath)

    evaluationResults = EvalScore(trueResultsPath, falseResultsPath)
    evalResultsPath = os.path.join(outputDir, f'{cwe_id}-Score-Results.txt')
    
    print("\nEvaluation Score:")
    print(evaluationResults)
    ToFile([evaluationResults], evalResultsPath)

if __name__ == "__main__":
    start_time = time.time()
    
    # Generic Output Directory
    output_base_dir = './output_evaluations' 
    os.makedirs(output_base_dir, exist_ok=True)

    # Define your CWEs and Joern queries here
    cwe_tests = [
        {'name': 'CWE-617', 'query': 'reachable-assertion', 'input_dir': './datasets/CWE-617'}
    ]

    for test_params in cwe_tests:
        print(f"\n----- Processing {test_params['name']} -----")
        parser(
            query=test_params['query'],
            inputDir=test_params['input_dir'],
            outputDir=os.path.join(output_base_dir, test_params['name']), 
            max_workers=os.cpu_count() or 4 # You can adjust this or let it default
        )

    print(f"\nTotal execution time: {(time.time() - start_time):.4f} seconds")
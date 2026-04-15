import os
import pandas as pd
from openai import OpenAI
import time
import datetime

# ==========================================
# CONFIGURATION
# ==========================================
API_KEY = "Deepseek_API_KEY"
BASE_URL = "https://api.deepseek.com"
INPUT_FILE  = r"data/input.csv"
OUTPUT_CSV  = r"results/output.csv"
LOG_FILE    = r"logs/run.log"
MODEL_NAME = "deepseek-chat"
ROWS_TO_TEST = None # Use 'None' for the full dataset

# Number of rows already done
START_FROM_ROW = 1000

# Initialize Client
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def run_test():
    # Start the Timer
    start_total_time = time.time()

    # 1. Load Data
    try:
        df = pd.read_csv(INPUT_FILE)
        
        if ROWS_TO_TEST is None:
            df_subset = df.iloc[START_FROM_ROW:].copy()
            count_str = f"Remaining {len(df_subset)} rows (Skipping first {START_FROM_ROW})"
        else:
            df_subset = df.iloc[START_FROM_ROW : START_FROM_ROW + ROWS_TO_TEST].copy()
            count_str = f"{ROWS_TO_TEST} rows (Index {START_FROM_ROW} to {START_FROM_ROW + ROWS_TO_TEST})"
            
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_FILE}")
        return

    # 2. FILE PREPARATION
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n\n--- RESUMING EXECUTION FROM ROW INDEX {START_FROM_ROW} ---\n\n")

    if not os.path.exists(OUTPUT_CSV):
        pd.DataFrame(columns=["predictions", "true_labels", "is_vul"]).to_csv(OUTPUT_CSV, index=False)
        print(f"Created new Output CSV: {OUTPUT_CSV}")
    else:
        print(f"Found existing CSV. Appending results to: {OUTPUT_CSV}")

    results_batch = []
    total_match = 0
    total_mismatch = 0
    total_errors = 0

    print(f"Starting test on: {count_str}")
    print("-" * 50)

    # 3. Iterate through rows
    for index, row in df_subset.iterrows():
        true_label = row.get('CWE', 'Unknown')
        code = row.get('Function', '')
        is_vul_status = row.get('is_vul', False)
        
        messages = [
            {'role': 'system', 'content': 'You are cyber security engineer and want to read C code and detect the vulnerability CWE number in the code'},
            {'role': 'user', 'content': f'Look at the following C code and print the type of the vulnerabilities and the type of CWE in this code if and only if exists, only print the number of CWE without any explanation and without writing the code again, if there is no vulnerability print secure:\n\n{code}'}
        ]

        # 4. Call API
        prediction = "ERROR"
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # Added timeout=30 to prevent it from hanging forever if network drops
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=1.0, 
                    max_tokens=64,
                    timeout=30 
                )
                prediction = response.choices[0].message.content.strip()
                
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(f"--- ROW ID: {index} ---\n") 
                    f.write(f"PROMPT:\n{messages[1]['content']}\n")
                    f.write(f"RESPONSE:\n{prediction}\n")
                    f.write(f"TRUE LABEL: {true_label}\n")
                    f.write("="*30 + "\n\n")
                
                break 

            except Exception as e:
                print(f"  [Attempt {attempt+1}/{max_retries}] Error on row {index}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2) 
                else:
                    prediction = "ERROR"
                    total_errors += 1
                    with open(LOG_FILE, 'a', encoding='utf-8') as f:
                        f.write(f"--- ROW ID: {index} ---\nERROR: {e}\n\n")

        # 5. Status Check
        p_clean = prediction.lower()
        t_clean = str(true_label).lower()

        is_match = False
        if p_clean == t_clean:
            is_match = True
        elif p_clean == "secure" and t_clean == "safe":
            is_match = True
        
        status_str = "MATCH" if is_match else "MISMATCH"
        
        if is_match:
            total_match += 1
        else:
            total_mismatch += 1

        print(f"Row {index + 1} | True: {true_label} | Pred: {prediction} | Status: {status_str}")

        # 6. Add to Batch
        results_batch.append({
            "predictions": prediction,
            "true_labels": true_label,
            "is_vul": is_vul_status
        })

        if len(results_batch) >= 50:
            df_batch = pd.DataFrame(results_batch)
            df_batch.to_csv(OUTPUT_CSV, mode='a', header=False, index=False)
            results_batch = [] 
            print("  [Checkpoint: Progress Saved]")

    # 7. Save Remaining Rows
    if results_batch:
        df_batch = pd.DataFrame(results_batch)
        df_batch.to_csv(OUTPUT_CSV, mode='a', header=False, index=False)

    # ==========================================
    # FINAL SUMMARY CALCULATION
    # ==========================================
    end_total_time = time.time()
    elapsed_seconds = end_total_time - start_total_time
    # Convert format to HH:MM:SS
    elapsed_str = str(datetime.timedelta(seconds=int(elapsed_seconds)))

    summary_text = (
        f"EXECUTION SUMMARY\n"
        f"--------------------------------------------------\n"
        f"Total Time Taken    : {elapsed_str}\n"
        f"Last Row Processed  : {index + 1}\n"
        f"New Errors          : {total_errors}\n"
        f"New MATCH           : {total_match}\n"
        f"New MISMATCH        : {total_mismatch}\n"
        f"--------------------------------------------------\n"
        f"Done! Results appended to {OUTPUT_CSV}\n"
        f"Full logs appended to {LOG_FILE}\n"
    )

    # Print to Terminal
    print("\n" + "-" * 50)
    print(summary_text)

    # Write to Log File
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write("\n" + "="*50 + "\n")
        f.write(summary_text)
        f.write("="*50 + "\n")

if __name__ == "__main__":
    run_test()
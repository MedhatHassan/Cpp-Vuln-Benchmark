import pandas as pd
import re
import os
import matplotlib.pyplot as plt
import numpy as np

def RemoveComments(df, targetColumn):
    """
    Removes comments from the specified column of a pandas DataFrame. (Overwrite the target column after removing the comments)
    Handles multi-line code strings, ensuring only comments are removed while preserving code structure.
    
    Args:
        df (pd.DataFrame): The input DataFrame.
        targetColumn (str): The name of the column to clean comments from.
    
    Returns:
        NONE
    """
    # Ensure targetColumn exists
    if targetColumn not in df.columns:
        raise ValueError(f"Column '{targetColumn}' not found in the DataFrame.")
    
    def cleanComments(code):
        if isinstance(code, str):
            # Step 1: Remove multi-line comments (/* ... */)
            code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)

            # Step 2: Split the code into lines
            lines = code.split('\n')
            
            # Step 3: Remove single-line comments (#, //) from each line
            cleanedLines = [re.sub(r'(//.*$|#.*$)', '', line).rstrip() for line in lines]
            
            # Step 4: Rejoin lines to maintain the original structure
            code = '\n'.join(cleanedLines).strip()
        return code

    # Overwrite the target column after removing the comments
    df[targetColumn] = df[targetColumn].apply(cleanComments)


# --- Helper Functions for Parsing ---
def _parse_true_labels(trueLabelStr):
    """Helper to normalize true labels consistently."""
    if isinstance(trueLabelStr, str):
        strippedLabel = trueLabelStr.strip()
        if not strippedLabel: # Handle empty string after stripping
            return []
        if ',' in strippedLabel: # Handle list (ex: "[CWE-1 , CWE-2]")
            return [cwe.strip() for cwe in strippedLabel.split(',') if cwe.strip()]
        else: # Single CWE or "Safe"
            return [strippedLabel]
    return [] # Return empty list for non-string or None

def _parse_multiclass_prediction(predictionStr):
    """Helper for multiclass model predictions (defaults is Safe)."""
    if isinstance(predictionStr, str):
        stripped = predictionStr.strip()
        if not stripped: # Handle empty prediction string
            return ["Safe"]
        if stripped.startswith("CWE-"): # Handle prediction explicit CWE-id
            return [stripped]
        # Case-insensitive check for explicit "Safe"
        elif stripped.lower() == "safe":
            return ["Safe"]
        else: # Default is Safe for other non-CWE strings
            return ["Safe"]
    return ["Safe"] # Default for non-string predictions (e.g., None, NaN)

def _parse_generation_prediction(predictionStr):
    """Helper for generation model predictions (defaults is Safe)."""
    if isinstance(predictionStr, str):
        stripped = predictionStr.strip()
        if not stripped: # Handle empty prediction string
            return ["Safe"]
        matches = re.findall(r"CWE-(\d+)", stripped) # Search on the stripped string for all CWE-ids
        if matches:
            return [f"CWE-{idMatch}" for idMatch in matches]
        # Case-insensitive check for explicit "Safe"
        elif stripped.lower() == "safe":
            return ["Safe"]
        else: # Default is Safe if no CWEs and not explicitly "Safe"
            return ["Safe"]
    return ["Safe"] # Default for non-string predictions

# --- Helper Functions for Evaluation Logic ---
def _evaluate_binary_model_as_binary(df, predictionString, trueLabelString):
    """Evaluates a strictly binary model (predictions are 0/1)."""
    TP = FP = TN = FN = 0
    for _, row in df.iterrows():
        trueLabel = row[trueLabelString]
        prediction = row[predictionString]

        # Binary classification: 1 for vulnerable, 0 for non-vulnerable
        trueIsVulnerable = (trueLabel == 1)
        predIsVulnerable = (prediction == 1)

        if predIsVulnerable and trueIsVulnerable:
            TP += 1
        elif not predIsVulnerable and not trueIsVulnerable:
            TN += 1
        elif predIsVulnerable and not trueIsVulnerable:
            FP += 1
        elif not predIsVulnerable and trueIsVulnerable:
            FN += 1
    return TP, FP, TN, FN

def _evaluate_multilabel_model_as_binary(df, predictionString, trueLabelString, modelTypeForParsing):
    """
    Evaluates multiclass/generation models with binary outcome (vulnerable vs. not vulnerable).
    A prediction is considered "vulnerable" if and only if it contains any CWE-ID.
    A true label is "vulnerable" if and only if it contains any CWE-ID (special handling for CWE-Other).
    """
    TP = FP = TN = FN = 0
    for _, row in df.iterrows():
        trueLabel = row[trueLabelString]
        prediction = row[predictionString]

        trueCwes = _parse_true_labels(trueLabel)
        
        trueIsVulnerable = any(cwe.startswith("CWE-") for cwe in trueCwes)
        # Specific rule: If "CWE-Other" is in the true label, it's always considered vulnerable for binary evaluation.
        if "CWE-Other" in trueCwes:
            trueIsVulnerable = True

        predIsVulnerable = False
        if modelTypeForParsing == 'multiclass':
            # For multiclass, a prediction is vulnerable if the (single) prediction string starts with "CWE-"
            # Using _parse_multiclass_prediction ensures it's a list, then check its content.
            parsed_pred = _parse_multiclass_prediction(prediction)
            # This parser explicitly assumes that for a modelType='multiclass', the prediction (the value from the prediction column) will be a single string.
            if parsed_pred and parsed_pred[0].startswith("CWE-"): # Should only be one item from this parser 
                predIsVulnerable = True
        elif modelTypeForParsing == 'generation':
            # For generation, a prediction is vulnerable if any extracted label starts with "CWE-"
            parsed_preds = _parse_generation_prediction(prediction)
            if any(p.startswith("CWE-") for p in parsed_preds):
                predIsVulnerable = True
        
        if predIsVulnerable and trueIsVulnerable: TP += 1
        elif not predIsVulnerable and not trueIsVulnerable: TN += 1
        elif predIsVulnerable and not trueIsVulnerable: FP += 1
        elif not predIsVulnerable and trueIsVulnerable: FN += 1
    return TP, FP, TN, FN

def _evaluate_multilabel_model_as_multiclass(df, predictionString, trueLabelString, modelTypeForParsing):
    """
    Evaluates multiclass/generation models with multiclass evaluation using micro-averaging.
    Predictions not matching CWE- format or "Safe" are treated as "Safe".
    """
    TP = FP = TN = FN = 0
    all_labels = set()
    perLabelMetrics = {}

    # Populate all unique labels (CWEs and "Safe") from true and predicted labels
    for _, row in df.iterrows():
        trueLabel = row[trueLabelString]
        prediction = row[predictionString]

        trueLabelsList = _parse_true_labels(trueLabel)
        all_labels.update(trueLabelsList)

        predictedLabelsList = []
        if modelTypeForParsing == 'multiclass':
            predictedLabelsList = _parse_multiclass_prediction(prediction)
        elif modelTypeForParsing == 'generation':
            predictedLabelsList = _parse_generation_prediction(prediction)
        all_labels.update(predictedLabelsList)
    
    all_labels.discard('') # Remove empty string (if it somehow got in)

    if not all_labels: # Error: If no labels found at all (e.g., empty df or all empty strings)
        raise ValueError(
            "Cannot perform multiclass evaluation: No valid labels (CWEs or 'Safe') "
            "found in true labels or predictions. Please check input data frame and column names."
        )

    # Calculate micro-averaged TP, FP, TN, FN
    for labelToEvaluate in all_labels:
        current_label_TP = current_label_FP = current_label_TN = current_label_FN = 0
        for _, row in df.iterrows():
            trueLabelStr = row[trueLabelString]
            predictionStr = row[predictionString]

            true_labels_in_sample = _parse_true_labels(trueLabelStr)
            
            predicted_labels_in_sample = []
            if modelTypeForParsing == 'multiclass':
                predicted_labels_in_sample = _parse_multiclass_prediction(predictionStr)
            elif modelTypeForParsing == 'generation':
                predicted_labels_in_sample = _parse_generation_prediction(predictionStr)

            true_has_label = labelToEvaluate in true_labels_in_sample
            pred_has_label = labelToEvaluate in predicted_labels_in_sample

            if true_has_label and pred_has_label: 
                current_label_TP += 1
            elif not true_has_label and pred_has_label: 
                current_label_FP += 1
            elif true_has_label and not pred_has_label: 
                current_label_FN += 1
            else: # not true_has_label and not pred_has_label
                current_label_TN += 1
            
        # Store metrics for the current label
        perLabelMetrics[labelToEvaluate] = {
        'TP': current_label_TP, 'FP': current_label_FP, 
        'TN': current_label_TN, 'FN': current_label_FN
        }
        # Accumulate current label's counts into overall counts
        TP += current_label_TP
        FP += current_label_FP
        TN += current_label_TN
        FN += current_label_FN

    return TP, FP, TN, FN, perLabelMetrics

# --- Main Evaluation Function ---
def ModelEval(df, modelType, filePath,targetMethod='binary', predictionString='predictions', trueLabelString='true_labels'):
    """
    Evaluates a model's predictions based on its type and writes the evaluation metrics to a file.
    
    Args:
        df (pd.DataFrame): The input DataFrame containing predictions and true labels.
        modelType (str): Type of model used ('generation', 'multiclass', 'binary').
        filePath (str): Path to save the model evaluation results.
        targetMethod (str): Apply either binary or multiclass evaluation logic (default: 'binary').
        predictionString (str): The name of the predictions column (default: 'predictions').
        trueLabelString (str): The name of the true labels column (default: 'true_labels').
    
    Returns:
        None
    
    Logic: (Micro-averaged for multiclass target method)
        True Positive (TP): Model correctly predicts a label that is present in true labels.
        True Negative (TN): Model correctly does not predict a label that is not in true labels.
        False Positive (FP): Model incorrectly predicts a label that is not in true labels.
        False Negative (FN): Model fails to predict a label that is present in true labels.
    """

    # Convert into lower case
    modelType = modelType.lower()
    targetMethod = targetMethod.lower()

    # Errors Checking
    validModelTypes = {"generation", "multiclass", "binary"}
    validMethodTypes = {"multiclass", "binary"}
    if modelType not in validModelTypes:
        raise ValueError(f"Model '{modelType}' type not found in valid model types {validModelTypes}.")

    if targetMethod not in validMethodTypes:
        raise ValueError(f"Evaluation method '{targetMethod}' not found in valid method types {validMethodTypes}.")

    if modelType == 'binary' and targetMethod != 'binary':
        raise ValueError(f"'{modelType}' model predictions can't be used for '{targetMethod}' evaluation.")

    # Ensure prediction & trueLabel columns exists
    missing_cols = [col for col in [predictionString, trueLabelString] if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing column(s): {missing_cols} in the DataFrame.")

    # Print Function settings
    print(f"Model type : {modelType}")
    print(f"Method type : {targetMethod}")
    print("The input DataFrame:")
    print(df.head())
    if filePath:
        print(f"Saving results to {filePath}")
    else:
        print("Results will be printed to console (no filePath provided).")


    TP = FP = TN = FN = 0 # Initialize counts
    perLabelDetails = {} # Initialize perLabelDetails dictionary

    if modelType == 'binary':
        # This case implies targetMethod must be 'binary' due to the check above.
        TP, FP, TN, FN = _evaluate_binary_model_as_binary(df, predictionString, trueLabelString)
    
    elif modelType == 'multiclass':
        if targetMethod == 'binary':
            TP, FP, TN, FN = _evaluate_multilabel_model_as_binary(df, predictionString, trueLabelString, 'multiclass')
        elif targetMethod == 'multiclass':
            TP, FP, TN, FN, perLabelDetails = _evaluate_multilabel_model_as_multiclass(df, predictionString, trueLabelString, 'multiclass')
    
    elif modelType == 'generation':
        if targetMethod == 'binary':
            TP, FP, TN, FN = _evaluate_multilabel_model_as_binary(df, predictionString, trueLabelString, 'generation')
        elif targetMethod == 'multiclass':
            TP, FP, TN, FN, perLabelDetails = _evaluate_multilabel_model_as_multiclass(df, predictionString, trueLabelString, 'generation')

    # Calculate metrics (Handle 0 Cases)
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    recall = TP / (TP + FN) if (TP + FN) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    totalPopulation = TP + TN + FP + FN
    accuracy = (TP + TN) / totalPopulation if totalPopulation > 0 else 0

    #Console output Results
    console_output_lines = [
        f"Model Type: {modelType}\n"
        f"Method Type: {targetMethod}\n"
        f"True Positives: {TP}\n"
        f"True Negatives: {TN}\n"
        f"False Positives: {FP}\n"
        f"False Negatives: {FN}\n"
        f"Total Population for Metrics: {totalPopulation}\n"
        f"Precision: {precision * 100:.2f}%\n"
        f"Recall: {recall * 100:.2f}%\n"
        f"F1 Score: {f1:.4f}\n"
        f"Accuracy: {accuracy * 100:.2f}%\n"
    ]
    console_output_string = "\n".join(console_output_lines) # Join for printing
    print("\n--- Evaluation Results ---")
    print(console_output_string)
    
    # Prepare results for file output (overall + per-label if applicable)
    file_output_lines = list(console_output_lines)

    # Store the reults of each label in the target file
    if targetMethod == 'multiclass' and perLabelDetails:
        file_output_lines.append("\nPer-Label Metrics:")
        for label, metrics in sorted(perLabelDetails.items()): # Sort for consistent output
            file_output_lines.append(f"  Label: {label}")
            file_output_lines.append(f"    TP: {metrics['TP']}, FP: {metrics['FP']}, TN: {metrics['TN']}, FN: {metrics['FN']}")
            # Optionally calculate and add per-label precision, recall, F1
            labelPrecision = metrics['TP'] / (metrics['TP'] + metrics['FP']) if (metrics['TP'] + metrics['FP']) > 0 else 0
            labelRecall = metrics['TP'] / (metrics['TP'] + metrics['FN']) if (metrics['TP'] + metrics['FN']) > 0 else 0
            labelF1 = (2 * labelPrecision * labelRecall) / (labelPrecision + labelRecall) if (labelPrecision + labelRecall) > 0 else 0
            file_output_lines.append(f"    Precision: {labelPrecision*100:.2f}%, Recall: {labelRecall*100:.2f}%, F1: {labelF1:.4f}")
    
    file_output_string = "\n".join(file_output_lines)

    if filePath:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        # Write metrics to file
        with open(filePath, 'w') as f:
            f.write(file_output_string)
        print(f"Results also saved to {filePath}")

def PlotModelResults(modelName, datasetName, resultsPath, outputPath):
    """
    Plots the evaluation results from the ModelEval function and saves the plot as an image.
    
    Args:
        modelName (str): The name of the model (ex: 'Code BERT').
        datasetName (str): The name of the dataset used (ex: 'Mega vuln').
        resultsPath (str): Path to the file containing evaluation results from ModelEval.
        outputPath (str): Directory where the plot will be saved as an image.
    
    Returns:
        None
    """
    if not os.path.exists(resultsPath):
        print(f"Error: Results file not found at {resultsPath}")
        return

    # Read results from the evaluation file
    with open(resultsPath, 'r') as file:
        results = file.readlines()

    tp = tn = fp = fn = 0

    for line in results:
        if "True Positives:" in line:
            tp = int(re.search(r"True Positives: (\d+)", line).group(1))
        elif "True Negatives:" in line:
            tn = int(re.search(r"True Negatives: (\d+)", line).group(1))
        elif "False Positives:" in line:
            fp = int(re.search(r"False Positives: (\d+)", line).group(1))
        elif "False Negatives:" in line:
            fn = int(re.search(r"False Negatives: (\d+)", line).group(1))

    labels = ['TP', 'TN', 'FP', 'FN']
    values = [tp, tn, fp, fn]
    colors = ['green', 'blue', 'red', 'orange']

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=colors)

    # Plot each category at slightly shifted positions
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f'{int(height)}',
                ha='center', va='bottom', fontsize=10)

    # Customize the plot
    ax.set_xlabel('Metric')
    ax.set_ylabel('Count')
    ax.set_title(f'Model Results for {modelName} on {datasetName}')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.set_ylim(0, max(values) * 1.2)


    # Save the plot to the specified output path
    output_file = f"{outputPath}/{modelName.replace(' ', '_')}_results_{datasetName.replace(' ', '_')}.png"
    plt.savefig(output_file)
    print(f"Results plot saved to: {output_file}")
    plt.close()

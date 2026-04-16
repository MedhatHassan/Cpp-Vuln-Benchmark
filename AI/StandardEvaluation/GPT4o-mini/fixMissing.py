import pandas as pd
import os
import re
from openai import OpenAI
import time

# ================= CONFIGURATION =================
API_KEY = "OpenAI_API_Key"
BASE_URL = "https://api.openai.com/v1"
MODEL_NAME = "gpt-4o-mini"

# Files
INPUT_DATASET     = r"data/input_dataset.csv"
LOG_FILE          = r"logs/execution.log"
FINAL_OUTPUT_CSV  = r"results/final_output.csv"
# =================================================

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def is_valid_format(text):
    """
    Returns True if text is 'secure', 'safe', or 'CWE-XXX'.
    Returns False if it is garbage, hallucination, or error code.
    """
    if not text: return False
    
    # Clean whitespace
    text = text.strip()
    
    # 1. Check for specific failure keywords
    if "Error code" in text or "Rate limit" in text or text == "ERROR":
        return False
        
    # 2. Check strict format (secure, safe, or CWE-123)
    # The regex allows "CWE-123" or "CWE-123, CWE-456"
    if re.match(r"^(secure|safe|CWE-\d{1,4}(,\s*CWE-\d{1,4})*)$", text, re.IGNORECASE):
        return True
        
    return False

def fast_load_map():
    """Reads log line-by-line into a dictionary {id: prediction}."""
    print("1. Reading Log file to map IDs...")
    data_map = {}
    
    if not os.path.exists(LOG_FILE):
        print("Error: Log file missing.")
        return {}
        
    current_id = -1
    capturing = False
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            # Fast String Matching (No heavy Regex)
            if line.startswith("--- ROW ID:"):
                try:
                    # Extract ID: "--- ROW ID: 123 ---" -> 123
                    parts = line.split()
                    if len(parts) >= 4:
                        current_id = int(parts[3])
                        capturing = False
                except:
                    current_id = -1
                continue
                
            if line.startswith("RESPONSE:"):
                capturing = True
                continue
                
            if capturing:
                # This line is the prediction
                data_map[current_id] = line.strip()
                capturing = False # Reset
                
    print(f"   Mapped {len(data_map)} rows from log.")
    return data_map

def run_repair_job():
    # 1. Load Original Data (for C code)
    print("2. Loading Original Dataset...")
    df_orig = pd.read_csv(INPUT_DATASET)
    total_rows = len(df_orig)
    
    # 2. Load Current State from Logs
    current_preds = fast_load_map()
    
    # 3. Build List of Rows to Fix
    # We check 3 conditions: Missing, Error Message, or Bad Format
    rows_to_fix = []
    
    for i in range(total_rows):
        pred = current_preds.get(i, None)
        
        # Condition A: Missing completely (The 1 missing row)
        if pred is None:
            rows_to_fix.append(i)
            continue
            
        # Condition B: Explicit API Error (The 42 errors)
        if "Error code" in pred or "Rate limit" in pred or pred == "ERROR":
            rows_to_fix.append(i)
            continue
            
        # Condition C: Bad Format / Hallucination
        if not is_valid_format(pred):
            rows_to_fix.append(i)
            continue

    print(f"3. Identified {len(rows_to_fix)} rows to repair.")
    
    # 4. Repair Loop
    if rows_to_fix:
        print("-" * 50)
        print("   STARTING REPAIR...")
        print("-" * 50)
        
        for i, idx in enumerate(rows_to_fix):
            row = df_orig.iloc[idx]
            code = row.get('Function', '')
            
            # Prepare API Message
            messages = [
                {'role': 'system', 'content': 'You are cyber security engineer and want to read C code and detect the vulnerability CWE number in the code'},
                {'role': 'user', 'content': f'Look at the following C code and print the type of the vulnerabilities and the type of CWE in this code if and only if exists, only print the number of CWE without any explanation and without writing the code again, if there is no vulnerability print secure:\n\n{code}'}
            ]
            
            prediction = "ERROR"
            
            # Retry 3 times
            for attempt in range(3):
                try:
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=messages,
                        temperature=0.0,
                        max_tokens=64,
                        timeout=30
                    )
                    prediction = response.choices[0].message.content.strip()
                    break 
                except Exception as e:
                    print(f"    Retry {idx} ({attempt+1}/3): {e}")
                    time.sleep(3)
            
            print(f"   [{i+1}/{len(rows_to_fix)}] Repaired Row {idx} -> {prediction}")
            
            # Update Map
            current_preds[idx] = prediction
            
            # Append to log to be safe
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"--- ROW ID: {idx} (REPAIR) ---\nRESPONSE:\n{prediction}\n\n")

    # 5. Final Assembly
    print("-" * 50)
    print("4. Saving Final CSV...")
    
    final_rows = []
    for i in range(total_rows):
        # Result
        p = current_preds.get(i, "ERROR_FINAL")
        
        # Original Truth
        t = df_orig.iloc[i].get('CWE', 'Unknown')
        v = df_orig.iloc[i].get('is_vul', False)
        
        final_rows.append({
            "predictions": p,
            "true_labels": t,
            "is_vul": v
        })
        
    df_final = pd.DataFrame(final_rows)
    df_final.to_csv(FINAL_OUTPUT_CSV, index=False)
    
    print(f"DONE! Saved to: {FINAL_OUTPUT_CSV}")
    print(f"Total Rows: {len(df_final)}")
    
    # Quick Check
    bad_count = df_final[df_final['predictions'] == 'ERROR_FINAL'].shape[0]
    if bad_count == 0:
        print("Status: PERFECT.")
    else:
        print(f"Warning: {bad_count} rows still failed.")

if __name__ == "__main__":
    run_repair_job()
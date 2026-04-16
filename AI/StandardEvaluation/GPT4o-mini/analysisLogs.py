import pandas as pd
import os
import re

# ================= CONFIGURATION =================
LOG_FILE     = r"logs/run.log"
RESULTS_CSV  = r"results/predictions.csv"
OUTPUT_REPORT = "error_report_summary.txt"
# =================================================

def generate_report():
    print("Scanning files... Please wait.")
    
    # 1. SETUP TRACKING
    all_log_ids = set()          # Every ID seen in the log
    ids_with_response = set()    # IDs that successfully got a "RESPONSE:"
    ids_with_error = set()       # IDs that explicitly logged an error
    
    # Store exact error messages: { 123: "Error code: 429..." }
    detailed_errors = {}
    
    # ---------------------------------------------------------
    # 2. SCAN LOG FILE
    # ---------------------------------------------------------
    if os.path.exists(LOG_FILE):
        current_id = -1
        
        # Regex patterns
        id_pattern = re.compile(r"--- ROW ID: (\d+) ---")
        response_pattern = re.compile(r"^RESPONSE:")
        
        # This captures your specific error format and others
        # It looks for "ERROR: Error code" OR just "Error code" OR "Rate limit"
        error_pattern = re.compile(r"(ERROR: Error code.*|Error code:.*|.*Rate limit.*|.*model_not_found.*)") 

        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # A. Detect New Row ID
                id_match = id_pattern.search(line)
                if id_match:
                    current_id = int(id_match.group(1))
                    all_log_ids.add(current_id)
                    continue

                # B. Detect Response
                if current_id != -1:
                    if response_pattern.search(line):
                        ids_with_response.add(current_id)
                        continue

                    # C. Detect Errors
                    if error_pattern.search(line):
                        ids_with_error.add(current_id)
                        # Clean the message
                        clean_msg = line.replace("ERROR:", "").strip()
                        detailed_errors[current_id] = clean_msg
    else:
        print(f"Error: Log file not found at {LOG_FILE}")
        return

    # ---------------------------------------------------------
    # 3. ANALYZE GAPS
    # ---------------------------------------------------------
    
    # A. Completely Missing from Logs (Gaps in sequence)
    missing_from_log = []
    if all_log_ids:
        min_id = min(all_log_ids)
        max_id = max(all_log_ids)
        full_range = set(range(min_id, max_id + 1))
        missing_from_log = sorted(list(full_range - all_log_ids))

    # B. In Log, but NO Response and NO Error (The "Zombie" Rows)
    # These are likely the ones missing from the CSV
    zombie_rows = sorted(list(all_log_ids - ids_with_response - ids_with_error))

    # ---------------------------------------------------------
    # 4. SCAN CSV (For explicit "ERROR" text)
    # ---------------------------------------------------------
    csv_error_count = 0
    csv_total_rows = 0
    if os.path.exists(RESULTS_CSV):
        try:
            df = pd.read_csv(RESULTS_CSV)
            csv_total_rows = len(df)
            # Check for "ERROR" in predictions
            error_rows = df[df['predictions'].astype(str).str.contains("ERROR", case=False, na=False)]
            csv_error_count = len(error_rows)
        except Exception as e:
            print(f"CSV Error: {e}")

    # ---------------------------------------------------------
    # 5. WRITE REPORT
    # ---------------------------------------------------------
    total_issues = len(missing_from_log) + len(zombie_rows) + len(detailed_errors)

    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write("==================================================\n")
        f.write("             DETAILED ERROR REPORT                \n")
        f.write("==================================================\n\n")
        
        f.write(f"Log File: {os.path.basename(LOG_FILE)}\n")
        f.write(f"CSV File: {os.path.basename(RESULTS_CSV)}\n")
        f.write(f"CSV Row Count: {csv_total_rows}\n")
        f.write(f"Log ID Count:  {len(all_log_ids)}\n")
        f.write(f"Discrepancy:   {len(all_log_ids) - csv_total_rows} rows difference\n\n")

        # --- SECTION 1: IN LOGS BUT NO RESPONSE (THE MISSING CSV ROWS) ---
        f.write("--------------------------------------------------\n")
        f.write(f" 1. INCOMPLETE LOGS (No Response Recorded) - Count: {len(zombie_rows)}\n")
        f.write("    (These are likely the rows missing from your CSV)\n")
        f.write("--------------------------------------------------\n")
        if zombie_rows:
            f.write("Row IDs:\n")
            f.write(", ".join(map(str, zombie_rows)))
        else:
            f.write("None. All logged rows have a response or an error.")
        f.write("\n\n")

        # --- SECTION 2: API ERRORS ---
        f.write("--------------------------------------------------\n")
        f.write(f" 2. API ERRORS (Rate Limit / 403 / Etc) - Count: {len(detailed_errors)}\n")
        f.write("--------------------------------------------------\n")
        if detailed_errors:
            f.write(f"{'Row ID':<10} | {'Error Message'}\n")
            f.write("-" * 80 + "\n")
            for r_id in sorted(detailed_errors.keys()):
                msg = detailed_errors[r_id]
                f.write(f"{r_id:<10} | {msg}\n")
        else:
            f.write("No explicit API errors found.\n")
        f.write("\n")

        # --- SECTION 3: MISSING FROM LOGS ---
        f.write("--------------------------------------------------\n")
        f.write(f" 3. COMPLETELY MISSING IDs (Gaps) - Count: {len(missing_from_log)}\n")
        f.write("--------------------------------------------------\n")
        if missing_from_log:
            f.write(", ".join(map(str, missing_from_log)))
        else:
            f.write("No gaps found in ID sequence.")
        f.write("\n\n")

        # --- SECTION 4: CSV ERRORS ---
        f.write("--------------------------------------------------\n")
        f.write(f" 4. CSV CONTENT ERRORS\n")
        f.write("--------------------------------------------------\n")
        f.write(f"Rows containing 'ERROR' text in CSV: {csv_error_count}\n")
    
    print("-" * 50)
    print("DONE!")
    print(f"Report saved to: {OUTPUT_REPORT}")
    print(f"Found {len(zombie_rows)} rows with No Response (The missing ones).")
    print(f"Found {len(detailed_errors)} rows with API Errors.")
    print("-" * 50)

if __name__ == "__main__":
    generate_report()
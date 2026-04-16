import re
import os

# ================= CONFIGURATION =================
# Update this to your actual log file path
INPUT_FILE = r"./gpt-4o-mini_full_logs.txt"
OUTPUT_FILE = "AI summary.txt"
# =================================================

def clean_log_file():
    print(f"Reading from: {INPUT_FILE}")
    
    if not os.path.exists(INPUT_FILE):
        print("Error: Input file not found. Please check the path.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # ================= REGEX EXPLANATION =================
    # PROMPT:       -> Finds the literal text "PROMPT:"
    # [\s\S]*?      -> Matches ALL characters (including new lines) in between, non-greedy
    # (?=RESPONSE:) -> Lookahead: Stops right before it hits "RESPONSE:"
    # =====================================================
    pattern = re.compile(r"PROMPT:[\s\S]*?(?=RESPONSE:)", re.MULTILINE)

    # Replace the matched PROMPT section with an empty string
    cleaned_content = re.sub(pattern, "", content)

    # Save to the new file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print("-" * 50)
    print("SUCCESS!")
    print(f"Cleaned logs saved to: {OUTPUT_FILE}")
    print("-" * 50)

if __name__ == "__main__":
    clean_log_file()
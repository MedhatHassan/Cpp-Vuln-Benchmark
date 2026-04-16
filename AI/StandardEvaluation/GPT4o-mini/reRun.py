import pandas as pd
from openai import OpenAI

# ========= CONFIG =========
API_KEY = "OpenAI_API_Key"
MODEL_NAME = "gpt-4o-mini"

INPUT_FILE = r"./MegaVuln_standard_evaluation.csv"
OUTPUT_FILE = r"./fix_19723_result.csv"
ROW_ID = 19723
# ==========================

client = OpenAI(api_key=API_KEY)

# Load dataset
df = pd.read_csv(INPUT_FILE)

row = df.iloc[ROW_ID]
code = row["Function"]
true_label = row["CWE"]
is_vul = row["is_vul"]

# Strict prompt
messages = [
            {'role': 'system', 'content': 'You are cyber security engineer and want to read C code and detect the vulnerability CWE number in the code'},
            {'role': 'user', 'content': f'Look at the following C code and print the type of the vulnerabilities and the type of CWE in this code if and only if exists, only print the number of CWE without any explanation and without writing the code again, if there is no vulnerability print secure:\n\n{code}'}
        ]

response = client.chat.completions.create(
    model=MODEL_NAME,
    messages=messages,
    temperature=1.0,
    max_tokens=10
)

prediction = response.choices[0].message.content.strip()

# Save result
out = pd.DataFrame([{
    "row_id": ROW_ID,
    "predictions": prediction,
    "true_labels": true_label,
    "is_vul": is_vul
}])

out.to_csv(OUTPUT_FILE, index=False)

print("Saved result to:", OUTPUT_FILE)
print(out)

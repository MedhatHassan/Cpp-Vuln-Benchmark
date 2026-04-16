# 🧠 LLM Standard Evaluation Benchmark

This directory contains the core experimental data, API execution scripts, and performance telemetry for the Large Language Model (LLM) phase of our research. 

To evaluate the true efficacy of generative AI in vulnerability detection, we benchmarked five state-of-the-art models: **DeepSeek v3.2, Gemma 2, Llama 3.2, Qwen, and GPT-4o mini**. The evaluations were conducted on a real-world C/C++ dataset using zero-shot prompting, focusing on both **Binary** (Vulnerable vs. Safe) and **Multiclass** (Specific CWE Identification) classification.

## 🗂️ Directory Structure & Artifacts

Each sub-directory corresponds to a specific LLM and contains the necessary artifacts to reproduce or analyze our findings:

*   **Raw Output Data:** `.csv` files containing the side-by-side ground truth (`true_labels`) vs. the raw generative text output (`predictions`) from the LLMs. *(Note: Gemma 2 data is compressed via `.rar` due to GitHub file size limits).*
*   **Execution Scripts:** Python scripts used to interact with model APIs (e.g., `openAIRun.py`, `deepseekRun.py`), including fault-tolerance logic for handling API drops (`reRun.py`, `fixMissing.py`, `LogSummary.py`).
*   **Evaluation Notebooks:** Jupyter notebooks (`eval.ipynb`) utilizing our custom `AIeval.py` framework to parse generative text, extract CWE arrays, and compute confusion matrices.
*   **Telemetry Reports:** Standardized text files (`_binary.txt`, `_multiclass.txt`) containing the exact True Positive, False Positive, and Precision/Recall metrics.

---

## 📊 Empirical Findings: The "Reasoning Gap"

Our evaluation exposed a critical vulnerability in how open-weight LLMs process code security. While models like DeepSeek v3.2 and Gemma 2 achieve phenomenal **Binary Recall (>88%)**, they do so via extreme over-prediction, resulting in a **False Positive Rate exceeding 87%**. 

When tasked with specific **Multiclass CWE identification**, these models collapse entirely (F1 scores drop below 0.1), revealing a severe lack of semantic deductive reasoning. We define this phenomenon as **The Reasoning Gap**.

### 1. Multiclass Results (Micro-Averaging)
*Evaluates the model's ability to accurately pinpoint the specific Common Weakness Enumeration (CWE) identifier.*

| Model   | Type       | True Positives | False Positives | False Negatives | Precision | Recall | F1 Score | 
|---------|-----------|---------------|---------------|---------------|-----------|--------|---------|
| **GPT-4o mini**  | Generation | 21,872          | 13,524        | 13,515        | 61.79%     | 61.81% | **0.6180**  |
| **Qwen**    | Generation | 19,372            | 21,195        | 16,015        | 47.75%     | 54.74%  | **0.5101**  |
| **DeepSeek v3.2**  | Generation | 3,483          | 32,054        | 31,904        | 9.80%     | 9.84% | 0.0982  |
| **Llama 3.2** | Generation | 5,094        |  66,897        | 30,293        | 7.08%    | 14.40% | 0.0949  |
| **Gemma 2**  | Generation | 128          | 72,013        | 35,259        | 0.18%     | 0.36% | 0.0024  |

> *NOTE: True Negatives (TN) & Accuracy are excluded in the **micro-averaging** evaluation methodology, as they heavily skew performance metrics in highly imbalanced, multi-label datasets.*

### 2. Binary Results
*Evaluates the model's ability to classify a code snippet broadly as "Vulnerable" or "Safe".*

| Model   | True Positives | True Negatives | False Positives | False Negatives | Precision | Recall  | F1 Score | Accuracy |
|---------|---------------|---------------|----------------|----------------|-----------|--------|---------|----------|
| **DeepSeek v3.2**    | 6,784          | 2,788         | 25,584           | 231           | 20.96%    | **96.71%** | **0.3445**  | 27.05%   |
| **GPT-4o mini**    | 2,780          | 21,660         | 6,712 | 4,235           | **29.29%**    | 39.63% | 0.3368  | **69.06%**   |
| **Gemma 2** | 6,186          | 3,509          | 24,863          | 829            | 19.92%    | 88.18% | 0.3250  | 27.40%   |
| **Llama 3.2** | 5,876          | 4,787          | 23,585          | 1,139           | 19.95%    | 83.76% | 0.3222  | 30.13%   |
| **Qwen**    | 2,230          | 19,362         | 9,010           | 4,785           | 19.84%    | 31.79% | 0.2443  | 61.02%   |

---

## 📈 Visualizing the Alert Fatigue

The charts below visualize the raw confusion matrix counts across all evaluated models. The massive red spikes in False Positives (particularly for DeepSeek, Gemma, and Llama) visually demonstrate the "Alert Fatigue" that renders raw, un-tuned LLMs currently unsuitable as hard, automated CI/CD gating mechanisms.

### Confusion Matrix Distribution by Model
![TP, TN, FP, FN Comparison](./True%20Positives,%20True%20Negatives,%20False%20Positives,%20False%20Negatives%20by%20Model.png)

### Model Accuracy & F1-Score Stability
![Accuracy vs F1 Score](./Accuracy%20and%20F1%20Score%20by%20Model.png)
# SAST modules
## 🔍 Automated SAST Benchmarking ([SATeval.py](SATeval.py))

Evaluating query-based SAST tools across massive datasets requires immense computational overhead. To facilitate the benchmarking of Graph-based static analysis, we engineered `SATeval.py`. 

This module acts as a high-performance wrapper for **Joern** (Code Property Graph scanner). It automates query execution via thread-pooling, parses output logs, and dynamically computes confusion matrix telemetry for binary vulnerability classification.

### Core Features
*   **Multithreaded Graph Scanning:** Drastically reduces execution time by dispatching `joern-scan` instances concurrently using `ThreadPoolExecutor`, bound by dynamic CPU availability.
*   **Automated Telemetry Computation:** Automatically parses Joern console outputs to extract `Result:` markers. It maps these findings against the dataset's ground-truth directory structure to calculate TP, FP, TN, FN, Precision, Recall, and F1-Scores.
*   **Time-out Protection:** Implements 300-second strict timeouts per scan to prevent hanging processes when generating overly complex CPGs on large source files.

### Directory Structure Requirement
To compute ground-truth metrics, `SATeval.py` requires datasets to be cleanly segregated into vulnerable (`True`) and safe (`False`) subdirectories:

```text
datasets/
 └── CWE-617/
      ├── True/   # Contains vulnerable source code
      └── False/  # Contains patched/safe source code
```

### Usage Example
Configure your queries and target directories in the `__main__` block of `SATeval.py`, then run:

```bash
# Ensure Joern is installed and accessible in your environment
python3 SATeval.py
```

**Example Console Output:**

```text
----- Processing CWE-617 -----
Using up to 8 threads for Joern scans.
Submitted 400 scan tasks to the thread pool.
...
Evaluation Score:
True Positives (TP): 185
False Negatives (FN): 15
False Positives (FP): 12
True Negatives (TN): 188
Precision: 93.91%
Recall: 92.50%
Accuracy: 93.25%
F1-Score: 0.93

Results saved to ./output_evaluations/CWE-617/CWE-617-Score-Results.txt
Total execution time: 42.1500 seconds
```
# ⚙️ SAST Standard Evaluation: Joern Default Queries Benchmark

This directory contains the telemetry, evaluation plots, and exact C/C++ source code subsets used for our baseline evaluation of **Joern** (a Graph-based, Query-SAST tool). 

The primary objective of this evaluation was to determine the true efficacy of Joern's default C/C++ queries when applied to real-world code structures derived from the **MegaVuln** dataset.

## 🧪 Methodology & Dataset Configuration
To ensure metric fidelity and prevent class imbalance skewing the Accuracy scores, this evaluation was conducted under strict parameters:
*   **Dataset Balancing:** All evaluated datasets maintain a strict **50% / 50% (Vulnerable / Safe)** ratio.
*   **Scale:** The evaluation was tested across **7,104** C/C++ code snippets.
*   **Query Scope:** We utilized **13** specific Joern queries mapped to **6** distinct CWEs.
*   **Disqualification Threshold:** Any default Joern query that yielded less than **1 True Positive (TP)** was disqualified from the final standard results to filter out deprecated or non-functional queries.
*   **Manual Verification:** The "Standard Results" presented below reflect the metrics *after* a rigorous manual review of all vulnerable data in the subset.

## 🗂️ Directory Structure & Artifacts

We have open-sourced the exact C/C++ ground-truth code used to generate these metrics to guarantee 100% reproducibility.

```text
.
├── CWE-*/                            <- Individual folders containing raw telemetry (Precision, Recall, F1) for each CWE.
├── Balanced_MegaVuln_Subset_Code.zip <- The exact C/C++ source code files (True/False labeled) used for this evaluation.
├── SurveyDefualtQuriesResults.txt    <- Aggregated text report of the default query survey.
└── *.png                             <- Visual plots detailing Accuracy, F1-Scores, and Confusion Matrices across CWE-IDs.
```

#### The default queries mapping
```
joern_c_query_filtered = {
    'signed-left-shift': 'CWE-190',
    'strlen-truncation': 'CWE-190',
    'malloc-memcpy-int-overflow': 'CWE-190',
    'socket-send': 'CWE-252',
    'unchecked-read-recv-malloc': 'CWE-252',
    'format-controlled-printf': 'CWE-134',
    'call-to-strcpy': 'CWE-120',
    'call-to-gets': 'CWE-120',
    'copy-loop': 'CWE-120',
    'call-to-scanf': 'CWE-120',
    'call-to-strcat': 'CWE-119',
    'call-to-strtok': 'CWE-119',
    'strncpy-no-null-term': 'CWE-119'
}
```

#### Standard Results
| CWE ID   | Total Files | TP  | FN   | FP  | TN   | Precision | Recall | Accuracy |
|----------|------------|-----|------|-----|------|-----------|--------|----------|
| CWE-119  | 3440       | 1   | 1719 | 2   | 1718 | 33.33%    | 0.06%  | 49.97%   |
| CWE-120  | 884        | 64  | 378  | 22  | 420  | 74.42%    | 14.48% | 54.75%   |
| CWE-134  | 60         | 2   | 28   | 0   | 30   | 100.00%   | 6.67%  | 53.33%   |
| CWE-190  | 1526       | 39  | 724  | 14  | 749  | 73.58%    | 5.11%  | 51.64%   |
| CWE-362  | 1110       | 4   | 551  | 0   | 555  | 100.00%   | 0.72%  | 50.36%   |
| CWE-252  | 84         | 1   | 41   | 1   | 41   | 50.00%    | 2.38%  | 50.00%   |
| CWE-119 & CWE-120 | 4324 | 290 | 1872 | 83  | 2079 | 77.75% | 13.41% | 54.79% |

### TP, TN, FP, FN
![Accuracy](<./Mega Vuln Default Query Standard Analysis  TP-FP-TN-FN.png>)
### Accuracy
![alt text](<./Mega Vuln Default Query Standard Analysis - Accuracy per CWE.png>)

*"Note: These charts visualize the finalized, highly accurate metrics after rigorous manual review and the disqualification of non-functional queries."*
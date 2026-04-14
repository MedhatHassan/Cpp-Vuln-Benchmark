# AI Custom modules
## ⚙️ Automated AI Evaluation Framework ([AIeval](AIeval.py))

To ensure rigorous, reproducible, and standardized evaluation across diverse architectures (Generative LLMs, Multiclass Classifiers, and Binary models), we engineered a custom Python evaluation module: `AIeval.py`. 

This module automates data sanitization, handles complex CWE multi-label mappings, and generates deterministic performance telemetry.

### Core Functionalities

#### 1. `RemoveComments(df, targetColumn)`: Data Sanitization
LLMs can suffer from "shortcut learning" or data leakage if source code comments contain hints about vulnerabilities. This function deterministically strips both single-line (`//`, `#`) and multi-line (`/* ... */`) comments while preserving the exact structural integrity of the AST/code block.
#### Usage
```python
import pandas as pd
from AIeval import RemoveComments

# Load raw source code dataset
df = pd.DataFrame({'source_code': ["/* Vulnerable buffer */ int x = 10; \nint y = 20; // init"]})

# Sanitize dataset prior to model inference
RemoveComments(df, targetColumn='source_code')
```

#### 2. `ModelEval()`: Standardized Telemetry Generation
Evaluates model predictions dynamically based on the model's architecture (`binary`, `multiclass`, or `generation`). It calculates True Positives (TP), True Negatives (TN), False Positives (FP), False Negatives (FN), Precision, Recall, Accuracy, and F1-Scores (utilizing micro-averaging for complex multiclass/CWE evaluations).

**Special Label Handling:**
*   **Generative Parsing:** Utilizes regex to extract `CWE-ID` arrays from unstructured LLM text outputs.
*   **Multi-Label Tolerance:** If a ground-truth label contains multiple CWEs (e.g., `CWE-459, CWE-787`), a model is penalized only if it fails to detect *any* of the correct mappings.

#### Usage
```python
from AIeval import ModelEval

# Evaluate an LLM's generative predictions against ground-truth CWEs
ModelEval(
    df=prediction_dataframe, 
    modelType='generation', 
    targetMethod='multiclass', 
    filePath='./results/Model-X_evaluation.txt',
    predictionString='llm_output', 
    trueLabelString='ground_truth'
)
```

#### 3. `PlotModelResults()`: Automated Visualization
Parses the text-based telemetry outputs from `ModelEval` and automatically generates publication-ready bar charts mapping the confusion matrix for visual benchmarking.

#### Usage
```python
from AIeval import PlotModelResults

# Generate visual benchmark charts
PlotModelResults(
    modelName='Model-X', 
    datasetName='Benchmark-Dataset-Y', 
    resultsPath='./results/Model-X_evaluation.txt', 
    outputPath='./results/plots/'
)
```

### Complete Evaluation Pipeline Example
```python
import pandas as pd
from AIeval import RemoveComments, ModelEval, PlotModelResults

# 1. Load inference data
df = pd.read_csv("model_inference_results.csv")

# 2. Evaluate performance and extract metrics
ModelEval(df, modelType='multiclass', filePath='eval_telemetry.txt')

# 3. Generate publication-ready visualizations
PlotModelResults('Model-X', 'Dataset-Y', 'eval_telemetry.txt', './output_plots/')
```

## LLM Runner Framework for Code Vulnerability Detection ([LLM_runner](LLM_runner.py))


This framework provides an automated pipeline to evaluate Large Language Models (LLMs) on C/C++ code vulnerability detection tasks using Hugging Face transformers.

### Core Functionalities

#### `LMM_runner(df, dataset_name, code_field, target_field='is_vul', class_field, model_name, model_path, max_new_tokens)`: LLM runner

This function supports running Hugging Face LLMs either directly from the Hugging Face Hub or from locally saved model directories.

#### Usage
```python
import torch
import pandas as pd
import numpy as np
import time
from transformers import pipeline
import psutil
from AIeval import RemoveComments

# Load raw source code dataset
df = pd.DataFrame({
    "source_code": ['inline template_t load(const std::string& filename)\n        {\n            return compile(detail::get_loader_ref()(filename));\n        }'],

    "cwe_type": ['CWE-22'],
    
    'is_vul': [1]
})

result_df = LLM_runner(
    df=df,
    dataset_name="code_vulnerability_df",
    code_field="source_code",
    target_field="is_vul",
    class_field="cwe_type",
    model_name="LLM_name",
    model_path="HuggingFace_hub_path or local_path",
    max_new_tokens=256
)
```
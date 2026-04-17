import torch
import pandas as pd
import numpy as np
import time
from transformers import pipeline
import psutil
from AIeval import RemoveComments


def LLM_runner(df, dataset_name=None, code_field='Function', target_field='is_vul', class_field='CWE',
               model_name='Llama', model_path='meta-llama/Llama-3.2-1B-Instruct', max_new_tokens=256):
    """
    Evaluate the LLM model using the given dataframe
    
    parameters
    -----------
    df: pandas.core.frame.DataFrame, dataframe of input code and output true labels to evaluate the model performance
    dataset_name: str, Name of the dataset file
    code_field: str, the column name in df which contains input C/C++ code
    target_field: str, the column name in df which contains the true label (0 or 1)
    class_field: str, the column name in df which contains the name of the class (CWE number)
    model_path: str, path of the model in local directory or huggingface hub
    max_new_tokens: int, number of the output tokens that the model will generate
    
    returns:
    --------
    Dataframe with 3 columns of true labels, true CWE classes and model's output generation
    """
        
    RemoveComments(df, code_field) # remove comments from each the code
    
    codes = df[code_field].tolist()
    target_labels = df[target_field].tolist()
    target_classes = df[class_field].tolist()
    
    model_input = [
        [
        {'role': 'system', 'content': 'You are cyber security engineer and want to read C code and detect the vulnerability CWE number in the code'},
        {'role': 'user', 'content': f'Look at the following C code and print the type of the vulnerabilities and the type of CWE in this code if and only if exists, only print the number of CWE without any explanation and without writing the code again, if there is no vulnerability print secure:\n\n{code}'}
        ] for code in codes
    ]
    
    pipe = pipeline(
        "text-generation",
        model=model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    outputs = []
    cpu_usage, ram_usage = [], []
    
    start_time = time.time()
    for formatted_input in model_input:
        output = pipe(formatted_input, max_new_tokens=max_new_tokens)
        outputs.append(output[0]['generated_text'][-1]['content'])
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_time = elapsed_time / len(formatted_input)
    
    cpu_usage.append(psutil.cpu_percent(2))
    ram_usage.append(psutil.virtual_memory()[3]/1000000000)
    mean_cpu = np.mean(cpu_usage)
    mean_ram = np.mean(ram_usage)
    print(f'Elapsed time: {elapsed_time}\nMean cpu usage: {mean_cpu}\nMean ram usage: {mean_ram}')
    di = {
        'true_labels': target_labels,
        'true_classes': target_classes,
        'predictions': outputs
    }
    result_df = pd.DataFrame(di)
    result_df.to_csv(f'{model_name}__{dataset_name}_true_labels_vs_predictions.csv', index=False)
    
    return result_df
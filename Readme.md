# 🛡️ Cpp-Vuln-Benchmark: The Reasoning Gap in Automated Vulnerability Detection
<div align="center">

[![Published in](https://img.shields.io/badge/Published_in-IEEE_Xplore-00629B.svg?logo=ieee&logoColor=white)](#)
[![Indexed by](https://img.shields.io/badge/Indexed_by-Scopus-E9711C.svg)](#)
[![Conference](https://img.shields.io/badge/Accepted-IEEE_3SCEA_2026-blue)](https://ufe.edu.eg/3scea2026/)
[![Target](https://img.shields.io/badge/Target_Code-C%2FC%2B%2B-00599C.svg?logo=c%2B%2B&logoColor=white)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Domain](https://img.shields.io/badge/Domain-Cybersecurity%20%7C%20AppSec-red.svg)](#)
[![Focus](https://img.shields.io/badge/Focus-LLM%20Evaluation%20%7C%20Static%20Analysis-8A2BE2.svg)](#)
[![Scripts](https://img.shields.io/badge/Eval_Scripts-Python_3.x-3776AB.svg?logo=python&logoColor=white)](#)

</div>

> Official repository for the paper: **"The Reasoning Gap in Automated Vulnerability Detection: A Comprehensive Benchmark of LLMs, SAST, DAST, and Graph-based Approaches"** accepted at the IEEE 3SCEA2026 Conference. Published in the **IEEE Xplore® Digital Library** and indexed by **Scopus**.

## 📖 Overview
Security vulnerabilities in modern software ecosystems continually outpace traditional remediation strategies. While this benchmark utilizes C/C++ as **the ultimate architectural stress test** chosen for its extreme complexity, direct memory access, and the highest volume of mapped CWEs—the fundamental paradigms, graph representations, and AI evaluation frameworks established here are entirely **language-agnostic**.

Representing months of rigorous empirical testing and synthesizing insights from **over 50 state-of-the-art academic papers**, this repository serves as a definitive meta-analysis. It formally bridges the gap between legacy Application Security Testing (AST) and emerging AI-driven paradigms.

### 🌟 Peer Review & Academic Recognition
This research was rigorously peer-reviewed and accepted at the IEEE 3SCEA 2026 Conference. The review committee highlighted the work as a benchmark-setting study:

> *"This is a high-quality, impactful paper that sets **a new standard** for benchmarking automated vulnerability detection techniques. The analysis is rigorous, the conclusions are well-supported, and the identification of the 'Reasoning Gap' is both novel and timely." — IEEE Review Committee*

### 🚀 Main Contributions
1. **The Reasoning Gap:** We evaluate state-of-the-art LLMs (including GPT-4o mini) across binary and multiclass tasks, uncovering a *“Reasoning Gap”* where open-weight models struggle with precision despite high recall.
2. **Comprehensive Methodology Review:** We analyze the efficacy of AI-Driven, Graph-based, and AST approaches for C/C++ vulnerability detection.
3. **Dataset Integrity:** We quantified significant data duplication between standard benchmarks, revealing that 62% of BigVul’s unique hashes exist within MegaVul, leading to severe data leakage in AI model training.
4. **Graph-Based Superiority:** We demonstrate that graphbased methods consistently outperform sequence-based approaches, providing deeper semantic insights for vulnerability detection.
5. **Roadmap for Future Research:** We identify systematic limitations in current methodologies and outline specific development areas to drive continuous improvement in automated detection.

## 🗂️ Repository Structure (Example)
*Note: Adjust these folders based on your actual repository setup.*
- `/llm_eval/` - Scripts and zero-shot prompts used to benchmark Qwen, Llama 3.2, Gemma 2, DeepSeek, and GPT-4o mini.
- `/sast_queries/` - Custom and default CodeQL queries used for the real-world dataset evaluation.
- `/dataset_analysis/` - Scripts used to identify the hash overlaps and duplication between MegaVul and BigVul.
- `/results/` - Raw CSV outputs, F1 score calculations, and Signal-to-Noise chart generation data.

## 📊 Evaluation Data Highlights
| Model | Binary Recall | False Positive Rate | Multiclass F1 |
|-------|--------------|---------------------|---------------|
| **DeepSeek v3.2** | 96.71% | > 90.0% | 0.0982 |
| **Gemma 2** | 88.18% | > 87.0% | 0.0024 |
| **GPT-4o mini** | 39.63% | 23.6% | **0.6180** |

## 📝 Citation
This paper is officially published in **IEEE Xplore** and indexed in **Scopus**. If you use this benchmark, code, or our dataset analysis in your research, please cite our paper:

**IEEE Xplore Link:** `[Link will be updated upon publication]`  
**DOI:** `[Pending]`

```bibtex
@inproceedings{ali2026reasoning,
  title={The Reasoning Gap in Automated Vulnerability Detection: A Comprehensive Benchmark of LLMs, SAST, DAST, and Graph-based Approaches},
  author={Ali, Medhat Hassan and Sakr, Youssef and Eissa, Abdullah and Aljazairy, Mohammed and Rashad, Hisham Salah},
  booktitle={2026 3rd International Conference on Smart Computing and Electronic Applications (IEEE 3SCEA)},
  year={2026},
  organization={IEEE}
}
```
## 📬 Contact the Authors
This research was conducted by the Computer Engineering Department at the Arab Academy for Science and Technology (AAST), Cairo, Egypt.
Feel free to reach out to the authors for questions, collaborations, or access to extended datasets:
### Medhat Hassan Ali (Lead Author / Offensive Security Engineer)
📧 Email: Eng.MedhatHassanAli@gmail.com | 💼 LinkedIn: [in/medhat-hassan](https://www.linkedin.com/in/medhat-hassan) | 🐙 GitHub: @MedhatHassan
### Youssef Sakr (Co-Author / Offensive Security Engineer)
📧 Email: Eng.Youssef.Sakr@gmail.com | 💼 LinkedIn: [/in/youssef-sakr](https://www.linkedin.com/in/youssef-sakr/) | 🐙 GitHub: @sakr00 
### Abdullah Eissa (Co-Author / AI Engineer)
📧 Email: abdullaheissa588@gmail.com | 💼 LinkedIn: [in/abdullah-eissa-623648245](https://www.linkedin.com/in/abdullah-eissa-623648245/) |🐙 GitHub: @Abdullah-Eissa
### Mohammed Aljazairy (Co-Author / Software Engineer)
📧 Email: mohammedaljazairy@icloud.com | 💼 LinkedIn: [in/mohammed-aljazairy-870167309](https://www.linkedin.com/in/mohammed-aljazairy-870167309/) |🐙 GitHub: @MohammedAljazairy
### Dr. Hisham Salah Rashad (Academic Supervisor)
📧 Email: hishamsalah@aast.edu

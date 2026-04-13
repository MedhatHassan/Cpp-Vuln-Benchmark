# Datasets 
## List of all conducted Datasets
### Artificial code dataset
- juliet
### Real-world code Datasets
- Megavuln
- Bigvuln
- Reveal
- Devign
- D2A
- CDG
- CVEfix
  
## [Compare Datasets](compareDatasets.ipynb)
### MegaVuln & Bigvuln
The raw counts (**353,873** in `MegaVuln` vs. **9,288 unique commit hash values**, and **188,636** in `BigVuln` vs. **4,058 unique commit hash values**) show that duplicates dominate the data. These duplicates artificially inflate the dataset size but do not affect the unique intersection count once deduplication is applied.
*All the intersected indices of **MegaVuln** and **BigVuln** can be stored in a file directly from the code*

#### Overlap Between Rows Based on Hashes:
Number of intersected rows **Vulnerable functions only** (`func_before`) based on commit hash: **4190**
Total intersected indices in MegaVuln: **4471**
Total intersected indices in BigVuln: **4424**

#### Overlap Between Unique Hashes:
After removing duplicates, `MegaVuln` has **9,288** unique hashes, and `BigVuln` has **4,058**.
The intersection count of **2,513** suggests that not all hashes are shared between the datasets. In fact:
2,513 / 4,058 ≈ **62%** of `BigVuln`'s unique hashes are found in `MegaVuln`.
2,513 / 9,288 ≈ **27%** of `MegaVuln`'s unique hashes are found in `BigVuln`.
2,513 / 2,391 ≈ **95%** of intersected unique hashes are **Vulnurable**.


|Features                     | MegaVul(C/CPP) | Big-Vul        |
|-----------------------------|----------------|----------------|
| Number of Repositories      | 1062           | 310            |
| Number of CVE IDs           | 8476           | 3539           |
| Number of CWE IDs           | 176            | 92             |
| Number of Commits           | 9288           | 4058           |
| Number of Vul/Non-Vul Function | 17975/335898   | 10900/177736   |
| Success Rate of Graph Generation | 87%            | None           |

## Resources 
#### [Juliet v1.3](https://samate.nist.gov/SARD/test-suites/112)
#### [Megavuln](https://github.com/Icyrockton/MegaVul)
#### [Bigvuln](https://github.com/ZeoVanMSR_20_Code_vulnerability_CSV_Dataset)
#### [Reveal](https://github.com/VulDetProject/ReVeal)
#### [Devign](https://sites.google.com/view/devign)
#### [D2A](https://developer.ibm.com/exchanges/data/all/d2a/)
#### [CDG](https://github.com/CGCL-codes/VulDeePecker/tree/master)
#### [CVEfix](https://github.com/secureIT-project/CVEfixes)
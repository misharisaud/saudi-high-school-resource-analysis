# Saudi High-School Resource Allocation and Staffing Analysis

## Overview

This repository contains the data, reproducible analysis code, outputs, and manuscript files supporting the study:

**Resource Allocation and Staffing Ratios Across School Types in Saudi Arabia's High School Education System: A National and Regional Descriptive Analysis**

The study examines Saudi Arabia's 2024 high-school education statistics across the 13 administrative regions and compares government, private, and international school provision. It focuses on school scale, enrolment, staffing, and three derived indicators:

- Students per school
- Students per teacher
- Students per administrator

A key methodological feature of this version is that comparisons between publicly funded and fee-paying provision are performed **after aggregation to matched regional units**, rather than treating lower-level administrative cells as independent observations.

## Study Design

The source workbook contains aggregated General Education Statistics from the Saudi Ministry of Education. After excluding Royal Commission records, the analysis focuses on the high-school subset.

The high-school dataset contains:

- **5,356 schools**
- **1,451,903 students**
- **120,330 teachers**
- **14,175 administrators**
- **192 aggregated high-school administrative cells**
- **13 administrative regions**

School sectors are analyzed as:

- Government
- Private
- International

For the financing-model comparison, sectors are grouped operationally as:

- **Publicly funded:** Government schools
- **Fee-paying:** Private + International schools

This grouping is institutional and does **not** represent a direct measure of tuition, affordability, expenditure, or household cost.

## Core Methodological Correction in Version 3

Earlier cell-level independent tests were removed. The revised analysis follows four steps:

1. Classify each high-school administrative cell as publicly funded or fee-paying.
2. Aggregate records within each of the 13 regions and funding groups, summing across gender and education administrations.
3. Calculate students-per-school, students-per-teacher, and students-per-administrator ratios **after aggregation**.
4. Compare public and fee-paying values as **paired regional observations**.

The paired analysis reports:

- Paired-samples t-tests
- 95% confidence intervals for the mean paired difference
- Cohen's *d*<sub>z</sub>
- Two-sided Wilcoxon signed-rank sensitivity tests
- Shapiro-Wilk diagnostics on paired differences

Students-per-school and students-per-teacher comparisons include all 13 regions. Students-per-administrator includes 12 regions because the fee-paying administrator total for Al Bahah is zero, making that ratio undefined.

## Main Results

### National sector profile

| Indicator | Government | Private | International |
|---|---:|---:|---:|
| Schools | 4,003 | 813 | 540 |
| Students | 1,209,480 | 182,580 | 59,843 |
| Teachers | 104,550 | 11,715 | 4,065 |
| Administrators | 12,684 | 831 | 660 |
| Students per school | 302.14 | 224.58 | 110.82 |
| Students per teacher | 11.57 | 15.59 | 14.72 |
| Students per administrator | 95.35 | 219.71 | 90.67 |

### Publicly funded vs fee-paying provision

- Publicly funded schools account for **74.7% of schools** and **83.3% of students**.
- Fee-paying schools account for **25.3% of schools** and **16.7% of students**.
- Publicly funded schools are larger on average.
- Fee-paying schools show higher aggregate student-to-teacher and student-to-administrator ratios.

### Paired regional comparison

| Indicator | Public mean | Fee-paying mean | Mean paired difference | Regions | Cohen's dz |
|---|---:|---:|---:|---:|---:|
| Students per school | 272.41 | 163.14 | +109.27 | 13 | 1.58 |
| Students per teacher | 11.36 | 16.04 | -4.68 | 13 | -1.93 |
| Students per administrator | 120.09 | 320.36 | -200.27 | 12 | -1.55 |

These results describe differences in institutional scale and recorded staffing intensity. They should **not** be interpreted as direct evidence of educational quality, efficiency, affordability, or causality.

## Repository Structure

```text
.
├── Supplementary_Code_High_School_Analysis_v3.py
├── Supplementary_Code_High_School_Analysis_v3_Colab.ipynb
├── Supplementary_Code_High_School_Analysis_v3_Colab_executed.ipynb
├── Supplementary_Data_General_Education_Statistics_2024.xlsx
├── analysis_outputs/
│   ├── table1_regional_descriptive_statistics.csv
│   ├── table2_school_type_summary.csv
│   ├── table3_public_vs_fee_paying_summary.csv
│   ├── table4_regional_school_load.csv
│   ├── table5_regional_summary.csv
│   ├── table6_paired_regional_comparison.csv
│   ├── supplementary_regional_funding_ratios.csv
│   ├── figure1_regional_resources.png
│   ├── figure2_gender_by_region.png
│   ├── figure3_sector_gender_composition.png
│   └── figure4_resource_ratios.png
├── High_School_Analysis_Outputs_v3.zip
├── analysis_run_log.txt
└── README.md
```

## Reproducibility

### Option 1 — Python script

Place the following two files in the same folder:

- `Supplementary_Code_High_School_Analysis_v3.py`
- `Supplementary_Data_General_Education_Statistics_2024.xlsx`

Then run:

```bash
python Supplementary_Code_High_School_Analysis_v3.py
```

The script generates report-ready CSV tables and figures inside `analysis_outputs/`.

### Option 2 — Google Colab

1. Upload `Supplementary_Code_High_School_Analysis_v3_Colab.ipynb` to Google Colab.
2. Select **Runtime → Run all**.
3. Upload `Supplementary_Data_General_Education_Statistics_2024.xlsx` when prompted.
4. The notebook generates the analysis outputs and a downloadable ZIP archive.

An executed notebook is also included for transparency:

`Supplementary_Code_High_School_Analysis_v3_Colab_executed.ipynb`

## Software

The analysis uses Python with:

- pandas
- NumPy
- SciPy
- Matplotlib
- Seaborn

## Data Handling Notes

Zero teacher or administrator counts are retained in count summaries because they appear in the published source. Ratios with zero denominators are treated as undefined rather than forced to zero or infinity.

The analysis uses aggregated administrative records rather than school-level microdata. Therefore:

- within-cell variation cannot be assessed;
- school-level independence cannot be assumed;
- p-values are exploratory because the 13 regions form a small national census rather than a random sample;
- staffing ratios are not equivalent to educational quality or class size;
- the dataset does not include tuition, expenditure, subsidies, scholarships, designed capacity, educational outcomes, household income, waiting lists, or parental preference variables.

## Figures and Tables

The analysis script reproduces:

- **Table 1:** Regional descriptive statistics
- **Table 2:** School-type resource summary
- **Table 3:** Publicly funded vs fee-paying provision
- **Table 4:** Regional students-per-school ranking
- **Table 5:** Regional high-school summary
- **Table 6:** Paired regional comparison of public vs fee-paying provision
- **Figure 1:** High-school resources by region
- **Figure 2:** Gender distribution by region
- **Figure 3:** School-type and gender composition
- **Figure 4:** Regional staffing and school-load ratios

## Interpretation

The repository is intended to provide a transparent and reproducible descriptive baseline for monitoring:

- regional education-system scale;
- sector composition;
- staffing intensity;
- school-load profiles; and
- differences between publicly funded and fee-paying provision.

The results should not be used alone to infer school quality, efficiency, overcrowding, affordability, private-school demand, or commercial viability. Those questions require school-level capacity, outcome, cost, demographic, geographic, and household-choice data.

## Citation

If you use this repository, please cite the associated manuscript:

```bibtex
@article{alazmi2026resource,
  title   = {Resource Allocation and Staffing Ratios Across School Types in Saudi Arabia's High School Education System: A National and Regional Descriptive Analysis},
  author  = {Alazmi, Meshari and Alqahtani, Faleh},
  year    = {2026},
  note    = {Manuscript}
}
```

Update the citation with the final journal, volume, article number, and DOI after publication.

## Authors

**Meshari Alazmi**  
College of Computer Science and Engineering, University of Ha'il, Saudi Arabia  
Corresponding author: `ms.alazmi@uoh.edu.sa`

**Faleh Alqahtani**  
College of Computing and Information Technology, Shaqra University, Saudi Arabia

## License

Add an appropriate software and data license before public release. A common choice for code is the **MIT License**, but the source-data redistribution terms should be confirmed independently before publishing the Excel workbook on GitHub.

## Disclaimer

This repository is provided for research transparency and reproducibility. The analysis is descriptive and exploratory and does not establish causal relationships or policy superiority between school sectors.

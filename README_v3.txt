Saudi High-School Resource Allocation Manuscript - Version 3
=============================================================

Core methodological correction
-------------------------------
The previous independent Welch tests based on 94 publicly funded and 98 fee-paying
administrative cells have been removed. The 192 high-school source cells are now:

1. classified as publicly funded (government) or fee-paying (private + international);
2. aggregated within each of the 13 regions and funding groups, summing across gender
   and education administrations;
3. converted to students-per-school, students-per-teacher, and students-per-administrator
   ratios after aggregation; and
4. compared as paired regional observations.

Table 6 reports paired-samples t-tests, 95% confidence intervals, Cohen's dz, and
Wilcoxon signed-rank sensitivity tests. Students per school and students per teacher
use all 13 regions. Students per administrator uses 12 regions because the fee-paying
administrator total for Al Bahah is zero, making that ratio undefined.

Files
-----
- Manuscript_RA_school_Q1_revised_v3_regional_paired.docx
- Manuscript_RA_school_Q1_revised_v3_regional_paired.pdf
- Supplementary_Code_High_School_Analysis_v3.py
- Supplementary_Code_High_School_Analysis_v3_Colab.ipynb
- Supplementary_Code_High_School_Analysis_v3_Colab_executed.ipynb
- Supplementary_Data_General_Education_Statistics_2024.xlsx
- analysis_outputs/ (Tables 1-6, Figures 1-4, and underlying regional funding ratios)
- High_School_Analysis_Outputs_v3.zip

Running in Google Colab
-----------------------
1. Upload Supplementary_Code_High_School_Analysis_v3_Colab.ipynb to Colab.
2. Select Runtime > Run all.
3. Upload Supplementary_Data_General_Education_Statistics_2024.xlsx when prompted.
4. The notebook creates analysis_outputs/ and High_School_Analysis_Outputs_v3.zip.

Interpretation
--------------
The funding classification is operational. The Ministry dataset does not contain tuition,
scholarships, subsidies, household expenditure, school costs, capacity, or outcomes.
The paired tests describe regional differences in scale and recorded staffing intensity;
they do not establish educational quality, efficiency, affordability, or causality.

# Reproducibility

Verified October 16, 2026: Python 3.12.10 on Windows. All 18 retained scripts passed in-memory syntax compilation. All 13 implemented experiments passed in temporary copies; all 17 CSVs and the processed dataset reproduced at rtol=atol=1e-9. No finalized research output was overwritten.

## Environment

From the research project directory in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Optional exact snapshot of the existing local environment:
python -m pip install -r requirements-verified.txt
```

The existing .venv was retained and used; no packages were installed. If activation is blocked, invoke .\.venv\Scripts\python.exe directly. Minimal direct dependencies: numpy, pandas, matplotlib, scikit-learn. scipy is transitive. Observed versions: {"numpy": "2.5.4", "pandas": "3.0.6", "scikit-learn": "1.9.1", "matplotlib": "3.11.2", "scipy": "1.18.1"}. requirements-verified.txt snapshots all installed distributions, including optional development packages; clean installation was not tested.

## Inputs and order

Immutable original input: data/raw/Medicare_DME_Devices_Supplies_by_Geography_and_Service_2023.csv. Finalized primary input: data/processed/medicare_dme_2023_51_areas.csv; script 07 regenerates it from raw data. See data_provenance.md for SHA-256 hashes and filters. The original acquisition date is unknown. Download the 2023 CSV from the official CMS catalog linked in that document and place it at the exact path above. Redistribution terms are unverified; the files are excluded from Git.

Execute from the project directory:

```powershell
python .\src\01_data_audit.py
python .\src\02_descriptive_analysis.py
python .\src\03_baseline_regression.py
python .\src\04_geographic_holdout.py
python .\src\05_repeated_validation.py
python .\src\06_leave_one_area_out.py
python .\src\07_study_population.py
python .\src\08_main_study_validation.py
python .\src\09_code_error_decomposition.py
python .\src\10_hcpcs_geographic_variation.py
python .\src\11_standardization_figure.py
python .\src\12_paired_payment_prediction.py
python .\src\13_rental_aware_validation.py
```

Scripts 01-06 use the preliminary 60-category state-labeled population. Script 07 selects 50 states plus DC; 08-10 and 12-13 use that processed dataset. Script 11 reads script 10's CV table. Script paths resolve ROOT from __file__, independent of working directory. Five unused docstring-only scripts are excluded from this sequence.

Normal execution overwrites generated tables/figures and, for script 07, processed data. Preserve finalized artifacts or run a separate copy for comparison. The final audit copied src, data, results and paper into an isolated temporary project, ran scripts there and compared outputs, leaving originals unchanged. Initial seed: 42; repeated seeds: 0-29. Leave-one-area-out means are learned only from training areas. Rental-aware fallback: code/rental, then code, then global mean.

## Outputs and verification

CSV outputs are under results/tables; figure PDFs under results/figures. experiment_log.md maps all producers. Script 02 makes payment_distribution.pdf and geographic_coverage.pdf; script 11 makes standardization_cv_comparison.pdf. No additional paper/figures copies are required.

Verify paired_payment_summary.csv micro_MAE, rental_aware_summary.csv MAE/RMSE, code_error_decomposition.csv records and mean_absolute_error, hcpcs_geographic_cv_comparison.csv row count and positive CV_difference, and rental_aware_by_area.csv paired MAEs against RESULTS_SUMMARY.md. Allow 0.00000051 absolute error for supplied six-decimal values. Weight area MAEs by records for micro MAE; use equal area weights for macro MAE.

## MiKTeX build

```powershell
Push-Location .\paper
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
Pop-Location
```

Run PDFLaTeX twice and **do not run BibTeX**: references_manual.tex is active. The existing VS Code recipe already does this. Keep all seven sections and ../results/figures available. An isolated build passed twice with no unresolved citation/reference warnings; the preserved main.pdf extracted text matches rebuilt text. MiKTeX must be on PATH.

## Limits and troubleshooting

The data download date/revision and redistribution permission are unknown. No software license was found. Keep private correspondence and raw/processed data out of Git pending rights verification. One year of aggregate data and different targets limit inference; no future-year validation, causal analysis or geographic uncertainty intervals were completed.

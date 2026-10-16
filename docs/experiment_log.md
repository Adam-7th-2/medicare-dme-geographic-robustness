# Experiment Log

| Date | Code version | Dataset version | Feature set | Split | Seed | Metrics | Notes |
|---|---|---|---|---|---|---|---|


## Final audit - October 16, 2026

Retrospective rerun, not an assertion about original experiment dates or commits. Python 3.12.10 in the retained .venv. All scripts ran in temporary copies; scientific source unchanged.

| Script | Output (CSV under results/tables unless stated) | Status |
|---|---|---|
| `01_data_audit.py` | stdout audit | exit 0 |
| `02_descriptive_analysis.py` | descriptive_summary.csv; geographic_coverage.csv; hcpcs_coverage.csv; payment_distribution.pdf; geographic_coverage.pdf | exit 0 |
| `03_baseline_regression.py` | baseline_random_split.csv | exit 0 |
| `04_geographic_holdout.py` | validation_comparison.csv; geographic_gap.csv; geographic_reliability.csv | exit 0 |
| `05_repeated_validation.py` | repeated_validation.csv | exit 0 |
| `06_leave_one_area_out.py` | leave_one_area_out.csv | exit 0 |
| `07_study_population.py` | data/processed/medicare_dme_2023_51_areas.csv | exit 0 |
| `08_main_study_validation.py` | main_study_51_area_validation.csv | exit 0 |
| `09_code_error_decomposition.py` | code_error_decomposition.csv | exit 0 |
| `10_hcpcs_geographic_variation.py` | hcpcs_geographic_cv_comparison.csv | exit 0 |
| `11_standardization_figure.py` | standardization_cv_comparison.pdf | exit 0 |
| `12_paired_payment_prediction.py` | paired_payment_summary.csv; paired_payment_by_area.csv; paired_payment_code_coverage.csv | exit 0 |
| `13_rental_aware_validation.py` | rental_aware_summary.csv; rental_aware_by_area.csv | exit 0 |

All 17 CSVs reproduced at rtol=atol=1e-9. Original code-version history and experiment dates are unavailable.

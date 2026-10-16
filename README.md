# Beyond Prediction Accuracy

**Evaluating Geographic Robustness and Reliability in Machine Learning Models for Medicare Durable Medical Equipment Payments**

Henok Tariku Yadeta, Moscow Institute of Physics and Technology (MIPT).

## Research overview

How reliable are Medicare DME payment predictions in geographic areas excluded entirely from training? The study compares prediction error for actual and geographically standardized average payment targets in CMS 2023 aggregate records. The completed experiments use **interpretable mean-based baselines rather than Random Forests or deep neural networks**.

## Dataset source and provenance

[Official CMS catalog](https://data.cms.gov/provider-summary-by-type-of-service/medicare-durable-medical-equipment-devices-supplies/medicare-durable-medical-equipment-devices-supplies-by-geography-and-service): 2023 Medicare Durable Medical Equipment, Devices & Supplies by Geography and Service. Local original: data/raw/Medicare_DME_Devices_Supplies_by_Geography_and_Service_2023.csv. The raw file has 38,675 rows and 18 columns. Exploratory analyses retain 37,028 State-labeled rows over 60 categories; the primary population contains 36,528 rows, 50 states plus DC, and 1,250 HCPCS codes. Original download date and precise release revision are unrecorded. See docs/data_provenance.md for filters and SHA-256 hashes. Public-use aggregate data can reflect suppression and do not describe individual patients. Redistribution terms remain unverified; raw and processed data are ignored by Git.

## Objectives and evaluation design

Compare random and geographic evaluation, inspect errors by area and code coverage, assess within-code geographic variability and distinguish payment-target variability from prediction performance. Preliminary work uses the 60-category population: initial 80/20 splits with seed 42, followed by repeated random/group splits over seeds 0-29. Main leave-one-area-out validation trains on 50 areas and holds out the remaining area, repeating across all 51. Every primary row is evaluated once per target.

## Methods and predictors

The global baseline predicts the training mean. HCPCS-only predictions use the training mean for each HCPCS code, falling back to the global mean. Rental-aware predictions use joint HCPCS/rental means, then code means, then the global mean. Actual and standardized targets are predicted separately on matching geographic partitions. All means are learned only from training areas. Metrics include micro/macro MAE, RMSE, NMAE and worst-area MAE. Descriptive CVs use sample standard deviations within code/rental groups represented in at least ten areas.

## Key verified experimental findings

| Held-out model | Actual-payment MAE | Standardized-payment MAE |
|---|---:|---:|
| HCPCS mean | 47.838395 | 38.878699 |
| HCPCS plus rental mean | 19.894409 | 10.300449 |

Adding rental classification substantially reduced held-out actual-payment MAE. Standardized-target MAE was lower in all 51 tested areas under both paired specifications. Of 916 comparable HCPCS/rental groups, 805 had lower standardized CV. Unseen HCPCS codes generated disproportionately high errors: 137 unseen-code observations had actual MAE 746.996987, compared with 36,391 known-code observations.

Random splits were not consistently more optimistic: geographic MAE exceeded random MAE in 12 of 30 preliminary comparisons. Mean geographic and random MAEs were 47.60 and 49.07; differing test composition limits interpretation. Errors for different payment targets are not interchangeable. A lower standardized-target MAE does not establish a causal improvement in predicting actual Medicare payments. Full values and producing scripts: docs/RESULTS_SUMMARY.md.

## Repository structure

- data/raw and data/processed: preserved original input and finalized 51-area dataset, retained locally and ignored by Git.
- src: 13 implemented experiments and five inert placeholders awaiting deletion approval.
- results/tables: 17 verified CSVs; results/figures: three manuscript figure PDFs.
- paper: main.tex, main.pdf, seven section files, active references_manual.tex and retained legacy references.bib.
- docs: data provenance, experiment log, reproducibility guide and verified result summary.
- .vscode/settings.json: existing Python interpreter and PDFLaTeX-twice recipe.
- data/raw and data/processed contain local-only inputs; the CSV files are excluded from Git pending redistribution-rights verification.
- notebooks and submission: intentional organizational placeholders.

## Python and Windows installation

From this project directory in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If activation is unavailable, call .\.venv\Scripts\python.exe directly. Existing .venv was retained. No package was installed during the audit.

## Reproducibility and execution order

Download the original 2023 CSV from the official CMS catalog linked above and place it at `data/raw/Medicare_DME_Devices_Supplies_by_Geography_and_Service_2023.csv`. Execute the 13 implemented scripts in numeric order, starting with `python .\src\01_data_audit.py`. Script 07 regenerates `data/processed/medicare_dme_2023_51_areas.csv`; script 10 must precede figure script 11. The complete PowerShell command sequence is in docs/REPRODUCIBILITY.md; producer/output mapping is in docs/experiment_log.md. Five similarly numbered placeholder files perform no experiment and are excluded from that sequence. Confirm CMS redistribution terms before sharing either CSV.

Normal execution overwrites generated outputs, including processed data in script 07. Preserve finalized artifacts or work in a copy when validating revisions. Paths resolve from each script's location. The 13 implemented experiments were validated in temporary copies; their 17 CSV outputs and processed data reproduced at rtol=atol=1e-9.

## Compile the LaTeX paper

With MiKTeX PDFLaTeX on PATH, from this project directory:

```powershell
Push-Location .\paper
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error main.tex
Pop-Location
```

Use references_manual.tex and **do not run BibTeX**. The existing VS Code recipe already runs PDFLaTeX twice. Keep ../results/figures available relative to paper; no duplicate paper/figures copies were created. An isolated two-pass build passed without unresolved references/citations. The preserved final PDF's extracted text matches the rebuild. All ten existing PDF pages were rendered and visually reviewed; all three figures and five tables display.

## Output figures and tables

Script 02 produces payment_distribution.pdf (exploratory log-scale payment histogram) and geographic_coverage.pdf (top 15 exploratory areas). Script 11 produces standardization_cv_comparison.pdf (916 primary code/rental groups). The five consolidated paper tables cover dataset composition, preliminary baselines, known/unseen code coverage, paired geographic CVs, and prediction errors. Table entries match recorded outputs at displayed precision. The 17 detailed CSVs are mapped in docs/experiment_log.md.

## Dependencies and software environment

Verified on Python 3.12.10, Windows. Four direct runtime dependencies: numpy, pandas, matplotlib, scikit-learn. Observed versions: numpy 2.5.4, pandas 3.0.6, scikit-learn 1.9.1, matplotlib 3.11.2, scipy 1.18.1; scipy is transitive. requirements.txt lists minimal direct requirements; requirements-verified.txt snapshots the complete installed environment, including optional development packages. A fresh installation was not tested; exact pins document the local verification environment. MiKTeX provides PDFLaTeX and PDF utilities.

## Important limitations and interpretation

One year, aggregate records, suppression, varying service volume and unmatched preliminary test populations limit inference. Metrics weight rows equally, not beneficiaries or expenditure. NMAE divides MAE by the relevant mean target and is not MAPE. No future-year test, geographic uncertainty intervals, flexible-model comparison or causal standardization experiment was completed. Lower standardized-target error is a comparison of different outcomes, not demonstrated better actual-expenditure prediction.

## Citations and academic references

paper/references_manual.tex contains ten academic/data references; all are cited and resolve: cmsdme2023, roberts2017, odonnell2013, subbaswamy2020, pedregosa2011, kohavi1995, steyerberg2010, arlot2010, cawley2010, varma2006. They cover CMS data, structured validation, payment standardization, dataset shift, prediction assessment, scikit-learn and model-selection bias. Preserve that file as the active citation source. references.bib remains useful legacy metadata. Citation resolution is verified; publisher-by-publisher bibliographic metadata verification was not performed.

## Final submission artifacts and project status

Reviewed manuscript: **paper/main.pdf**, preserved with its original source. Regeneration requires main.tex, seven sections, references_manual.tex and three results/figures PDFs. PDFLaTeX succeeds in two passes without BibTeX. See docs/REPRODUCIBILITY.md for the exact build commands.

## License and data-sharing notes

No project software license or verified dataset redistribution terms were found. No license or repository URL is invented. The source and processed CMS CSVs remain local and ignored until redistribution terms are verified. Private correspondence and personal records are not part of this repository.

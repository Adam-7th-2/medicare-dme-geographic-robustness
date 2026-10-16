
from pathlib import Path
import numpy as np
import pandas as pd

# Project directories
ROOT = Path(__file__).resolve().parents[1]

DATA = (
    ROOT / "data" / "processed"
    / "medicare_dme_2023_51_areas.csv"
)

OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

# Variables
CODE = "HCPCS_Cd"
RENTAL = "Suplr_Rentl_Ind"
AREA = "Rfrg_Prvdr_Geo_Desc"

ACTUAL = "Avg_Suplr_Mdcr_Pymt_Amt"
STANDARD = "Avg_Suplr_Mdcr_Stdzd_Amt"

# Load the finalized 51-area dataset
df = pd.read_csv(DATA, low_memory=False)

assert df[AREA].nunique() == 51

# Keep records with valid positive payment amounts
for col in [ACTUAL, STANDARD]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

valid = (
    df[[ACTUAL, STANDARD]].notna().all(axis=1)
    & np.isfinite(df[ACTUAL])
    & np.isfinite(df[STANDARD])
    & (df[ACTUAL] > 0)
    & (df[STANDARD] > 0)
)

df = df.loc[valid].copy()

print("VALID RECORDS:", len(df))

# Check for multiple records in a geographic/code/rental group
keys = [CODE, RENTAL, AREA]
duplicates = df.duplicated(subset=keys).sum()

print("DUPLICATE GROUP KEYS:", duplicates)

if duplicates:
    raise ValueError(
        "Multiple rows have the same HCPCS, rental "
        "indicator and geographic area. Inspect "
        "their additional grouping fields first."
    )

# Descriptive coefficient of variation
# ddof=1 means sample standard deviation
summary = (
    df.groupby([CODE, RENTAL])
    .agg(
        areas=(AREA, "nunique"),
        actual_mean=(ACTUAL, "mean"),
        actual_sd=(ACTUAL, "std"),
        standard_mean=(STANDARD, "mean"),
        standard_sd=(STANDARD, "std")
    )
    .reset_index()
)

# Retain sufficiently represented groups
# The threshold is a design choice, not a CMS rule.
summary = summary.loc[
    summary["areas"] >= 10
].copy()

summary["CV_actual"] = (
    summary["actual_sd"] / summary["actual_mean"]
)

summary["CV_standardized"] = (
    summary["standard_sd"] / summary["standard_mean"]
)

summary["CV_difference"] = (
    summary["CV_actual"]
    - summary["CV_standardized"]
)

summary = summary.replace(
    [np.inf, -np.inf], np.nan
).dropna(
    subset=["CV_actual", "CV_standardized"]
)

print("\nGROUPS WITH AT LEAST 10 GEOGRAPHIC AREAS")
print(len(summary))

print("\nCV SUMMARY")
print(
    summary[
        ["CV_actual", "CV_standardized", "CV_difference"]
    ].describe().to_string()
)

print("\nGROUPS WITH LOWER STANDARDIZED CV")
print((summary["CV_difference"] > 0).sum())

print("\nGROUPS WITH HIGHER STANDARDIZED CV")
print((summary["CV_difference"] < 0).sum())

print("\nGROUPS WITH EQUAL CV")
print((summary["CV_difference"] == 0).sum())

print("\nTOP 10 LARGEST CV REDUCTIONS")
print(
    summary.nlargest(
        10, "CV_difference"
    )[
        [CODE, RENTAL, "areas",
         "CV_actual", "CV_standardized",
         "CV_difference"]
    ].to_string(index=False)
)

print("\nTOP 10 CV INCREASES AFTER STANDARDIZATION")
print(
    summary.nsmallest(
        10, "CV_difference"
    )[
        [CODE, RENTAL, "areas",
         "CV_actual", "CV_standardized",
         "CV_difference"]
    ].to_string(index=False)
)

summary.to_csv(
    OUT / "hcpcs_geographic_cv_comparison.csv",
    index=False
)

print("\nLESSON 8 EXPERIMENT COMPLETED")

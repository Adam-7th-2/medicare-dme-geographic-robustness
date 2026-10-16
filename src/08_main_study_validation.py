
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

# 1. Load the finalized 51-area dataset
ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT / "data" / "processed"
    / "medicare_dme_2023_51_areas.csv"
)

OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

TARGET = "Avg_Suplr_Mdcr_Pymt_Amt"
AREA = "Rfrg_Prvdr_Geo_Desc"
CODE = "HCPCS_Cd"

df = pd.read_csv(DATA_PATH, low_memory=False)

assert df[AREA].nunique() == 51

results = []

# 2. Hold out one geographic area at a time
for area in sorted(df[AREA].unique()):

    train = df.loc[df[AREA] != area]
    test = df.loc[df[AREA] == area].copy()

    # Ensure no geographic overlap
    assert area not in set(train[AREA])

    # 3. Learn baseline from training data only
    global_mean = train[TARGET].mean()
    code_means = train.groupby(CODE)[TARGET].mean()

    # Which test codes were seen in training?
    known = test[CODE].isin(code_means.index)

    # Predict using code means, with fallback
    predictions = (
        test[CODE].map(code_means)
        .fillna(global_mean)
    )

    errors = (
        test[TARGET] - predictions
    ).abs()

    # Overall geographic error
    area_mae = errors.mean()

    # Error among known HCPCS codes
    known_mae = (
        errors.loc[known].mean()
        if known.any() else np.nan
    )

    # Error among unseen HCPCS codes
    unseen_mae = (
        errors.loc[~known].mean()
        if (~known).any() else np.nan
    )

    results.append({
        "geography": area,
        "records": len(test),
        "MAE": area_mae,
        "known_MAE": known_mae,
        "unseen_MAE": unseen_mae,
        "known_records": int(known.sum()),
        "unseen_records": int((~known).sum()),
        "known_fraction": known.mean()
    })

# 4. Results
results = pd.DataFrame(results)
results = results.sort_values("MAE", ascending=False)

print("\nTOP 10 HIGHEST-ERROR AREAS")
print(results.head(10).to_string(index=False))

print("\nOVERALL SUMMARY")
print("Areas:", len(results))
print("Total test records:", results["records"].sum())
print("Macro MAE:", results["MAE"].mean())

micro_mae = np.average(
    results["MAE"],
    weights=results["records"]
)

print("Micro MAE:", micro_mae)
print("Worst-area MAE:", results["MAE"].max())

print("\nHCPCS COVERAGE SUMMARY")
print("Total known records:", results["known_records"].sum())
print("Total unseen records:", results["unseen_records"].sum())
print("Areas with unseen codes:",
      (results["unseen_records"] > 0).sum())

# 5. Save results
results.to_csv(
    OUT / "main_study_51_area_validation.csv",
    index=False
)

print("\nMAIN STUDY VALIDATION COMPLETED")


from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)

# ======================================
# 1. PROJECT PATHS
# ======================================

ROOT = Path(__file__).resolve().parents[1]

DATA = (
    ROOT / "data" / "processed"
    / "medicare_dme_2023_51_areas.csv"
)

OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

AREA = "Rfrg_Prvdr_Geo_Desc"
CODE = "HCPCS_Cd"

ACTUAL = "Avg_Suplr_Mdcr_Pymt_Amt"
STANDARD = "Avg_Suplr_Mdcr_Stdzd_Amt"

# ======================================
# 2. LOAD AND VALIDATE DATA
# ======================================

df = pd.read_csv(DATA, low_memory=False)

for col in [ACTUAL, STANDARD]:
    df[col] = pd.to_numeric(
        df[col], errors="coerce"
    )

valid = (
    df[[ACTUAL, STANDARD]].notna().all(axis=1)
    & np.isfinite(df[ACTUAL])
    & np.isfinite(df[STANDARD])
    & (df[ACTUAL] > 0)
    & (df[STANDARD] > 0)
    & df[AREA].notna()
    & df[CODE].notna()
)

df = df.loc[valid].copy()

assert df[AREA].nunique() == 51

print("VALID RECORDS:", len(df))
print("GEOGRAPHIC AREAS:", df[AREA].nunique())

# ======================================
# 3. LEAVE-ONE-AREA-OUT EXPERIMENT
# ======================================

area_results = []
all_predictions = []

for area in sorted(df[AREA].unique()):

    train = df.loc[df[AREA] != area].copy()
    test = df.loc[df[AREA] == area].copy()

    assert area not in set(train[AREA])

    known_codes = test[CODE].isin(
        train[CODE].unique()
    )

    # Both targets use the same train/test
    # area split and the same HCPCS feature.
    for target_name, target in [
        ("Actual", ACTUAL),
        ("Standardized", STANDARD)
    ]:

        global_mean = train[target].mean()

        code_means = (
            train.groupby(CODE)[target].mean()
        )

        predictions = (
            test[CODE]
            .map(code_means)
            .fillna(global_mean)
        )

        errors = (
            test[target] - predictions
        ).abs()

        mae = mean_absolute_error(
            test[target], predictions
        )

        rmse = np.sqrt(
            mean_squared_error(
                test[target], predictions
            )
        )

        # Relative to the mean of that
        # target within the test area.
        target_mean = test[target].mean()
        nmae = mae / target_mean

        area_results.append({
            "geography": area,
            "target": target_name,
            "records": len(test),
            "MAE": mae,
            "RMSE": rmse,
            "NMAE": nmae,
            "known_records": int(known_codes.sum()),
            "unseen_records": int((~known_codes).sum())
        })

        all_predictions.append(pd.DataFrame({
            "geography": area,
            "target": target_name,
            "actual_value": test[target].to_numpy(),
            "prediction": predictions.to_numpy(),
            "absolute_error": errors.to_numpy(),
            "known_code": known_codes.to_numpy()
        }))

area_results = pd.DataFrame(area_results)
predictions_df = pd.concat(
    all_predictions, ignore_index=True
)

# ======================================
# 4. GLOBAL PERFORMANCE BY TARGET
# ======================================

summary_rows = []

for target_name, group in predictions_df.groupby("target"):

    mae = mean_absolute_error(
        group["actual_value"],
        group["prediction"]
    )

    rmse = np.sqrt(
        mean_squared_error(
            group["actual_value"],
            group["prediction"]
        )
    )

    nmae = mae / group["actual_value"].mean()

    area_subset = area_results.loc[
        area_results["target"] == target_name
    ]

    summary_rows.append({
        "target": target_name,
        "records": len(group),
        "micro_MAE": mae,
        "micro_RMSE": rmse,
        "pooled_NMAE": nmae,
        "macro_MAE": area_subset["MAE"].mean(),
        "worst_area_MAE": area_subset["MAE"].max(),
        "worst_area": area_subset.loc[
            area_subset["MAE"].idxmax(), "geography"
        ]
    })

summary = pd.DataFrame(summary_rows)

print("\nOVERALL PAIRED PREDICTION RESULTS")
print(summary.to_string(index=False))

# ======================================
# 5. PAIRED STATE-LEVEL COMPARISON
# ======================================

paired = area_results.pivot(
    index="geography",
    columns="target",
    values=["MAE", "NMAE"]
)

paired.columns = [
    f"{metric}_{target}"
    for metric, target in paired.columns
]

paired["MAE_reduction"] = (
    paired["MAE_Actual"]
    - paired["MAE_Standardized"]
)

paired["NMAE_reduction"] = (
    paired["NMAE_Actual"]
    - paired["NMAE_Standardized"]
)

print("\nPAIRED STATE-LEVEL SUMMARY")
print("Areas with lower standardized MAE:",
      int((paired["MAE_reduction"] > 0).sum()))

print("Areas with lower standardized NMAE:",
      int((paired["NMAE_reduction"] > 0).sum()))

print("\nTOP 10 BY ACTUAL-PAYMENT MAE")
print(
    paired.sort_values(
        "MAE_Actual", ascending=False
    ).head(10).to_string()
)

# ======================================
# 6. KNOWN / UNSEEN CODE COMPARISON
# ======================================

coverage_results = (
    predictions_df
    .groupby(["target", "known_code"])
    .agg(
        records=("absolute_error", "size"),
        MAE=("absolute_error", "mean")
    )
)

print("\nKNOWN / UNSEEN CODE COMPARISON")
print(coverage_results.to_string())

# ======================================
# 7. SAVE RESULTS
# ======================================

summary.to_csv(
    OUT / "paired_payment_summary.csv",
    index=False
)

paired.to_csv(
    OUT / "paired_payment_by_area.csv"
)

coverage_results.to_csv(
    OUT / "paired_payment_code_coverage.csv"
)

print("\nLESSON 9 EXPERIMENT COMPLETED")

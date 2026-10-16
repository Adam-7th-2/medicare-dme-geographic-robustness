
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    GroupShuffleSplit
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)

# ==========================================
# 1. PROJECT PATHS
# ==========================================

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT / "data" / "raw"
    / "Medicare_DME_Devices_Supplies_by_Geography_and_Service_2023.csv"
)

RESULTS_DIR = ROOT / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TARGET = "Avg_Suplr_Mdcr_Pymt_Amt"
GROUP = "Rfrg_Prvdr_Geo_Desc"
CODE = "HCPCS_Cd"

# ==========================================
# 2. LOAD AND PREPARE DATA
# ==========================================

df = pd.read_csv(DATA_PATH, low_memory=False)

df = df.loc[
    df["Rfrg_Prvdr_Geo_Lvl"] == "State"
].copy()

df[TARGET] = pd.to_numeric(
    df[TARGET],
    errors="coerce"
)

df = df.dropna(
    subset=[TARGET, GROUP, CODE]
).copy()

print("TOTAL RECORDS:", len(df))
print("GEOGRAPHIC CATEGORIES:", df[GROUP].nunique())

# ==========================================
# 3. PREDICT AND EVALUATE BASELINES
# ==========================================

def evaluate_split(train, test, split_name):

    train = train.copy()
    test = test.copy()

    # Baseline A: global mean
    global_mean = train[TARGET].mean()

    # Baseline B: HCPCS mean, learned
    # exclusively from training records
    code_means = (
        train.groupby(CODE)[TARGET].mean()
    )

    test["global_prediction"] = global_mean

    test["hcpcs_prediction"] = (
        test[CODE]
        .map(code_means)
        .fillna(global_mean)
    )

    known_codes = test[CODE].isin(
        code_means.index
    )

    records = []

    for model, pred_col in [
        ("Global mean", "global_prediction"),
        ("HCPCS mean", "hcpcs_prediction")
    ]:
        mae = mean_absolute_error(
            test[TARGET],
            test[pred_col]
        )

        rmse = np.sqrt(
            mean_squared_error(
                test[TARGET],
                test[pred_col]
            )
        )

        records.append({
            "split": split_name,
            "model": model,
            "train_n": len(train),
            "test_n": len(test),
            "MAE": mae,
            "RMSE": rmse,
            "known_test_codes": int(
                known_codes.sum()
            ),
            "unseen_test_codes": int(
                (~known_codes).sum()
            )
        })

    return pd.DataFrame(records), test

# ==========================================
# 4. RANDOM SPLIT
# ==========================================

random_train, random_test = train_test_split(
    df,
    test_size=0.20,
    random_state=42
)

random_results, random_predictions = (
    evaluate_split(
        random_train,
        random_test,
        "Random"
    )
)

# ==========================================
# 5. GEOGRAPHIC HOLDOUT
# ==========================================

splitter = GroupShuffleSplit(
    n_splits=1,
    test_size=0.20,
    random_state=42
)

train_idx, test_idx = next(
    splitter.split(
        df,
        groups=df[GROUP]
    )
)

geo_train = df.iloc[train_idx].copy()
geo_test = df.iloc[test_idx].copy()

# Explicitly check that no geographic
# category occurs in both subsets.
train_areas = set(geo_train[GROUP])
test_areas = set(geo_test[GROUP])

assert train_areas.isdisjoint(test_areas), (
    "Geographic data leakage detected!"
)

geo_results, geo_predictions = (
    evaluate_split(
        geo_train,
        geo_test,
        "Geographic"
    )
)

# ==========================================
# 6. COMPARE EXPERIMENTS
# ==========================================

results = pd.concat(
    [random_results, geo_results],
    ignore_index=True
)

print("\nEXPERIMENT RESULTS")
print(results.to_string(index=False))

comparison = results.pivot(
    index="model",
    columns="split",
    values="MAE"
)

comparison["geographic_gap"] = (
    comparison["Geographic"]
    - comparison["Random"]
)

print("\nGEOGRAPHIC MAE GAP")
print(comparison.to_string())

# ==========================================
# 7. GEOGRAPHIC COVERAGE
# ==========================================

print("\nHELD-OUT GEOGRAPHIC AREAS")

for area in sorted(test_areas):
    print(area)

print("\nGEOGRAPHIC TRAIN AREAS:", len(train_areas))
print("GEOGRAPHIC TEST AREAS:", len(test_areas))

# ==========================================
# 8. GEOGRAPHIC RELIABILITY
# ==========================================

geo_predictions["absolute_error"] = (
    geo_predictions[TARGET]
    - geo_predictions["hcpcs_prediction"]
).abs()

per_area = (
    geo_predictions
    .groupby(GROUP)
    .agg(
        records=(TARGET, "size"),
        MAE=("absolute_error", "mean")
    )
    .sort_values("MAE", ascending=False)
)

print("\nERROR BY HELD-OUT GEOGRAPHIC AREA")
print(per_area.to_string())

# ==========================================
# 9. SAVE RESULTS
# ==========================================

results.to_csv(
    RESULTS_DIR / "validation_comparison.csv",
    index=False
)

comparison.to_csv(
    RESULTS_DIR / "geographic_gap.csv"
)

per_area.to_csv(
    RESULTS_DIR / "geographic_reliability.csv"
)

print("\nLESSON 4 EXPERIMENT COMPLETED")

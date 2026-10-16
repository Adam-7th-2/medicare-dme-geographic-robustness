
from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.model_selection import (
    train_test_split,
    GroupShuffleSplit
)
from sklearn.metrics import mean_absolute_error

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT / "data" / "raw"
    / "Medicare_DME_Devices_Supplies_by_Geography_and_Service_2023.csv"
)

OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

TARGET = "Avg_Suplr_Mdcr_Pymt_Amt"
GROUP = "Rfrg_Prvdr_Geo_Desc"
CODE = "HCPCS_Cd"

df = pd.read_csv(DATA_PATH, low_memory=False)

df = df.loc[
    df["Rfrg_Prvdr_Geo_Lvl"] == "State"
].dropna(
    subset=[TARGET, GROUP, CODE]
).copy()

def baseline_mae(train, test):
    global_mean = train[TARGET].mean()

    means = train.groupby(CODE)[TARGET].mean()

    predictions = (
        test[CODE]
        .map(means)
        .fillna(global_mean)
    )

    return mean_absolute_error(
        test[TARGET], predictions
    )

records = []

for seed in range(30):

    # Random row split
    train_r, test_r = train_test_split(
        df, test_size=0.2,
        random_state=seed
    )

    random_mae = baseline_mae(
        train_r, test_r
    )

    # Geographic group split
    splitter = GroupShuffleSplit(
        n_splits=1,
        test_size=0.2,
        random_state=seed
    )

    train_idx, test_idx = next(
        splitter.split(df, groups=df[GROUP])
    )

    train_g = df.iloc[train_idx]
    test_g = df.iloc[test_idx]

    assert set(train_g[GROUP]).isdisjoint(
        set(test_g[GROUP])
    )

    geographic_mae = baseline_mae(
        train_g, test_g
    )

    records.append({
        "seed": seed,
        "random_MAE": random_mae,
        "geographic_MAE": geographic_mae,
        "geographic_gap": (
            geographic_mae - random_mae
        ),
        "geographic_test_n": len(test_g)
    })

results = pd.DataFrame(records)

print("\nREPEATED VALIDATION: 30 SPLITS")
print(results.to_string(index=False))

print("\nSUMMARY")
print(
    results[
        ["random_MAE", "geographic_MAE",
         "geographic_gap"]
    ].agg(["mean", "std", "min", "max"])
)

positive = (results["geographic_gap"] > 0).sum()

print("\nPOSITIVE GEOGRAPHIC GAPS:", positive, "/ 30")

results.to_csv(
    OUT / "repeated_validation.csv",
    index=False
)

print("\nREPEATED VALIDATION COMPLETED")

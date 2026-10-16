
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

df = pd.read_csv(
    ROOT / "data" / "processed"
    / "medicare_dme_2023_51_areas.csv",
    low_memory=False
)

TARGET = "Avg_Suplr_Mdcr_Pymt_Amt"
AREA = "Rfrg_Prvdr_Geo_Desc"
CODE = "HCPCS_Cd"

records = []

for area in sorted(df[AREA].unique()):
    train = df[df[AREA] != area]
    test = df[df[AREA] == area].copy()

    global_mean = train[TARGET].mean()
    code_means = train.groupby(CODE)[TARGET].mean()

    predictions = test[CODE].map(code_means)

    test["code_status"] = np.where(
        predictions.notna(), "Known", "Unseen"
    )

    test["absolute_error"] = (
        test[TARGET]
        - predictions.fillna(global_mean)
    ).abs()

    records.append(
        test[[AREA, CODE, "code_status",
              "absolute_error"]]
    )

evaluated = pd.concat(records, ignore_index=True)

summary = evaluated.groupby("code_status").agg(
    records=("absolute_error", "size"),
    mean_absolute_error=("absolute_error", "mean"),
    total_absolute_error=("absolute_error", "sum")
)

summary["record_share_pct"] = (
    100 * summary["records"] / len(evaluated)
)

summary["error_share_pct"] = (
    100 * summary["total_absolute_error"]
    / summary["total_absolute_error"].sum()
)

print("\nKNOWN VS UNSEEN CODE ERROR DECOMPOSITION")
print(summary.to_string())

print("\nOVERALL RECORD-WEIGHTED MAE")
print(evaluated["absolute_error"].mean())

OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

summary.to_csv(
    OUT / "code_error_decomposition.csv"
)

print("\nEXPERIMENT COMPLETED")


from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error
)

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

df = df[
    df["Rfrg_Prvdr_Geo_Lvl"] == "State"
].dropna(
    subset=[TARGET, GROUP, CODE]
).copy()

results = []

for area in sorted(df[GROUP].unique()):

    train = df[df[GROUP] != area]
    test = df[df[GROUP] == area]

    global_mean = train[TARGET].mean()

    code_means = (
        train.groupby(CODE)[TARGET].mean()
    )

    known = test[CODE].isin(code_means.index)

    prediction = (
        test[CODE]
        .map(code_means)
        .fillna(global_mean)
    )

    mae = mean_absolute_error(
        test[TARGET], prediction
    )

    rmse = np.sqrt(
        mean_squared_error(
            test[TARGET], prediction
        )
    )

    results.append({
        "geography": area,
        "records": len(test),
        "MAE": mae,
        "RMSE": rmse,
        "known_code_records": int(known.sum()),
        "unseen_code_records": int((~known).sum())
    })

results = pd.DataFrame(results)

results = results.sort_values(
    "MAE", ascending=False
)

print("\nLEAVE-ONE-AREA-OUT RESULTS")
print(results.to_string(index=False))

print("\nSUMMARY")
print("Geographic categories:", len(results))
print("Mean area MAE:", results["MAE"].mean())
print("Median area MAE:", results["MAE"].median())
print("Worst area MAE:", results["MAE"].max())
print("Best area MAE:", results["MAE"].min())

weighted_mae = np.average(
    results["MAE"],
    weights=results["records"]
)

print("Record-weighted MAE:", weighted_mae)

results.to_csv(
    OUT / "leave_one_area_out.csv",
    index=False
)

print("\nLESSON 5 EXPERIMENT COMPLETED")

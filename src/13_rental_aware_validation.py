
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data" / "processed" / "medicare_dme_2023_51_areas.csv"
OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

AREA = "Rfrg_Prvdr_Geo_Desc"
CODE = "HCPCS_Cd"
RENTAL = "Suplr_Rentl_Ind"

TARGETS = {
    "Actual": "Avg_Suplr_Mdcr_Pymt_Amt",
    "Standardized": "Avg_Suplr_Mdcr_Stdzd_Amt"
}

df = pd.read_csv(DATA, low_memory=False)

assert df[AREA].nunique() == 51

# Use the same eligible records for both targets
for target in TARGETS.values():
    df[target] = pd.to_numeric(df[target], errors="coerce")

valid = df[
    list(TARGETS.values())
].notna().all(axis=1)

for target in TARGETS.values():
    valid &= np.isfinite(df[target]) & (df[target] > 0)

valid &= df[[AREA, CODE, RENTAL]].notna().all(axis=1)
df = df.loc[valid].copy()

results = []
prediction_rows = []

for area in sorted(df[AREA].unique()):
    train = df.loc[df[AREA] != area]
    test = df.loc[df[AREA] == area]

    for name, target in TARGETS.items():

        global_mean = train[target].mean()

        code_means = train.groupby(CODE)[target].mean()

        pair_means = train.groupby(
            [CODE, RENTAL]
        )[target].mean()

        # Match test records to code/rental averages
        test_pairs = pd.MultiIndex.from_frame(
            test[[CODE, RENTAL]]
        )

        pair_pred = pd.Series(
            pair_means.reindex(test_pairs).to_numpy(),
            index=test.index
        )

        # Fallback: HCPCS mean, then global mean
        code_pred = test[CODE].map(code_means)

        prediction = (
            pair_pred.fillna(code_pred)
            .fillna(global_mean)
        )

        error = (test[target] - prediction).abs()

        results.append({
            "area": area,
            "target": name,
            "records": len(test),
            "MAE": mean_absolute_error(
                test[target], prediction
            ),
            "RMSE": np.sqrt(
                mean_squared_error(
                    test[target], prediction
                )
            ),
            "NMAE": error.mean() / test[target].mean()
        })

        prediction_rows.append(pd.DataFrame({
            "target": name,
            "actual": test[target].to_numpy(),
            "predicted": prediction.to_numpy()
        }))

results = pd.DataFrame(results)
predictions = pd.concat(prediction_rows, ignore_index=True)

print("\nRENTAL-AWARE RESULTS")

summary = []
for target, group in predictions.groupby("target"):
    area_rows = results[results["target"] == target]
    summary.append({
        "target": target,
        "MAE": mean_absolute_error(
            group["actual"], group["predicted"]
        ),
        "RMSE": np.sqrt(mean_squared_error(
            group["actual"], group["predicted"]
        )),
        "pooled_NMAE": (
            mean_absolute_error(
                group["actual"], group["predicted"]
            ) / group["actual"].mean()
        ),
        "worst_area_MAE": area_rows["MAE"].max()
    })

summary = pd.DataFrame(summary)
print(summary.to_string(index=False))

paired = results.pivot(
    index="area", columns="target", values=["MAE", "NMAE"]
)

paired.columns = [
    f"{metric}_{target}"
    for metric, target in paired.columns
]

print("\nAREAS WITH LOWER STANDARDIZED MAE:",
      (paired["MAE_Standardized"] < paired["MAE_Actual"]).sum())

print("AREAS WITH LOWER STANDARDIZED NMAE:",
      (paired["NMAE_Standardized"] < paired["NMAE_Actual"]).sum())

summary.to_csv(OUT / "rental_aware_summary.csv", index=False)
paired.to_csv(OUT / "rental_aware_by_area.csv")

print("\nLESSON 10 EXPERIMENT COMPLETED")

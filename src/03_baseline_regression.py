
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error

# 1. Project paths
ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT / "data" / "raw"
    / "Medicare_DME_Devices_Supplies_by_Geography_and_Service_2023.csv"
)

RESULTS_DIR = ROOT / "results" / "tables"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 2. Read the data
df = pd.read_csv(DATA_PATH, low_memory=False)

# 3. Use geographic categories labeled State
df = df.loc[
    df["Rfrg_Prvdr_Geo_Lvl"] == "State"
].copy()

target = "Avg_Suplr_Mdcr_Pymt_Amt"

# 4. Validate required fields
df[target] = pd.to_numeric(
    df[target], errors="coerce"
)

df = df.dropna(
    subset=[target, "HCPCS_Cd"]
).copy()

# 5. Random 80/20 split
train, test = train_test_split(
    df,
    test_size=0.20,
    random_state=42
)

print("TRAIN RECORDS:", len(train))
print("TEST RECORDS:", len(test))

# 6. Baseline A: global mean
global_mean = train[target].mean()

test = test.copy()
test["prediction_global"] = global_mean

# 7. Baseline B: HCPCS mean
code_means = train.groupby(
    "HCPCS_Cd"
)[target].mean()

test["prediction_hcpcs"] = (
    test["HCPCS_Cd"]
    .map(code_means)
    .fillna(global_mean)
)

# 8. Evaluate both models
def evaluate(name, actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(
        mean_squared_error(actual, predicted)
    )

    return {
        "model": name,
        "MAE": mae,
        "RMSE": rmse
    }

results = [
    evaluate(
        "Global mean",
        test[target],
        test["prediction_global"]
    ),
    evaluate(
        "HCPCS mean",
        test[target],
        test["prediction_hcpcs"]
    )
]

results_df = pd.DataFrame(results)

print("\nBASELINE RESULTS")
print(results_df.to_string(index=False))

# 9. Code coverage diagnostics
known_codes = test["HCPCS_Cd"].isin(
    code_means.index
)

print("\nTEST RECORDS WITH KNOWN HCPCS CODES")
print(int(known_codes.sum()))

print("\nTEST RECORDS WITH UNSEEN HCPCS CODES")
print(int((~known_codes).sum()))

# 10. Save reproducible results
results_df.to_csv(
    RESULTS_DIR / "baseline_random_split.csv",
    index=False
)

print("\nBASELINE EXPERIMENT COMPLETED")

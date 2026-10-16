
from pathlib import Path
import pandas as pd

# Locate the research project
ROOT = Path(__file__).resolve().parents[1]

# Specify the official CMS dataset
CSV_PATH = (
    ROOT
    / "data"
    / "raw"
    / "Medicare_DME_Devices_Supplies_by_Geography_and_Service_2023.csv"
)

# Load the dataset
df = pd.read_csv(CSV_PATH, low_memory=False)

print("=" * 60)
print("AAEC MEDICARE DME DATASET AUDIT")
print("=" * 60)

print("\n1. DATASET DIMENSIONS")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])

print("\n2. COLUMN NAMES")
for i, col in enumerate(df.columns, start=1):
    print(f"{i}. {col}")

print("\n3. FIRST FIVE RECORDS")
print(df.head().to_string())

print("\n4. MISSING VALUES")
missing = df.isna().sum().sort_values(ascending=False)
print(missing.to_string())

print("\n5. COLUMN DATA TYPES")
print(df.dtypes.to_string())

print("\n6. DUPLICATE ROWS")
print(df.duplicated().sum())

print("\n7. NUMERIC SUMMARY")
print(df.describe().to_string())

print("\nAUDIT COMPLETED")

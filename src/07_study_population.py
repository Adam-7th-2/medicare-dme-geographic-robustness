
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    ROOT / "data" / "raw"
    / "Medicare_DME_Devices_Supplies_by_Geography_and_Service_2023.csv"
)

OUTPUT_DIR = ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# The 50 U.S. states and Washington, DC
areas = """
Alabama
Alaska
Arizona
Arkansas
California
Colorado
Connecticut
Delaware
District of Columbia
Florida
Georgia
Hawaii
Idaho
Illinois
Indiana
Iowa
Kansas
Kentucky
Louisiana
Maine
Maryland
Massachusetts
Michigan
Minnesota
Mississippi
Missouri
Montana
Nebraska
Nevada
New Hampshire
New Jersey
New Mexico
New York
North Carolina
North Dakota
Ohio
Oklahoma
Oregon
Pennsylvania
Rhode Island
South Carolina
South Dakota
Tennessee
Texas
Utah
Vermont
Virginia
Washington
West Virginia
Wisconsin
Wyoming
"""

study_areas = set(areas.strip().splitlines())

assert len(study_areas) == 51

df = pd.read_csv(DATA_PATH, low_memory=False)

state_df = df.loc[
    df["Rfrg_Prvdr_Geo_Lvl"] == "State"
].copy()

study_df = state_df.loc[
    state_df["Rfrg_Prvdr_Geo_Desc"].isin(study_areas)
].copy()

observed_areas = set(
    study_df["Rfrg_Prvdr_Geo_Desc"].unique()
)

assert observed_areas == study_areas, (
    "Some requested geographic areas are missing."
)

print("ORIGINAL RECORDS:", len(df))
print("ALL STATE-LEVEL RECORDS:", len(state_df))
print("MAIN STUDY RECORDS:", len(study_df))
print("MAIN STUDY AREAS:", len(observed_areas))
print("EXCLUDED STATE-LEVEL RECORDS:",
      len(state_df) - len(study_df))

print("UNIQUE HCPCS CODES:",
      study_df["HCPCS_Cd"].nunique())

target = "Avg_Suplr_Mdcr_Pymt_Amt"

print("\nMAIN STUDY PAYMENT SUMMARY")
print(study_df[target].describe())

output = OUTPUT_DIR / "medicare_dme_2023_51_areas.csv"

study_df.to_csv(output, index=False)

print("\nSAVED:", output)
print("STUDY POPULATION CHECK COMPLETED")

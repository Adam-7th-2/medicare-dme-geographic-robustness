
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

DATA = (
    ROOT / "results" / "tables"
    / "hcpcs_geographic_cv_comparison.csv"
)

FIGURES = ROOT / "results" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA)

# Each point represents one HCPCS/rental group
fig, ax = plt.subplots(figsize=(7, 6))

ax.scatter(
    df["CV_actual"],
    df["CV_standardized"],
    alpha=0.35,
    s=15
)

# Equality line: points below it have lower
# standardized geographic variation
limit = max(
    df["CV_actual"].max(),
    df["CV_standardized"].max()
)

ax.plot(
    [0, limit],
    [0, limit],
    linestyle="--",
    color="black",
    linewidth=1
)

ax.set_xlim(0, limit * 1.03)
ax.set_ylim(0, limit * 1.03)

ax.set_xlabel("Observed-payment CV")
ax.set_ylabel("Standardized-payment CV")
ax.set_title("Geographic variation before and after standardization")

fig.tight_layout()

fig.savefig(
    FIGURES / "standardization_cv_comparison.pdf"
)

plt.close(fig)

print("GROUPS:", len(df))
print("FIGURE CREATED SUCCESSFULLY")

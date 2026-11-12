"""Central place for paths and settings (change here, not in 10 files)."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"

# Priority order: real UCI file first, then the sample file.
RAW_CANDIDATES = [
    DATA_DIR / "Online Retail.xlsx",
    DATA_DIR / "online_retail.csv",
    DATA_DIR / "online_retail_sample.csv",
]

# Colours used in all charts, so the project looks consistent
SEGMENT_COLORS = {
    "Champions": "#1b9e77",
    "Loyal Customers": "#66a61e",
    "Potential Loyalists": "#7570b3",
    "New Customers": "#1f78b4",
    "Need Attention": "#e6ab02",
    "At Risk": "#d95f02",
    "Cannot Lose Them": "#e7298a",
    "Hibernating": "#999999",
}
SEGMENT_ORDER = list(SEGMENT_COLORS.keys())

"""
rfm_pipeline.py
---------------
Reusable functions for the RFM customer segmentation project.

Run from the project root:
    python src/rfm_pipeline.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent))
from config import OUTPUT_DIR, RAW_CANDIDATES  # noqa: E402


# ----------------------------------------------------------------------
# 1. LOAD
# ----------------------------------------------------------------------
def load_data(path=None) -> pd.DataFrame:
    """Load the raw dataset (xlsx or csv). Picks the first file that exists."""
    if path is None:
        path = next((p for p in RAW_CANDIDATES if p.exists()), None)
        if path is None:
            raise FileNotFoundError("No dataset found in /data. See data/README.md")
    path = Path(path)
    print(f"Loading: {path.name}")
    if path.suffix.lower() == ".xlsx":
        df = pd.read_excel(path, dtype={"InvoiceNo": str, "StockCode": str})
    else:
        df = pd.read_csv(path, dtype={"InvoiceNo": str, "StockCode": str},
                         parse_dates=["InvoiceDate"], encoding="ISO-8859-1")
    return df


# ----------------------------------------------------------------------
# 2. CLEAN
# ----------------------------------------------------------------------
def clean_data(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Return a clean copy and print how many rows each step removed."""
    df = df.copy()
    log = [("Raw rows", len(df))]

    df = df.drop_duplicates()
    log.append(("After removing duplicates", len(df)))

    df = df.dropna(subset=["CustomerID"])
    log.append(("After dropping missing CustomerID", len(df)))

    df = df[~df["InvoiceNo"].astype(str).str.upper().str.startswith("C")]
    log.append(("After removing cancelled invoices (C...)", len(df)))

    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    log.append(("After removing Quantity<=0 / Price<=0", len(df)))

    # Non-product codes: postage, manual adjustments, bank charges ...
    non_product = r"^(POST|D|M|DOT|BANK CHARGES|C2|CRUK|S|AMAZONFEE)$"
    df = df[~df["StockCode"].astype(str).str.upper().str.match(non_product)]
    log.append(("After removing non-product StockCodes", len(df)))

    df["CustomerID"] = df["CustomerID"].astype(int)
    df["Description"] = df["Description"].fillna("UNKNOWN").str.strip().str.upper()
    df["TotalSales"] = (df["Quantity"] * df["UnitPrice"]).round(2)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["InvoiceMonth"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    df["InvoiceDay"] = df["InvoiceDate"].dt.date          # used for the Power BI date relationship

    if verbose:
        print("\nCLEANING LOG")
        for step, n in log:
            print(f"  {step:<45}{n:>10,}")
        print(f"  {'FINAL clean rows':<45}{len(df):>10,}")
    return df.reset_index(drop=True)


# ----------------------------------------------------------------------
# 3. RFM
# ----------------------------------------------------------------------
def calculate_rfm(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Timestamp]:
    """One row per customer: Recency (days), Frequency (orders), Monetary (money)."""
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("TotalSales", "sum"),
    )
    rfm["Monetary"] = rfm["Monetary"].round(2)
    return rfm.reset_index(), snapshot_date


def score_rfm(rfm: pd.DataFrame) -> pd.DataFrame:
    """Score each metric 1-5 (5 = best)."""
    rfm = rfm.copy()
    # Recency: SMALLER is better, so labels are reversed (5 -> 1)
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    # Frequency has many ties (lots of 1-order customers) -> rank first, else qcut fails
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5,
                             labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_Score"] = (rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str)
                        + rfm["M_Score"].astype(str))
    rfm["RFM_Total"] = rfm[["R_Score", "F_Score", "M_Score"]].sum(axis=1)
    return rfm


def assign_segment(r: int, f: int) -> str:
    """Business rules. Rules are checked top to bottom; first match wins."""
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 4 and f == 1:
        return "New Customers"
    if r >= 3 and f >= 3 and not (r == 3 and f == 3):
        return "Loyal Customers"
    if r == 3:
        return "Need Attention"
    if r >= 4:                       # r is 4-5 and f is 2
        return "Potential Loyalists"
    if f == 5:                       # r is 1-2
        return "Cannot Lose Them"
    if f >= 3:
        return "At Risk"
    return "Hibernating"


def segment_customers(rfm: pd.DataFrame) -> pd.DataFrame:
    rfm = rfm.copy()
    rfm["Segment"] = [assign_segment(r, f) for r, f in zip(rfm["R_Score"], rfm["F_Score"])]
    return rfm


def segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """Customers, revenue and averages per segment."""
    s = rfm.groupby("Segment").agg(
        Customers=("CustomerID", "count"),
        Avg_Recency=("Recency", "mean"),
        Avg_Frequency=("Frequency", "mean"),
        Avg_Monetary=("Monetary", "mean"),
        Total_Revenue=("Monetary", "sum"),
    ).round(1)
    s["Customer_%"] = (s["Customers"] / s["Customers"].sum() * 100).round(1)
    s["Revenue_%"] = (s["Total_Revenue"] / s["Total_Revenue"].sum() * 100).round(1)
    return s.sort_values("Total_Revenue", ascending=False)


# ----------------------------------------------------------------------
# 4. MAIN
# ----------------------------------------------------------------------
def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    raw = load_data()
    clean = clean_data(raw)
    rfm, snapshot = calculate_rfm(clean)
    rfm = segment_customers(score_rfm(rfm))
    summary = segment_summary(rfm)

    country = clean.groupby("CustomerID")["Country"].agg(lambda x: x.mode().iat[0])
    rfm = rfm.merge(country.rename("Country"), on="CustomerID")

    clean.to_csv(OUTPUT_DIR / "clean_transactions.csv", index=False)
    rfm.to_csv(OUTPUT_DIR / "rfm_customers.csv", index=False)
    summary.to_csv(OUTPUT_DIR / "segment_summary.csv")

    print(f"\nSnapshot date used for Recency: {snapshot.date()}")
    print(f"Customers: {len(rfm):,} | Revenue: {clean['TotalSales'].sum():,.0f}")
    print("\nSEGMENT SUMMARY\n", summary)
    print(f"\nFiles saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

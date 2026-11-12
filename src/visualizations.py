"""
visualizations.py
-----------------
Creates the 6 professional charts and saves them to outputs/charts/.
Run AFTER rfm_pipeline.py:   python src/visualizations.py
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parent))
from config import CHART_DIR, OUTPUT_DIR, SEGMENT_COLORS, SEGMENT_ORDER  # noqa: E402

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.dpi": 110, "axes.titleweight": "bold", "axes.titlesize": 13})


def _save(fig, name):
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(CHART_DIR / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {name}")


def chart_customers_by_segment(rfm):
    counts = rfm["Segment"].value_counts().reindex(SEGMENT_ORDER)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(x=counts.values, y=counts.index, hue=counts.index,
                palette=SEGMENT_COLORS, legend=False, ax=ax)
    for i, v in enumerate(counts.values):
        ax.text(v + 5, i, f"{v:,} ({v / counts.sum():.1%})", va="center")
    ax.set(title="Customer Count by Segment", xlabel="Number of customers", ylabel="")
    ax.set_xlim(0, counts.max() * 1.25)
    _save(fig, "01_customers_by_segment.png")


def chart_revenue_by_segment(rfm):
    rev = rfm.groupby("Segment")["Monetary"].sum().reindex(SEGMENT_ORDER)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(x=rev.index, y=rev.values, hue=rev.index, palette=SEGMENT_COLORS,
                legend=False, ax=ax)
    for i, v in enumerate(rev.values):
        ax.text(i, v, f"{v / rev.sum():.1%}", ha="center", va="bottom", fontsize=9)
    ax.set(title="Revenue Contribution by Segment", xlabel="", ylabel="Revenue")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x / 1e3:,.0f}K"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    _save(fig, "02_revenue_by_segment.png")


def chart_recency_vs_frequency(rfm):
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(data=rfm, x="Recency", y="Frequency", hue="Segment",
                    palette=SEGMENT_COLORS, hue_order=SEGMENT_ORDER,
                    size="Monetary", sizes=(15, 250), alpha=0.6, ax=ax)
    ax.set_yscale("log")
    ax.set(title="Recency vs Frequency (bubble size = Monetary)",
           xlabel="Recency (days since last purchase)", ylabel="Frequency (orders, log scale)")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    _save(fig, "03_recency_vs_frequency.png")


def chart_rfm_comparison(rfm):
    avg = rfm.groupby("Segment")[["R_Score", "F_Score", "M_Score"]].mean().reindex(SEGMENT_ORDER)
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.heatmap(avg, annot=True, fmt=".1f", cmap="YlGnBu", vmin=1, vmax=5,
                linewidths=.5, cbar_kws={"label": "Average score (1-5)"}, ax=ax)
    ax.set(title="Average R, F, M Score by Segment", xlabel="", ylabel="")
    _save(fig, "04_rfm_score_comparison.png")


def chart_top10_customers(rfm):
    top = rfm.nlargest(10, "Monetary").copy()
    top["CustomerID"] = top["CustomerID"].astype(str)
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(data=top, x="Monetary", y="CustomerID", hue="Segment",
                palette=SEGMENT_COLORS, dodge=False, ax=ax)
    for i, v in enumerate(top["Monetary"]):
        ax.text(v, i, f" {v:,.0f}", va="center", fontsize=9)
    ax.set(title="Top 10 Customers by Spending", xlabel="Total spend", ylabel="Customer ID")
    ax.set_xlim(0, top["Monetary"].max() * 1.15)
    ax.legend(title="Segment", fontsize=8)
    _save(fig, "05_top10_customers.png")


def chart_monthly_sales(clean):
    monthly = clean.groupby("InvoiceMonth")["TotalSales"].sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly.index, monthly.values, marker="o", lw=2.5, color="#1f78b4")
    ax.fill_between(monthly.index, monthly.values, alpha=0.15, color="#1f78b4")
    peak = monthly.idxmax()
    ax.annotate(f"Peak: {peak}", (peak, monthly.max()), xytext=(0, 12),
                textcoords="offset points", ha="center", fontweight="bold")
    ax.set(title="Monthly Sales Trend", xlabel="Month", ylabel="Revenue")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x / 1e3:,.0f}K"))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    _save(fig, "06_monthly_sales_trend.png")


def main():
    rfm = pd.read_csv(OUTPUT_DIR / "rfm_customers.csv")
    clean = pd.read_csv(OUTPUT_DIR / "clean_transactions.csv")
    chart_customers_by_segment(rfm)
    chart_revenue_by_segment(rfm)
    chart_recency_vs_frequency(rfm)
    chart_rfm_comparison(rfm)
    chart_top10_customers(rfm)
    chart_monthly_sales(clean)


if __name__ == "__main__":
    main()

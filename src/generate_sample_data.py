"""
generate_sample_data.py
-----------------------
Creates a realistic e-commerce dataset in the SAME format as the UCI
"Online Retail" dataset (InvoiceNo, StockCode, Description, Quantity,
InvoiceDate, UnitPrice, CustomerID, Country).

Use this ONLY if you cannot download the real UCI file.
The data deliberately contains "dirty" records (cancellations, missing
CustomerID, duplicates, bad prices) so that you practise real cleaning.
"""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)

N_CUSTOMERS = 3000
START = pd.Timestamp("2010-12-01")
END = pd.Timestamp("2011-12-09")

# ---------- product catalogue ----------
adjectives = ["VINTAGE", "RETRO", "CERAMIC", "WOODEN", "GLASS", "PAINTED", "HANGING",
              "SCANDI", "ROSE", "BLUE", "GREEN", "RED", "SILVER", "LARGE", "MINI"]
nouns = ["MUG", "CANDLE HOLDER", "LUNCH BAG", "CAKE TIN", "PHOTO FRAME", "NOTEBOOK",
         "TEA SET", "STORAGE JAR", "DOORMAT", "BUNTING", "CUSHION COVER", "LANTERN",
         "BOTTLE", "TRAY", "CLOCK", "HEART DECORATION", "PENCIL SET", "WRAP SET"]
products = []
for i in range(220):
    desc = f"{rng.choice(adjectives)} {rng.choice(nouns)}"
    price = float(np.round(rng.choice([0.42, 0.65, 0.85, 1.25, 1.65, 2.10, 2.95,
                                       3.75, 4.95, 6.95, 9.95, 12.75, 16.95]), 2))
    products.append((str(10000 + i * 7), desc, price))
products = pd.DataFrame(products, columns=["StockCode", "Description", "UnitPrice"])

countries = ["United Kingdom", "Germany", "France", "EIRE", "Spain", "Netherlands",
             "Belgium", "Switzerland", "Portugal", "Australia"]
c_probs = [0.85, 0.04, 0.03, 0.02, 0.015, 0.015, 0.01, 0.01, 0.005, 0.005]

# (name, share, n_orders range, first-order window (days from START), last-order window (days before END))
archetypes = [
    ("champion", 0.10, (12, 30), (0, 120), (0, 20)),
    ("loyal",    0.15, (6, 14),  (0, 200), (0, 60)),
    ("new",      0.15, (1, 2),   (300, 360), (0, 30)),
    ("promising",0.15, (2, 4),   (150, 330), (0, 90)),
    ("at_risk",  0.12, (5, 12),  (0, 120), (120, 220)),
    ("lost",     0.18, (1, 3),   (0, 200), (200, 360)),
    ("big_sleeper", 0.05, (15, 30), (0, 60), (150, 250)),
    ("one_off",  0.10, (1, 1),   (0, 360), (0, 360)),
]
shares = np.array([a[1] for a in archetypes]); shares = shares / shares.sum()
total_days = (END - START).days

rows = []
invoice_no = 536365
for cid in range(12347, 12347 + N_CUSTOMERS):
    arch = archetypes[rng.choice(len(archetypes), p=shares)]
    _, _, (o_min, o_max), (f_lo, f_hi), (l_lo, l_hi) = arch
    n_orders = int(rng.integers(o_min, o_max + 1))
    country = rng.choice(countries, p=c_probs)
    first_day = int(rng.integers(f_lo, f_hi + 1))
    last_day = total_days - int(rng.integers(l_lo, l_hi + 1))
    last_day = max(last_day, first_day)
    if arch[0] == "one_off":
        days = [int(rng.integers(0, total_days))]
    else:
        days = sorted(rng.integers(first_day, last_day + 1, size=n_orders).tolist())
    spend_level = rng.lognormal(mean=0.0, sigma=0.5)
    for d in days:
        invoice_no += 1
        order_dt = START + pd.Timedelta(days=int(d), hours=int(rng.integers(8, 18)),
                                        minutes=int(rng.integers(0, 60)))
        n_lines = max(1, int(rng.poisson(5 * spend_level)) + 1)
        items = products.sample(n=min(n_lines, 25), random_state=int(rng.integers(0, 10**9)))
        for _, p in items.iterrows():
            qty = int(rng.choice([1, 2, 3, 4, 6, 8, 12, 24], p=[.2, .2, .15, .15, .12, .08, .07, .03]))
            rows.append([str(invoice_no), p.StockCode, p.Description, qty,
                         order_dt, p.UnitPrice, float(cid), country])

df = pd.DataFrame(rows, columns=["InvoiceNo", "StockCode", "Description", "Quantity",
                                 "InvoiceDate", "UnitPrice", "CustomerID", "Country"])

# ---------- inject real-world dirt ----------
n = len(df)
cancel_idx = rng.choice(n, size=int(0.02 * n), replace=False)          # cancellations
df.loc[cancel_idx, "InvoiceNo"] = "C" + df.loc[cancel_idx, "InvoiceNo"]
df.loc[cancel_idx, "Quantity"] = -df.loc[cancel_idx, "Quantity"]
miss_idx = rng.choice(n, size=int(0.15 * n), replace=False)             # guest checkouts
df.loc[miss_idx, "CustomerID"] = np.nan
desc_idx = rng.choice(n, size=int(0.005 * n), replace=False)            # missing descriptions
df.loc[desc_idx, "Description"] = np.nan
bad_q = rng.choice(n, size=40, replace=False); df.loc[bad_q, "Quantity"] = -rng.integers(1, 50, 40)
bad_p = rng.choice(n, size=25, replace=False); df.loc[bad_p, "UnitPrice"] = 0.0
nonprod = rng.choice(n, size=60, replace=False)                         # non-product codes
df.loc[nonprod, "StockCode"] = rng.choice(["POST", "D", "M", "BANK CHARGES"], 60)
dups = df.sample(n=int(0.01 * n), random_state=1)                       # exact duplicates
df = pd.concat([df, dups], ignore_index=True)
df = df.sort_values("InvoiceDate", kind="stable").reset_index(drop=True)

out = Path(__file__).resolve().parents[1] / "data" / "online_retail_sample.csv"
out.parent.mkdir(exist_ok=True)
df.to_csv(out, index=False, date_format="%Y-%m-%d %H:%M:%S")
print(f"Saved {len(df):,} rows -> {out}")

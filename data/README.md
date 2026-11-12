# Dataset

## Option A – Real dataset (recommended for your resume)
**UCI Online Retail** – ~541,909 transactions of a UK online gift shop, 01-Dec-2010 to 09-Dec-2011.

1. Open: https://archive.ics.uci.edu/dataset/352/online+retail
2. Click **Download** → unzip → you get `Online Retail.xlsx`.
3. Copy it into this `data/` folder (keep the name `Online Retail.xlsx`).
   - Alternative: the same data is on Kaggle ("Online Retail" / "E-Commerce Data").
4. Run `python src/rfm_pipeline.py` – it automatically prefers the real file.

> Real file loads in ~30-60 seconds because it is Excel. Tip: open it once and *Save As* CSV named `online_retail.csv` (encoding ISO-8859-1 / Windows-1252 is handled) for faster loading.

## Option B – Included sample dataset
`online_retail_sample.csv` (138k rows, 3,000 customers) has the **same columns** and the same kind of dirt (cancellations, missing CustomerID, duplicates, zero prices). It is *synthetic*: use it to learn and for testing. Regenerate with:
```
python src/generate_sample_data.py
```
Be honest in interviews: say the demo numbers come from a simulated dataset and that the code is tested on the UCI structure.

## Columns
| Column | Type | Description |
|---|---|---|
| InvoiceNo | text | 6-digit order id; prefix **C** = cancellation |
| StockCode | text | product code (POST, M, D … are non-products) |
| Description | text | product name |
| Quantity | int | units per line (negative = return) |
| InvoiceDate | datetime | order timestamp |
| UnitPrice | float | price per unit (GBP) |
| CustomerID | float | 5-digit customer id (≈25 % missing in real data) |
| Country | text | customer country |

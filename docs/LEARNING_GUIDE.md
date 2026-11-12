# Learning Guide – how to study this project (Fresher friendly)

Work in this order. Finish each step and its practice questions before moving on.

| Step | Where | What you learn | Time |
|---|---|---|---|
| 1 | Notebook Step 1-2 | Libraries, loading data, `head/info/describe` | 1 h |
| 2 | Notebook Step 3-4 | Data quality + cleaning, cleaning log | 1.5 h |
| 3 | Notebook Step 5-7 | Total sales, KPIs, EDA, customer behaviour, Pareto | 2 h |
| 4 | Notebook Step 8-9 | Recency/Frequency/Monetary, `qcut` scoring | 2 h |
| 5 | Notebook Step 10-11 | Segmentation rules, business insights | 1.5 h |
| 6 | Notebook Step 12-13 | Six charts, exports | 1.5 h |
| 7 | `sql/01` → `sql/03` | MySQL load, clean view, KPIs, CTE, window functions, RFM in SQL | 3 h |
| 8 | `power_bi/POWER_BI_GUIDE.md` | Model, DAX, 6 visuals, slicers | 3 h |
| 9 | `src/*.py` | Move notebook code into reusable functions | 1.5 h |
| 10 | `docs/GITHUB_RESUME_LINKEDIN.md` | GitHub, resume, LinkedIn | 1 h |
| 11 | `docs/INTERVIEW_QA.md` | Practise explaining aloud | 1 h |

## Practice answers (check after trying yourself)
- P1a `np.__version__`; P1b `as pd` gives a short nickname.
- P2: `df["Country"].nunique()`, `df["InvoiceDate"].agg(["min","max"])`, `df["StockCode"].nunique()`.
- P3: `df[df.CustomerID.isnull()].eval("Quantity*UnitPrice").sum()` (after removing cancellations for a fair number).
- P4: `len(clean) / len(df) * 100`.
- P5: `total_revenue / total_customers`; it is bigger than AOV when customers place more than one order.
- P7: `(cust.Orders == 1).sum()` and `cust[cust.Orders == 1].Spend.sum()`.
- P8: `rfm.loc[rfm.Recency.idxmin()]`, `rfm.loc[rfm.Monetary.idxmax()]`; `count()` counts lines, `nunique()` counts orders.
- P9: 555 = bought very recently, very often, spent most; 111 = long ago, rarely, spent little. Recency labels reversed because fewer days = better.
- P10: R5,F1 → New Customers; R2,F5 → Cannot Lose Them (call personally).

## Telugu-English cheat sheet
- **Recency** = last ga ela eppudu konnaru (ఇటీవల ఎప్పుడు)
- **Frequency** = entha sarlu konnaru (ఎన్నిసార్లు)
- **Monetary** = entha kharchu chesaru (ఎంత ఖర్చు)
- **Cleaning** = tappu/duplicate data tholaginchadam
- **Segment** = similar customers ni oka group ga cheyyadam
- **Snapshot date** = analysis kosam "ee roju" ani anukune date

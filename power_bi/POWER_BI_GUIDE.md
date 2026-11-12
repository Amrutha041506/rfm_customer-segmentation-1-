# Power BI Dashboard – Step-by-Step Guide

Time needed: about 90 minutes. Software: Power BI Desktop (free, Windows).

## STEP 0 – Files you need (already created by the Python pipeline)
| File | Purpose |
|---|---|
| `outputs/clean_transactions.csv` | fact table – one row per product line |
| `outputs/rfm_customers.csv` | customer table – R, F, M, scores, Segment |

(Run `python src/rfm_pipeline.py` first if these do not exist.)

## STEP 1 – Load data
1. Open Power BI Desktop → **Home → Get data → Text/CSV**.
2. Select `clean_transactions.csv` → **Transform Data** (opens Power Query).
3. Check data types: `InvoiceDate` = Date/Time, `Quantity` = Whole number, `UnitPrice` & `TotalSales` = Fixed decimal number, `CustomerID` = **Text** (IDs are labels, not numbers to add!), `InvoiceNo` = Text.
4. **Home → Close & Apply**.
5. Repeat for `rfm_customers.csv` (`CustomerID` = Text, scores = Whole number, `Monetary` = Fixed decimal).

*Telugu-English: CustomerID ni Text ga pettali – numbers ga unte Power BI sum chese pramadam undi.*

## STEP 2 – Create the Date table
1. **Modeling → New table** → paste the `DateTable` code from `dax_measures.dax`.
2. Select DateTable → **Table tools → Mark as date table** → column `Date`.
3. Select the `Month` column → **Column tools → Sort by column → Month Sort** (so Jan, Feb … order is correct).
4. `clean_transactions.csv` already contains an `InvoiceDay` column (date only). In Power Query set its type to **Date**. We use it to link to the DateTable.

## STEP 3 – Build relationships (Model view)
Drag to create:
- `rfm_customers[CustomerID]` **1 → \*** `clean_transactions[CustomerID]` (single direction: rfm_customers filters transactions)
- `DateTable[Date]` **1 → \*** `clean_transactions[InvoiceDay]`

Result = a small **star schema** (one fact, two dimensions). Interviewers love hearing this term.

## STEP 4 – Add the measures
Paste all measures from `dax_measures.dax` (Home → New measure). Also add the calculated column `Segment Sort` to `rfm_customers`, then select `Segment` → **Sort by column → Segment Sort**.

## STEP 5 – Build the report page (canvas 16:9)
Set **View → Page view → Fit to page**, and use a dark-blue header strip with title *“Customer Segmentation – RFM Dashboard”*.

### 5.1 KPI cards (top row)
| Visual | Field |
|---|---|
| Card | `Total Customers` |
| Card | `Total Revenue` (format: $, no decimals; Display units: Thousands) |
| Card | `Average Order Value` (2 decimals) |
| Card (optional) | `At Risk Customers` |

Format → Visual → *Callout value* font 28, *Category label* on.

### 5.2 Customer Segment Distribution – Donut chart
- Legend: `rfm_customers[Segment]`
- Values: `Segment Customers`
- Details labels: *Category, percent of total*.
- Colours: Format → Slices → set per segment (Champions green, At Risk orange, Hibernating grey…).
**Why:** shows how the customer base is split.

### 5.3 Revenue by Customer Segment – Clustered bar chart
- Y-axis: `Segment`; X-axis: `Segment Revenue`; Tooltips: `Revenue % of Total`.
- Sort by `Segment Revenue` descending (… menu → Sort axis).
**Why:** reveals the Pareto effect – a few segments produce most money.

### 5.4 Customer Purchase Behavior – Scatter chart
- X-axis: `Avg Recency (Days)`; Y-axis: `Avg Frequency`; Size: `Segment Revenue`; Legend/Details: `Segment`.
**Why:** one bubble per segment; bottom-left = bad, top-left = champions.
Extra: add a **Table** visual: `Segment`, `Segment Customers`, `Avg Recency (Days)`, `Avg Frequency`, `Avg Monetary` with conditional-format data bars.

### 5.5 Monthly Revenue Trend – Line and clustered column chart
- X-axis: `DateTable[Month]`; Column values: `Total Revenue`; Line values: `Total Customers` (secondary axis) *or* `Revenue MoM %`.
**Why:** seasonality (find the peak month in YOUR data – real UCI data peaks in November), growth, and customer activity. Note: first and last months are partial, so mention that when presenting.

### 5.6 Interactive slicers
| Slicer | Field | Style |
|---|---|---|
| Segment | `rfm_customers[Segment]` | Tile / list, multi-select |
| Country | `clean_transactions[Country]` | Dropdown, with search |
| Month | `DateTable[Month]` | Between / list |
| (optional) RFM_Total | `rfm_customers[RFM_Total]` | Between (range slider) |

Use **View → Sync slicers** if you build a second page.

## STEP 6 – Polish
- Align with **Format → Align/Distribute**. Keep 3 colours + segment colours only.
- Add a text box: *“Insight: Champions are ~18 % of customers but ~42 % of revenue (sample data).”* (Check your own numbers!)
- Edit interactions (**Format → Edit interactions**) so the donut does not filter the KPI cards if you want fixed totals.
- Page 2 (optional): **At-Risk Action List** – Table with `CustomerID, Segment, Recency, Frequency, Monetary`, filtered to At Risk + Cannot Lose Them, sorted by Monetary.
- Add **bookmarks** + a *Reset filters* button (Insert → Buttons → Bookmark).

## STEP 7 – Save and export
Save as `power_bi/RFM_Customer_Segmentation.pbix`, then **File → Export → PDF** and take a screenshot to `outputs/dashboard_screenshot.png` for your README.

## Common errors
| Problem | Fix |
|---|---|
| KPI cards ignore the Segment slicer | Check relationship direction rfm_customers → clean_transactions |
| Months appear alphabetical | Set *Sort by column* → `Month Sort` |
| Total Customers looks too large | `CustomerID` must be Text and the measure must be DISTINCTCOUNT |
| Revenue differs from Python | Make sure you loaded the *clean* file, not the raw data |

# GitHub upload, Resume bullets, LinkedIn description

## A. Upload to GitHub (first time)
1. Install Git: https://git-scm.com/downloads . Create a free account at github.com.
2. On GitHub: **New repository** → name `rfm-customer-segmentation` → Public → **do not** tick "Add README" → Create.
3. Open a terminal inside the project folder and run:
```bash
git init
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
git add .
git commit -m "Initial commit: RFM customer segmentation project"
git branch -M main
git remote add origin https://github.com/<your-username>/rfm-customer-segmentation.git
git push -u origin main
```
4. Refresh the GitHub page – the README with charts should show.
5. Add *About* description + topics: `data-analysis rfm customer-segmentation python sql power-bi pandas`.
6. Put a screenshot of your Power BI dashboard in `outputs/dashboard_screenshot.png`, add it to README, then:
```bash
git add . && git commit -m "Add dashboard screenshot" && git push
```
Tips: commit small and often; never upload passwords; the `.pbix` file (usually < 25 MB) is fine to upload.

## B. Resume bullets (choose 3-4, replace numbers with YOUR results)
- Built an end-to-end **RFM customer segmentation** project on 540K+ e-commerce transactions using **Python (Pandas, NumPy), MySQL and Power BI**, grouping customers into 8 behavioural segments.
- Cleaned and validated transaction data (duplicates, cancelled invoices, missing IDs, invalid values) and engineered Recency, Frequency and Monetary features with quintile scoring.
- Identified that **Champions (~18% of customers) drive ~42% of revenue** and that **At Risk / Cannot-Lose customers hold ~31% of revenue**, enabling prioritised retention campaigns.
- Wrote **MySQL** queries with CTEs and window functions (NTILE, LAG) for revenue trends, lifetime value and at-risk lists; designed an interactive **Power BI** dashboard with **DAX** measures (AOV, revenue share, MoM growth) and slicers.

## C. LinkedIn project description
**Customer Segmentation Analysis using RFM | Python · SQL · Power BI**

I analysed e-commerce purchase data to answer a simple business question: *which customers should we reward, retain or win back?*

▪ Cleaned 540K+ transactions and calculated Recency, Frequency and Monetary value for every customer
▪ Scored customers 1–5 and created 8 segments (Champions, Loyal, At Risk, Cannot Lose Them, Hibernating and more)
▪ Found that a small group of Champions generates a very large share of revenue, while valuable at-risk customers are slipping away
▪ Reproduced the logic in MySQL and built an interactive Power BI dashboard with DAX KPIs and slicers

Tools: Python, Pandas, NumPy, Matplotlib, Seaborn, MySQL, Power BI, Jupyter, GitHub
🔗 GitHub: <your link>   #DataAnalytics #Python #SQL #PowerBI #RFM

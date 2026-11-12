# Interview Questions on This Project

**1. What is RFM?** Recency = days since last purchase, Frequency = number of orders, Monetary = total spend. A simple, explainable way to rank customer value.

**2. Why use a snapshot date and not today's date?** The data ends in Dec 2011. With today's date every customer looks inactive. Snapshot = last date + 1 day.

**3. Why reverse the Recency score?** Smaller recency days is better, so the smallest days must receive score 5.

**4. Why `rank(method="first")` before `qcut` on Frequency?** Many customers share the same frequency (e.g. 1 order); `qcut` needs unique bin edges, so ranking breaks ties.

**5. Why remove cancelled invoices?** They are returns, not purchases. (Advanced: you can instead net them against purchases; mention it as an alternative.)

**6. Why drop rows with missing CustomerID?** RFM is customer-level; guest orders cannot be attributed. I reported how much revenue this removed.

**7. Frequency: count rows or distinct invoices?** Distinct InvoiceNo – one order has many product lines.

**8. How did you define segments?** Rule-based on R and F scores (Monetary used for prioritisation inside segments). Alternative: K-Means.

**9. Difference between pandas `qcut` and SQL `NTILE`?** NTILE forces equal-size buckets even for ties; qcut works on value quantiles, so results differ slightly for tied values.

**10. What business actions come out of the analysis?** Champions → rewards/referrals; New → onboarding; At Risk / Cannot Lose → personalised win-back; Hibernating → low-cost or stop.

**11. What are the limitations?** No margin or category data, one-year window, equal weights for R/F/M, thresholds are judgement-based.

**12. Explain your Power BI model.** Star schema: `clean_transactions` fact, `rfm_customers` and `DateTable` dimensions, one-to-many relationships on CustomerID and Date.

**13. Difference between a measure and a calculated column?** Measure = calculated at query time and reacts to slicers (e.g. Total Revenue). Calculated column = stored per row at refresh (e.g. Segment Sort).

**14. How would you improve the project?** Add margin, use K-Means/CLV, churn prediction, A/B test the campaigns, automate refresh.

**15. Be honest about data:** If you used the sample data, say so and state that the pipeline also runs on the UCI file.

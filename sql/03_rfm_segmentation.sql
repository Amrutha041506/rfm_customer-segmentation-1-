-- =====================================================================
-- 03_rfm_segmentation.sql  (MySQL 8.0+)
-- Builds RFM metrics, scores (1-5 using NTILE), segments, and at-risk list.
-- NOTE: NTILE splits rows into equal-size buckets even when values tie, so
-- results can differ slightly from pandas qcut. This is normal - explain it
-- in interviews.
-- =====================================================================
USE rfm_project;

-- ---------------------------------------------------------------------
-- STEP 1: RFM metrics per customer
-- Snapshot date = day after the last transaction in the data
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS rfm_base;
CREATE VIEW rfm_base AS
SELECT CustomerID,
       DATEDIFF((SELECT DATE(MAX(InvoiceDate)) + INTERVAL 1 DAY FROM clean_transactions),
                MAX(InvoiceDate))          AS Recency,
       COUNT(DISTINCT InvoiceNo)           AS Frequency,
       ROUND(SUM(TotalSales), 2)           AS Monetary
FROM clean_transactions
GROUP BY CustomerID;

SELECT * FROM rfm_base ORDER BY Monetary DESC LIMIT 10;

-- ---------------------------------------------------------------------
-- STEP 2: Scores 1-5
--   Recency  : smaller days = better -> ORDER BY Recency DESC so recent customers get 5
--   Frequency: higher = better        -> ORDER BY Frequency ASC
--   Monetary : higher = better        -> ORDER BY Monetary ASC
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS rfm_scores;
CREATE VIEW rfm_scores AS
SELECT CustomerID, Recency, Frequency, Monetary,
       NTILE(5) OVER (ORDER BY Recency   DESC)              AS R_Score,
       NTILE(5) OVER (ORDER BY Frequency ASC, CustomerID)   AS F_Score,
       NTILE(5) OVER (ORDER BY Monetary  ASC)               AS M_Score
FROM rfm_base;

-- ---------------------------------------------------------------------
-- STEP 3: Segments (same business rules as Python)
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS rfm_segments;
CREATE VIEW rfm_segments AS
SELECT s.*,
       CONCAT(R_Score, F_Score, M_Score) AS RFM_Score,
       CASE
           WHEN R_Score >= 4 AND F_Score >= 4                                   THEN 'Champions'
           WHEN R_Score >= 4 AND F_Score = 1                                    THEN 'New Customers'
           WHEN R_Score >= 3 AND F_Score >= 3 AND NOT (R_Score = 3 AND F_Score = 3) THEN 'Loyal Customers'
           WHEN R_Score = 3                                                     THEN 'Need Attention'
           WHEN R_Score >= 4                                                    THEN 'Potential Loyalists'
           WHEN F_Score = 5                                                     THEN 'Cannot Lose Them'
           WHEN F_Score >= 3                                                    THEN 'At Risk'
           ELSE 'Hibernating'
       END AS Segment
FROM rfm_scores s;

-- ---------------------------------------------------------------------
-- STEP 4: Segment summary (customers, revenue, share)
-- ---------------------------------------------------------------------
SELECT Segment,
       COUNT(*)                                             AS customers,
       ROUND(AVG(Recency), 1)                               AS avg_recency,
       ROUND(AVG(Frequency), 1)                             AS avg_frequency,
       ROUND(AVG(Monetary), 1)                              AS avg_monetary,
       ROUND(SUM(Monetary), 0)                              AS revenue,
       ROUND(SUM(Monetary) / SUM(SUM(Monetary)) OVER () * 100, 1) AS revenue_pct
FROM rfm_segments
GROUP BY Segment
ORDER BY revenue DESC;

-- ---------------------------------------------------------------------
-- STEP 5: At-risk customer identification (campaign list)
-- High-value customers who have gone quiet. Sorted so the biggest
-- spenders are contacted first.
-- ---------------------------------------------------------------------
SELECT CustomerID, Segment, Recency AS days_since_last_order,
       Frequency AS orders, Monetary AS lifetime_spend
FROM rfm_segments
WHERE Segment IN ('At Risk', 'Cannot Lose Them')
ORDER BY Monetary DESC
LIMIT 50;

-- Alternative rule-based version (no scoring needed):
-- "Bought 3+ times, spent above average, but silent for more than 120 days"
SELECT CustomerID, Recency, Frequency, Monetary
FROM rfm_base
WHERE Frequency >= 3
  AND Monetary > (SELECT AVG(Monetary) FROM rfm_base)
  AND Recency  > 120
ORDER BY Monetary DESC;

-- =====================================================================
-- 02_business_analysis.sql  (MySQL 8.0+)  -- all queries use the clean view
-- =====================================================================
USE rfm_project;

-- Q1. Total revenue
SELECT ROUND(SUM(TotalSales), 2) AS total_revenue
FROM clean_transactions;

-- Q2. Total customers
SELECT COUNT(DISTINCT CustomerID) AS total_customers
FROM clean_transactions;

-- Q3. Total orders and Average Order Value (AOV)
SELECT COUNT(DISTINCT InvoiceNo)                                        AS total_orders,
       ROUND(SUM(TotalSales) / COUNT(DISTINCT InvoiceNo), 2)            AS avg_order_value
FROM clean_transactions;

-- Q4. Top 10 customers by spending
SELECT CustomerID,
       ROUND(SUM(TotalSales), 2)   AS total_spent,
       COUNT(DISTINCT InvoiceNo)   AS orders
FROM clean_transactions
GROUP BY CustomerID
ORDER BY total_spent DESC
LIMIT 10;

-- Q5. Customer purchase frequency (orders per customer) + distribution
SELECT CustomerID, COUNT(DISTINCT InvoiceNo) AS purchase_frequency
FROM clean_transactions
GROUP BY CustomerID
ORDER BY purchase_frequency DESC;

SELECT purchase_frequency, COUNT(*) AS customers
FROM (
    SELECT CustomerID, COUNT(DISTINCT InvoiceNo) AS purchase_frequency
    FROM clean_transactions GROUP BY CustomerID
) t
GROUP BY purchase_frequency
ORDER BY purchase_frequency;

-- Q6. Customer lifetime spending (CLV so far) with first/last purchase and active days
SELECT CustomerID,
       MIN(InvoiceDate)                              AS first_purchase,
       MAX(InvoiceDate)                              AS last_purchase,
       DATEDIFF(MAX(InvoiceDate), MIN(InvoiceDate))  AS active_days,
       COUNT(DISTINCT InvoiceNo)                     AS orders,
       ROUND(SUM(TotalSales), 2)                     AS lifetime_spend,
       ROUND(SUM(TotalSales) / COUNT(DISTINCT InvoiceNo), 2) AS avg_order_value
FROM clean_transactions
GROUP BY CustomerID
ORDER BY lifetime_spend DESC;

-- Q7. Monthly revenue trend with month-over-month growth % (window function LAG)
WITH monthly AS (
    SELECT DATE_FORMAT(InvoiceDate, '%Y-%m') AS ym,
           SUM(TotalSales)                    AS revenue,
           COUNT(DISTINCT CustomerID)         AS active_customers,
           COUNT(DISTINCT InvoiceNo)          AS orders
    FROM clean_transactions
    GROUP BY DATE_FORMAT(InvoiceDate, '%Y-%m')
)
SELECT ym,
       ROUND(revenue, 2) AS revenue,
       active_customers,
       orders,
       ROUND((revenue - LAG(revenue) OVER (ORDER BY ym))
             / LAG(revenue) OVER (ORDER BY ym) * 100, 1) AS mom_growth_pct
FROM monthly
ORDER BY ym;

-- Q8. Revenue by country
SELECT Country, ROUND(SUM(TotalSales),2) AS revenue, COUNT(DISTINCT CustomerID) AS customers
FROM clean_transactions
GROUP BY Country
ORDER BY revenue DESC;

-- Q9. Repeat vs one-time customers
SELECT CASE WHEN orders = 1 THEN 'One-time' ELSE 'Repeat' END AS customer_type,
       COUNT(*) AS customers
FROM (SELECT CustomerID, COUNT(DISTINCT InvoiceNo) AS orders
      FROM clean_transactions GROUP BY CustomerID) t
GROUP BY customer_type;

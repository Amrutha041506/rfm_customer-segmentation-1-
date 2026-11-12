-- =====================================================================
-- 01_create_database_and_load.sql   (MySQL 8.0+)
-- Creates the database, the raw table, and loads the CSV.
-- =====================================================================
CREATE DATABASE IF NOT EXISTS rfm_project;
USE rfm_project;

DROP TABLE IF EXISTS online_retail_raw;
CREATE TABLE online_retail_raw (
    InvoiceNo    VARCHAR(20),
    StockCode    VARCHAR(30),
    Description  VARCHAR(255),
    Quantity     INT,
    InvoiceDate  DATETIME,
    UnitPrice    DECIMAL(10,2),
    CustomerID   DECIMAL(10,1) NULL,   -- CSV stores 14441.0 ; NULL = guest checkout
    Country      VARCHAR(60)
);

-- Enable local file loading once (run as admin if you get error 3948 / 1148):
--   SET GLOBAL local_infile = 1;
-- Start the client with:  mysql --local-infile=1 -u root -p
-- Change the path below to YOUR file location (use forward slashes on Windows).
LOAD DATA LOCAL INFILE 'C:/path/to/rfm-customer-segmentation/data/online_retail_sample.csv'
INTO TABLE online_retail_raw
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(InvoiceNo, StockCode, @desc, Quantity, @invdate, UnitPrice, @cust, Country)
SET Description = NULLIF(@desc, ''),
    InvoiceDate = STR_TO_DATE(@invdate, '%Y-%m-%d %H:%i:%s'),
    CustomerID  = NULLIF(@cust, '');

-- Sanity check
SELECT COUNT(*) AS raw_rows FROM online_retail_raw;   -- expect 138,144 for the sample file

-- ---------------------------------------------------------------------
-- CLEAN VIEW: same rules as Python (no duplicates handled here: see note)
-- Note: exact duplicate rows are removed with SELECT DISTINCT.
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS clean_transactions;
CREATE VIEW clean_transactions AS
SELECT DISTINCT
       InvoiceNo,
       StockCode,
       COALESCE(Description, 'UNKNOWN')       AS Description,
       Quantity,
       InvoiceDate,
       UnitPrice,
       CAST(CustomerID AS UNSIGNED)           AS CustomerID,
       Country,
       ROUND(Quantity * UnitPrice, 2)         AS TotalSales
FROM online_retail_raw
WHERE CustomerID IS NOT NULL
  AND InvoiceNo NOT LIKE 'C%'
  AND Quantity  > 0
  AND UnitPrice > 0
  AND StockCode NOT IN ('POST','D','M','DOT','BANK CHARGES','C2','CRUK','S','AMAZONFEE');

SELECT COUNT(*) AS clean_rows FROM clean_transactions;  -- expect 113,840

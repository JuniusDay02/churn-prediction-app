create database Churn_db;
use churn_db;
create table customer_churn_data (
CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    Age INT,
    Gender INT,  -- 0 = Male, 1 = Female
    Tenure INT,
    MonthlyCharges FLOAT,
    ChurnPrediction INT DEFAULT NULL,  -- 0 = Not Churn, 1 = Churn
    Email VARCHAR(255));
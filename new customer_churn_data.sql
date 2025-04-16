
use churn_db;
create table customer_churn_data (
CustomerID INT PRIMARY KEY,
    Age INT,
    Gender VARCHAR(10),
    Tenure INT,
    MonthlyCharges FLOAT,
    ContractType VARCHAR(50),
    InternetService VARCHAR(50),
    TotalCharges FLOAT,
    TechSupport VARCHAR(10),
    Churn VARCHAR(10),
    Email VARCHAR(255),  
    ChurnPrediction INT 
    );
    
    desc customer_churn_data;
    
 select email from customer_churn_data;
 select * from customer_churn_data;
 
USE churn_db;

SELECT CustomerID, Age, Gender, MonthlyCharges, ChurnPrediction
FROM customer_churn_data
ORDER BY CustomerID;
SELECT CustomerID, ChurnPrediction,Email FROM customer_churn_data;

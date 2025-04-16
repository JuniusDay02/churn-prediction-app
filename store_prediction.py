import pandas as pd
import mysql.connector
import joblib
import numpy as np

model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")


#connecting to mysql

data_conn = mysql.connector.connect(
    host = "churndb.c1kio68symiq.ap-south-1.rds.amazonaws.com",
    user = "ChurnAdmin",
    password = "Churn_customer",
    database = "churn_db",
    port=3306
)

cursor = data_conn.cursor()

#reading data from sql
df = pd.read_sql("SELECT * FROM customer_churn_data", data_conn)

#preprocessing of the data
x = df[["Age", "Gender", "Tenure", "MonthlyCharges"]]
x["Gender"] = x["Gender"].apply(lambda g: 1 if g == "Female" else 0)
x_scaled = scaler.transform(x)

#PREDICTING
predictions = model.predict(x_scaled)
df["ChurnPrediction"] = predictions

# storing predictions in the Database 
for i, row in df.iterrows():
    cursor.execute(
        "UPDATE customer_churn_data SET ChurnPrediction = %s WHERE CustomerID = %s",
        (int(row["ChurnPrediction"]), int(row["CustomerID"]))
    )

data_conn.commit()
cursor.close()
data_conn.close()

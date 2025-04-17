import streamlit as st
import joblib
import numpy as np
import mysql.connector
from email.message import EmailMessage
import smtplib
import pandas as pd

scaler = joblib.load("scaler.pkl")
model = joblib.load("model.pkl")

st.title("Churn Prediction Application for VoiceMe Telecom services")

st.divider()
st.write("Please enter the values and hit predict for getting an prediction")
st.divider()

age = st.number_input("Enter age", min_value= 6, max_value= 150, value= 30)
tenure = st.number_input("Enter tenure (Months)", min_value= 0, max_value=30, value=10)
monthlycharge = st.number_input("Enter monthly Charge", min_value=30, max_value=150)
gender = st.selectbox("Enter your gender",["Male","Female"])

st.divider()
predictbutton = st.button("predict")
st.divider()

if predictbutton:
    gender_selected = 1 if gender == "Female" else 0
    x = [age, gender_selected, tenure, monthlycharge]
    x_scaled = scaler.transform([x])
    prediction = model.predict(x_scaled)[0]
    if prediction == 1:
        st.error("Customer is likely to churn ❌")
    else:
        st.success("Customer will stay ✅")



#prediction taken from DB
st.divider()
if st.button("Fetch from MySQL and Predict for All"):
    data_conn = mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        port=int(st.secrets["DB_PORT"])
    )

    df = pd.read_sql("SELECT * FROM customer_churn_data", data_conn)
    x_db = df[["Age", "Gender", "Tenure", "MonthlyCharges"]]
    x_db["Gender"] = x_db["Gender"].apply(lambda x: 1 if x == "Female" else 0)
    x_scaled = scaler.transform(x_db)
    predictions = model.predict(x_scaled)
    df["ChurnPrediction"] = predictions


    for i, row in df.iterrows():
        cursor = data_conn.cursor()
        cursor.execute( 
            "UPDATE customer_churn_data SET ChurnPrediction = %s WHERE CustomerID = %s",
            (int(row["ChurnPrediction"]), int(row["CustomerID"]))
        )
        cursor.close()


    data_conn.commit()
    data_conn.close()
    st.success("Predictions updated in Database")

#Sending automated emails to Churned Customers
# 
st.divider()
def send_email(to_email, name):
    msg = EmailMessage()
    msg['Subject'] = "We're sorry to see you go 😔"
    msg['From'] = st.secrets["EMAIL_ADDRESS"]
    msg['To'] = to_email

    msg.set_content(f"""Hi {name},
                    
We noticed you may be considering leaving VoiceMe Telecom. Before you decide, here's a special offer just for you:
Get 30% OFF on your next 3 months of service!    

Click here to redeem: https://voiceme-telecom.com/offer-retain                    
                    
Warm regards,  
The VoiceMe Telecom Team
""")
    msg.add_alternative(f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333;">Hi {name},</h2>
                <p style="font-size: 16px; color: #555;">
                    We noticed you may be considering leaving <strong>VoiceMe Telecom</strong>. Before you decide, here's a
                    <strong style="color: #d9534f;">special offer</strong> just for you:
                </p>
                <p style="font-size: 18px; font-weight: bold; color: #2c3e50;">🔥 Get 30% OFF on your next 3 months of service!</p>
                <p style="font-size: 16px; color: #555;">
                    This limited-time promotion is available only to selected customers.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://voiceme-telecom.com/offer-retain" style="background-color: #007BFF; color: white; padding: 12px 25px; border-radius: 5px; text-decoration: none; font-size: 16px;">
                        Redeem Your Offer 🎁
                    </a>
                </div>
                <p style="font-size: 14px; color: #888;">
                    We value your loyalty and hope to continue serving you with even better service ahead.<br><br>
                    Warm regards,<br>
                    <strong>The VoiceMe Telecom Team</strong>
                </p>
            </div>
        </body>
    </html>
    """, subtype='html')

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(st.secrets["EMAIL_ADDRESS"], st.secrets["EMAIL_PASSWORD"])
            smtp.send_message(msg)
    except Exception as e:
        st.warning(f"Email to {to_email} skipped. Reason:{e}")

if st.button("Send Emails to Predicted Churn Customers"):
    data_conn = mysql.connector.connect(
        host=st.secrets["DB_HOST"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"],
        database=st.secrets["DB_NAME"],
        port=int(st.secrets["DB_PORT"])
    )
    st.success("connected to MySQL successfully")
    churn_df = pd.read_sql("SELECT * FROM customer_churn_data WHERE ChurnPrediction = 1", data_conn)
    st.write("fetched rows:",df.shape[0])
    for i, row in churn_df.iterrows():
        if send_email(row["Email"], f"Customer {row['CustomerID']}"):
            st.session_state.emailed_customers.append({"CustomerID": row["CustomerID"], "Email": row["Email"]})



    data_conn.close()
    st.success("Promotional emails sent to churn customers.")

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="Malaysia Fuel Price Dashboard", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    weekly = pd.read_sql("SELECT * FROM fuel_prices ORDER BY price_date", conn)
    monthly = pd.read_sql("SELECT * FROM fuel_prices_monthly ORDER BY month", conn)
    conn.close()
    return weekly, monthly

weekly, monthly = load_data()

st.title("🇲🇾 Malaysia Fuel Price Dashboard")
st.caption("Live data from data.gov.my, processed through an Airflow-orchestrated ETL pipeline")
st.caption(f"Latest data point: {weekly.iloc[-1]['price_date']}")

latest = weekly.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("RON95", f"RM {latest['ron95']:.2f}")
col2.metric("RON97", f"RM {latest['ron97']:.2f}")
col3.metric("Diesel", f"RM {latest['diesel']:.2f}")

st.subheader("Weekly Price Trend")
fig = px.line(weekly, x="price_date", y=["ron95", "ron97", "diesel"], labels={"value": "Price (RM)", "price_date": "Date", "variable": "Fuel Type"})
st.plotly_chart(fig, use_container_width=True)

st.subheader("Monthly Average Prices")
fig2 = px.bar(monthly, x="month", y=["avg_ron95", "avg_ron97", "avg_diesel"], barmode="group", labels={"value": "Avg Price (RM)", "month": "Month"})
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Raw Data")
st.dataframe(weekly, use_container_width=True)
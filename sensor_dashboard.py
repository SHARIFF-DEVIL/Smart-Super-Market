import streamlit as st
import sqlite3
import pandas as pd
import time

DB_PATH = "database/supermarket.db"


def fetch(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def app():
    st.title("📡 Single Shelf Monitoring")

    auto = st.checkbox("Auto Refresh")

    if auto:
        time.sleep(3)
        st.rerun()

    stock = fetch("""
        SELECT quantity
        FROM stock_logs
        ORDER BY timestamp DESC
        LIMIT 1
    """)

    if stock.empty:
        st.warning("No data yet")
        return

    quantity = int(stock.iloc[0]["quantity"])
    threshold = 5

    col1, col2 = st.columns(2)
    col1.metric("Current Quantity", quantity)
    col2.metric("Threshold", threshold)

    if quantity < threshold:
        st.error("🚨 LOW STOCK")
    else:
        st.success("🟢 STOCK OK")

    traffic = fetch("""
        SELECT COUNT(*) as visits
        FROM traffic_logs
    """)

    st.metric("Customer Visits", int(traffic.iloc[0]["visits"]))


if __name__ == "__main__":
    app()

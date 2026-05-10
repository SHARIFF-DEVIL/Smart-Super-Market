import streamlit as st
import pandas as pd
from database.db_manager import fetch_data

def revenue_dashboard():

    st.header("Revenue & Profit Intelligence")

    data = fetch_data("""
        SELECT sm.shelf_id,
               s.product_name,
               s.price,
               s.cost,
               SUM(sm.units_changed) as units_sold
        FROM stock_movements sm
        JOIN shelves s ON sm.shelf_id = s.shelf_id
        WHERE sm.movement_type='SALE'
        GROUP BY sm.shelf_id
    """)

    if data.empty:
        st.info("No sales data.")
        return

    data["Revenue"] = data["units_sold"] * data["price"]
    data["Cost"] = data["units_sold"] * data["cost"]
    data["Profit"] = data["Revenue"] - data["Cost"]
    data["Margin (%)"] = (
        (data["Profit"] / data["Revenue"]) * 100
    ).round(2)

    st.dataframe(data)

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Revenue (₹)",
                round(data["Revenue"].sum(), 2))

    col2.metric("Total Profit (₹)",
                round(data["Profit"].sum(), 2))

    col3.metric("Avg Margin (%)",
                round(data["Margin (%)"].mean(), 2))
import streamlit as st
import pandas as pd
from database.db_manager import fetch_data
def sales_intelligence():

    st.header("Shelf Sales Analysis")

    shelves = fetch_data("SELECT shelf_id FROM shelves")

    if shelves.empty:
        return

    shelf = st.selectbox("Select Shelf", shelves["shelf_id"])

    sales = fetch_data("""
        SELECT timestamp, units_changed
        FROM stock_movements
        WHERE shelf_id=? AND movement_type='SALE'
        ORDER BY timestamp
    """, (shelf,))

    if sales.empty:
        st.info("No sales data.")
        return

    sales["timestamp"] = pd.to_datetime(sales["timestamp"])
    sales["units_changed"] = pd.to_numeric(sales["units_changed"])

    sales["Cumulative"] = sales["units_changed"].cumsum()

    st.line_chart(sales.set_index("timestamp")["Cumulative"])

    total = sales["units_changed"].sum()

    st.metric("Total Units Sold", int(total))

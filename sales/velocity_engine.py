import streamlit as st
import pandas as pd
from database.db_manager import fetch_data
def sales_velocity_dashboard():

    st.header("Sales Velocity")

    data = fetch_data("""
        SELECT shelf_id, units_changed, timestamp
        FROM stock_movements
        WHERE movement_type='SALE'
        ORDER BY timestamp
    """)

    if data.empty:
        st.info("No sales data.")
        return

    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data["units_changed"] = pd.to_numeric(data["units_changed"])

    result = []

    for shelf in data["shelf_id"].unique():

        df = data[data["shelf_id"]==shelf]

        total = df["units_changed"].sum()
        hours = (df["timestamp"].max()-df["timestamp"].min()).total_seconds()/3600

        velocity = total/hours if hours>0 else total

        result.append({
            "Shelf": shelf,
            "Velocity (Units/Hour)": round(velocity,2)
        })

    res_df = pd.DataFrame(result)

    st.dataframe(res_df)
    st.bar_chart(res_df.set_index("Shelf"))
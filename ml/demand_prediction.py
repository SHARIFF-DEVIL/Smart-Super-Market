import streamlit as st
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from database.db_manager import fetch_data

def demand_prediction_dashboard():

    st.header("ML Demand Prediction")

    shelves = fetch_data("SELECT shelf_id FROM shelves")
    if shelves.empty:
        return

    shelf = st.selectbox("Select Shelf", shelves["shelf_id"])

    sales = fetch_data("""
        SELECT timestamp, units_changed
        FROM stock_movements
        WHERE shelf_id=? AND movement_type='SALE'
    """, (shelf,))

    if sales.empty:
        st.warning("Not enough data.")
        return

    sales["timestamp"] = pd.to_datetime(sales["timestamp"])
    sales["units_changed"] = pd.to_numeric(sales["units_changed"])

    sales["date"] = sales["timestamp"].dt.date
    daily = sales.groupby("date")["units_changed"].sum().reset_index()

    if len(daily) < 2:
        st.warning("Need more data.")
        return

    daily["index"] = np.arange(len(daily))

    X = daily[["index"]]
    y = daily["units_changed"]

    model = LinearRegression()
    model.fit(X,y)

    future_index = np.arange(len(daily), len(daily)+7).reshape(-1,1)
    pred = model.predict(future_index)

    st.line_chart(daily.set_index("date")["units_changed"])

    st.metric("Avg Predicted Next 7 Days",
              round(pred.mean(),2))

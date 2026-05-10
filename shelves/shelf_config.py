import streamlit as st
import pandas as pd
from database.db_manager import fetch_data, execute_query

def shelf_configuration():

    st.header("Shelf Configuration")

    shelf_id = st.text_input("Shelf ID")
    product = st.text_input("Product Name")
    unit_weight = st.number_input("Unit Weight", min_value=1.0)
    threshold = st.number_input("Threshold", min_value=1)
    max_capacity = st.number_input("Max Capacity", min_value=1)
    price = st.number_input("Selling Price", min_value=0.0)
    cost = st.number_input("Cost Price", min_value=0.0)
    brand = st.text_input("Brand")

    if st.button("Save Shelf"):
        execute_query("""
            INSERT OR REPLACE INTO shelves
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shelf_id,
            product,
            brand,
            unit_weight,
            threshold,
            max_capacity,
            price,
            cost
        ))

        st.success("Shelf Saved")
        st.rerun()

    st.dataframe(fetch_data("SELECT * FROM shelves"))
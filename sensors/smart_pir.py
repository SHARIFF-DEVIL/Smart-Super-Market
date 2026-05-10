import streamlit as st
import pandas as pd
from database.db_manager import fetch_data, execute_query
def traffic_monitoring():

    st.header("Smart PIR Monitoring")

    shelves = fetch_data("SELECT * FROM shelves")
    debounce = 5

    for _, shelf in shelves.iterrows():

        if st.button(f"Simulate Motion - {shelf['shelf_id']}"):

            last = fetch_data("""
                SELECT timestamp FROM traffic_logs
                WHERE shelf_id=?
                ORDER BY timestamp DESC LIMIT 1
            """, (shelf["shelf_id"],))

            allow = True

            if not last.empty:
                last_time = pd.to_datetime(last.iloc[0]["timestamp"])
                diff = (pd.Timestamp.now() - last_time).total_seconds()
                if diff < debounce:
                    allow = False

            if allow:
                execute_query("""
                    INSERT INTO traffic_logs (shelf_id, traffic_count)
                    VALUES (?,1)
                """, (shelf["shelf_id"],))
                st.success("Valid Footfall Recorded")
            else:
                st.warning("Ignored (Debounce Active)")

            st.rerun()
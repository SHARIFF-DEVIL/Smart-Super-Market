import streamlit as st
import pandas as pd
from database.db_manager import fetch_data, execute_query
def stock_monitoring():

    st.header("Load Cell Simulation")

    shelves = fetch_data("SELECT * FROM shelves")

    for _, shelf in shelves.iterrows():

        weight = st.slider(
            f"{shelf['product_name']} Weight",
            0, 10000, 1000,
            key=f"w_{shelf['shelf_id']}"
        )

        quantity = int(weight / float(shelf["unit_weight"]))
        st.write(f"Calculated Quantity: {quantity}")

        if st.button(f"Update {shelf['shelf_id']}"):

            prev = fetch_data("""
                SELECT quantity FROM stock_logs
                WHERE shelf_id=?
                ORDER BY timestamp DESC LIMIT 1
            """, (shelf["shelf_id"],))

            prev_qty = int(prev.iloc[0]["quantity"]) if not prev.empty else quantity
            diff = prev_qty - quantity

            if diff > 0:
                mtype = "SALE"
                units = diff
            elif diff < 0:
                mtype = "RESTOCK"
                units = abs(diff)
            else:
                mtype = "NO_CHANGE"
                units = 0

            execute_query("""
                INSERT INTO stock_logs (shelf_id, weight, quantity)
                VALUES (?, ?, ?)
            """, (shelf["shelf_id"], weight, quantity))

            if units > 0:
                execute_query("""
                    INSERT INTO stock_movements
                    (shelf_id, previous_quantity, new_quantity,
                     units_changed, movement_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    shelf["shelf_id"],
                    prev_qty,
                    quantity,
                    units,
                    mtype
                ))

            st.success(f"{mtype} recorded: {units}")
            st.rerun()

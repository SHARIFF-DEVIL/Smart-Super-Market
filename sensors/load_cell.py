import streamlit as st
import pandas as pd
from database.db_manager import fetch_data, execute_query
from modules.automation.auto_task_engine import create_auto_task


def stock_monitoring():

    st.header("Load Cell Simulation")

    shelves = fetch_data("SELECT * FROM shelves")

    for _, shelf in shelves.iterrows():

        # ============================
        # INPUT SIMULATION
        # ============================
        weight = st.slider(
            f"{shelf['product_name']} ({shelf['brand']}) Weight",
            0, 10000, 1000,
            key=f"w_{shelf['shelf_id']}"
        )

        quantity = int(weight / float(shelf["unit_weight"]))
        st.write(f"Calculated Quantity: {quantity}")

        # ============================
        # EXTRACT VALUES
        # ============================
        threshold = shelf["threshold"]
        product_name = f"{shelf['product_name']} ({shelf['brand']})"
        shelf_id = shelf["shelf_id"]

        task_desc = f"Restock {product_name} on shelf {shelf_id}"

        # ============================
        # UPDATE BUTTON
        # ============================
        if st.button(f"Update {shelf_id}"):

            # ----------------------------
            # PREVIOUS QUANTITY
            # ----------------------------
            prev = fetch_data("""
                SELECT quantity FROM stock_logs
                WHERE shelf_id=?
                ORDER BY timestamp DESC LIMIT 1
            """, (shelf_id,))

            prev_qty = int(prev.iloc[0]["quantity"]) if not prev.empty else quantity
            diff = prev_qty - quantity

            # ----------------------------
            # MOVEMENT TYPE
            # ----------------------------
            if diff > 0:
                mtype = "SALE"
                units = diff
            elif diff < 0:
                mtype = "RESTOCK"
                units = abs(diff)
            else:
                mtype = "NO_CHANGE"
                units = 0

            # ============================
            # STORE STOCK LOG
            # ============================
            execute_query("""
                INSERT INTO stock_logs (shelf_id, weight, quantity)
                VALUES (?, ?, ?)
            """, (shelf_id, weight, quantity))

            # ============================
            # STORE MOVEMENT
            # ============================
            if units > 0:
                execute_query("""
                    INSERT INTO stock_movements
                    (shelf_id, previous_quantity, new_quantity,
                     units_changed, movement_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    shelf_id,
                    prev_qty,
                    quantity,
                    units,
                    mtype
                ))

            # ============================
            # 🔥 RESET TASK (VERY IMPORTANT)
            # ============================
            if quantity >= threshold:
                execute_query("""
                    UPDATE tasks
                    SET status = 'Completed'
                    WHERE task_description = ?
                    AND status = 'Pending'
                """, (task_desc,))

                st.info("Stock normal → task reset")

            # ============================
            # 🔥 AUTO TASK TRIGGER
            # ============================
            if quantity < threshold:

                existing = fetch_data("""
                    SELECT * FROM tasks
                    WHERE task_description = ?
                    AND status = 'Pending'
                """, (task_desc,))

                if existing.empty:
                    create_auto_task(product_name, shelf_id)
                    st.warning("⚠️ Low stock → Task Assigned")
                else:
                    st.info("Task already pending → no duplicate")

            # ============================
            # SUCCESS MESSAGE
            # ============================
            st.success(f"{mtype} recorded: {units}")

            st.rerun()
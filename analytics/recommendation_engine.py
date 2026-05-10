import streamlit as st
import pandas as pd
from database.db_manager import fetch_data

def shelf_recommendation():

    st.header("🧠 Shelf Recommendation (Custom Strategy)")

    # 🔹 Monthly Sales Data
    data = fetch_data("""
        SELECT s.shelf_id,
               s.product_name,
               SUM(sm.units_changed) as total_sold
        FROM stock_movements sm
        JOIN shelves s ON sm.shelf_id = s.shelf_id
        WHERE sm.movement_type = 'SALE'
        AND strftime('%Y-%m', sm.timestamp) = strftime('%Y-%m', 'now')
        GROUP BY s.shelf_id
    """)

    if data.empty:
        st.warning("No sales data available.")
        return

    # 🔹 Sort descending
    data = data.sort_values(by="total_sold", ascending=False).reset_index(drop=True)

    # 🔹 Classification thresholds
    max_sales = data["total_sold"].max()

    def classify(x):
        if x > 0.7 * max_sales:
            return "HIGH"
        elif x > 0.3 * max_sales:
            return "MEDIUM"
        else:
            return "LOW"

    data["Category"] = data["total_sold"].apply(classify)

    # 🔴 YOUR CUSTOM PLACEMENT LOGIC
    def recommend(cat):
        if cat == "HIGH":
            return "Move to LAST Shelf"
        elif cat == "MEDIUM":
            return "Keep in MIDDLE Shelf"
        else:
            return "Move to FRONT Shelf"

    data["Recommendation"] = data["Category"].apply(recommend)

    # 🔹 Display Table
    st.subheader("📊 Monthly Product Performance")

    st.dataframe(
        data[["product_name", "total_sold", "Category", "Recommendation"]],
        use_container_width=True
    )

    # 🔹 Visual
    st.bar_chart(data.set_index("product_name")["total_sold"])

    # 🔹 Highlight Insights
    st.subheader("Insights")

    high = data[data["Category"]=="HIGH"]
    low = data[data["Category"]=="LOW"]

    if not high.empty:
        st.error(f"High Selling → Move to LAST Shelf: {', '.join(high['product_name'])}")

    if not low.empty:
        st.success(f"Low Selling → Move to FRONT Shelf: {', '.join(low['product_name'])}")
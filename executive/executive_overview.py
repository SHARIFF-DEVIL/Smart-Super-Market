import streamlit as st
import pandas as pd
from database.db_manager import fetch_data

def executive_overview():

    st.header("📊 Executive Overview")

    # =====================================================
    # 🔹 STOCK (WITH BRAND)
    # =====================================================

    stock = fetch_data("""
        SELECT s.shelf_id,
               s.product_name,
               s.brand,
               s.threshold,
               COALESCE(sl.quantity,0) as quantity
        FROM shelves s
        LEFT JOIN stock_logs sl
        ON sl.id = (
            SELECT id FROM stock_logs
            WHERE shelf_id = s.shelf_id
            ORDER BY timestamp DESC
            LIMIT 1
        )
    """)

    if stock.empty:
        st.info("No shelves configured.")
        return

    # =====================================================
    # 🔹 KPI CARDS
    # =====================================================

    total_units = int(stock["quantity"].sum())
    total_products = len(stock)

    traffic = fetch_data("""
        SELECT COALESCE(SUM(traffic_count),0) as total_traffic
        FROM traffic_logs
    """)

    total_traffic = int(traffic.iloc[0]["total_traffic"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Products", total_products)
    col2.metric("Units in Shelves", total_units)
    col3.metric("Total Traffic", total_traffic)

    st.divider()

    # =====================================================
    # 🔴 LOW STOCK ALERTS (WITH BRAND)
    # =====================================================

    st.subheader("🚨 Low Stock Alerts")

    low = stock[stock["quantity"] < stock["threshold"]]

    if not low.empty:
        for _, row in low.iterrows():
            st.error(
                f"{row['product_name']} ({row['brand']}) | "
                f"Shelf {row['shelf_id']} | "
                f"Remaining: {int(row['quantity'])} | "
                f"Threshold: {int(row['threshold'])}"
            )
    else:
        st.success("All shelves above threshold.")

    st.divider()

    # =====================================================
    # 📦 SHELF INVENTORY (WITH BRAND)
    # =====================================================

    st.subheader("📦 Current Shelf Inventory")

    st.dataframe(
        stock[["shelf_id", "product_name", "brand", "quantity"]],
        use_container_width=True
    )

    st.divider()

    # =====================================================
    # 🏷 BRAND-WISE STOCK DISTRIBUTION
    # =====================================================

    st.subheader("🏷 Brand-wise Stock Distribution")

    brand_stock = stock.groupby("brand")["quantity"].sum().reset_index()

    if not brand_stock.empty:
        st.bar_chart(brand_stock.set_index("brand"))
    else:
        st.info("No brand data available.")

    st.divider()

    # =====================================================
    # 💰 BRAND SALES (IF TRANSACTIONS EXIST)
    # =====================================================

    st.subheader("💰 Brand-wise Sales")

    sales = fetch_data("""
        SELECT brand, SUM(quantity) as total_sales
        FROM transactions
        GROUP BY brand
        ORDER BY total_sales DESC
    """)

    if not sales.empty:
        st.bar_chart(sales.set_index("brand"))
    else:
        st.info("No transaction data available.")

    st.divider()

    # =====================================================
    # 🧠 QUICK INSIGHTS
    # =====================================================

    st.subheader("🧠 Insights")

    if not brand_stock.empty:
        top_brand_stock = brand_stock.sort_values("quantity", ascending=False).iloc[0]["brand"]
        st.info(f"📦 Highest stock brand: **{top_brand_stock}**")

    if not sales.empty:
        top_sales_brand = sales.iloc[0]["brand"]
        st.info(f"🔥 Top selling brand: **{top_sales_brand}**")
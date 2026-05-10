import streamlit as st
from database.db_manager import fetch_data


def sensor_dashboard():

    st.title("📡 Sensor Monitoring Dashboard")

    # =========================
    # AUTO REFRESH (OPTIONAL)
    # =========================
    refresh = st.checkbox("Auto Refresh (5s)")
    if refresh:
        st.experimental_rerun()

    # =========================
    # LATEST STOCK PER SHELF
    # =========================
    stock = fetch_data("""
        SELECT 
            s.shelf_id,
            s.product_name,
            s.brand,
            s.threshold,
            COALESCE(sl.quantity, 0) AS quantity
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
        st.warning("No stock data available")
        return

    # =========================
    # KPI CARDS
    # =========================
    total_units = int(stock["quantity"].sum())
    low_count = int((stock["quantity"] < stock["threshold"]).sum())

    col1, col2 = st.columns(2)
    col1.metric("Total Units", total_units)
    col2.metric("Low Stock Shelves", low_count)

    st.divider()

    # =========================
    # LOW STOCK ALERTS
    # =========================
    st.subheader("🚨 Low Stock Alerts")

    low_stock = stock[stock["quantity"] < stock["threshold"]]

    if not low_stock.empty:
        for _, row in low_stock.iterrows():
            st.error(
                f"{row['product_name']} ({row['brand']}) | "
                f"Shelf: {row['shelf_id']} | "
                f"Qty: {row['quantity']} | "
                f"Threshold: {row['threshold']}"
            )
    else:
        st.success("All shelves are above threshold")

    st.divider()

    # =========================
    # STOCK TABLE
    # =========================
    st.subheader("📦 Shelf Status")

    stock["Status"] = stock.apply(
        lambda r: "🔴 Low" if r["quantity"] < r["threshold"] else "🟢 OK",
        axis=1
    )

    st.dataframe(
        stock[[
            "shelf_id",
            "product_name",
            "brand",
            "quantity",
            "threshold",
            "Status"
        ]],
        use_container_width=True
    )

    st.divider()

    # =========================
    # TRAFFIC (PIR)
    # =========================
    st.subheader("🚶 Shelf Traffic")

    traffic = fetch_data("""
        SELECT shelf_id, SUM(traffic_count) as total_traffic
        FROM traffic_logs
        GROUP BY shelf_id
        ORDER BY total_traffic DESC
    """)

    if not traffic.empty:
        st.bar_chart(
            traffic.set_index("shelf_id")["total_traffic"]
        )
    else:
        st.info("No traffic data yet")
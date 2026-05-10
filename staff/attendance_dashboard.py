import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "database/supermarket.db"


def dashboard():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query("""
        SELECT s.name, a.check_in, a.check_out, a.status, a.fine
        FROM attendance_logs a
        JOIN staff s ON s.staff_id = a.staff_id
        WHERE DATE(a.check_in, 'localtime') = DATE('now', 'localtime')
    """, conn)

    st.header("📊 Attendance Dashboard")

    if df.empty:
        st.warning("No attendance today")
        return

    st.dataframe(df, use_container_width=True)

    st.subheader("Status Distribution")
    st.bar_chart(df["status"].value_counts())

    st.metric("💰 Total Fine", round(df["fine"].sum(), 2))
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from database.db_manager import fetch_data


def staff_performance():

    st.header("Staff Performance Dashboard")

    # Auto refresh every 5 seconds
    st_autorefresh(interval=5000, key="perf_refresh")

    # ======================================================
    # 1️⃣ STAFF-WISE PERFORMANCE SUMMARY
    # ======================================================

    perf = fetch_data("""
        SELECT 
            s.staff_id,
            s.name,
            COUNT(t.id) AS total_tasks,
            SUM(CASE 
                    WHEN t.completed_at IS NOT NULL 
                    THEN 1 
                    ELSE 0 
                END) AS completed_tasks
        FROM staff s
        LEFT JOIN tasks t
            ON s.staff_id = t.staff_id
        GROUP BY s.staff_id, s.name
        ORDER BY s.name
    """)

    if perf.empty:
        st.info("No staff available.")
        return

    # Replace NULL with 0
    perf["total_tasks"] = perf["total_tasks"].fillna(0).astype(int)
    perf["completed_tasks"] = perf["completed_tasks"].fillna(0).astype(int)

    # Pending Tasks
    perf["pending_tasks"] = (
        perf["total_tasks"] - perf["completed_tasks"]
    )

    # Completion Rate
    perf["Completion Rate (%)"] = perf.apply(
        lambda row: round(
            (row["completed_tasks"] / row["total_tasks"]) * 100, 2
        ) if row["total_tasks"] > 0 else 0,
        axis=1
    )

    # ======================================================
    # KPI METRICS
    # ======================================================

    total_assigned = int(perf["total_tasks"].sum())
    total_completed = int(perf["completed_tasks"].sum())
    total_pending = int(perf["pending_tasks"].sum())

    overall_rate = (
        (total_completed / total_assigned) * 100
        if total_assigned > 0 else 0
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Tasks Assigned", total_assigned)
    col2.metric("Total Tasks Completed", total_completed)
    col3.metric("Total Pending Tasks", total_pending)
    col4.metric("Overall Completion Rate (%)", round(overall_rate, 2))

    st.divider()

    # ======================================================
    # STAFF-WISE TABLE
    # ======================================================

    st.subheader("Staff-wise Performance Summary")

    st.dataframe(
        perf[
            [
                "staff_id",
                "name",
                "total_tasks",
                "completed_tasks",
                "pending_tasks",
                "Completion Rate (%)"
            ]
        ],
        use_container_width=True
    )

    st.bar_chart(
        perf.set_index("name")["Completion Rate (%)"]
    )

    st.divider()

    # ======================================================
    # 2️⃣ TASK-LEVEL DETAILS
    # ======================================================

    st.subheader("Task-Level Breakdown")

    tasks = fetch_data("""
        SELECT 
            t.id AS id,
            s.name,
            t.task_description,
            t.priority,
            t.assigned_time,
            t.completed_at
        FROM tasks t
        JOIN staff s
            ON t.staff_id = s.staff_id
        ORDER BY t.assigned_time DESC
    """)

    if tasks.empty:
        st.info("No tasks assigned yet.")
        return

    tasks["Status"] = tasks["completed_at"].apply(
        lambda x: "✅ Completed" if pd.notnull(x) else "⏳ Pending"
    )

    st.dataframe(tasks, use_container_width=True)
    st.write("DEBUG TASKS TABLE:")
    st.write(fetch_data("SELECT * FROM tasks"))
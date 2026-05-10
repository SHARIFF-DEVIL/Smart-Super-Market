import streamlit as st
import pandas as pd
from database.db_manager import fetch_data, execute_query
from modules.staff.telegram_service import send_task_notification
from modules.staff.performance_engine import get_staff_performance_summary


def work_management():

    st.header("🛠 Work Management & Task Assignment")

    # ======================================================
    # 1️⃣ FETCH PRESENT STAFF
    # ======================================================

    present = fetch_data("""
        SELECT DISTINCT s.staff_id, s.name
        FROM attendance_logs a
        JOIN staff s ON a.staff_id = s.staff_id
        WHERE a.check_in IS NOT NULL
        AND a.check_out IS NULL
    """)

    if present.empty:
        st.warning("No staff currently checked in.")
        return

    # ======================================================
    # 2️⃣ ASSIGN TASK
    # ======================================================

    st.subheader("Assign New Task")

    staff_name = st.selectbox("Assign To", present["name"])
    task_description = st.text_area("Task Description")

    col1, col2 = st.columns(2)

    with col1:
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])

    with col2:
        deadline = st.date_input("Deadline")

    if st.button("Assign Task"):

        if task_description.strip() == "":
            st.warning("Task description required.")
            return

        staff_id = int(
            present[present["name"] == staff_name]["staff_id"].values[0]
        )

        # Insert task
        execute_query("""
            INSERT INTO tasks
            (staff_id, task_description, priority, deadline)
            VALUES (?, ?, ?, ?)
        """, (staff_id, task_description, priority, deadline))

        # Get latest task_id
        task_id = fetch_data(
            "SELECT MAX(id) as id FROM tasks"
        )["id"].iloc[0]

        # Send Telegram Notification with button
        send_task_notification(
            task_id,
            staff_name,
            task_description,
            priority,
            deadline
        )

        st.success("Task Assigned Successfully")
        st.rerun()

    st.divider()

    # ======================================================
    # 3️⃣ TASK OVERVIEW
    # ======================================================

    st.subheader("📋 Task Overview")

    tasks = fetch_data("""
        SELECT 
            t.id,
            s.name,
            t.task_description,
            t.priority,
            t.deadline,
            t.status,
            t.assigned_time,
            t.completed_at
        FROM tasks t
        JOIN staff s ON t.staff_id = s.staff_id
        ORDER BY t.assigned_time DESC
    """)

    if tasks.empty:
        st.info("No tasks available.")
        return

    today = pd.to_datetime("today").date()

    # Safe status function (handles NULL deadlines)
    def get_status(row):
        if row["status"] == "Completed":
            return "✅ Completed"
        if pd.isna(row["deadline"]):
            return "⚪ No Deadline"
        deadline = pd.to_datetime(row["deadline"]).date()
        if deadline < today:
            return "🔴 Overdue"
        return "⏳ Pending"

    tasks["Status_Display"] = tasks.apply(get_status, axis=1)

    # Highlight priority
    def highlight_priority(val):
        if val == "High":
            return "color: red; font-weight: bold"
        elif val == "Medium":
            return "color: orange"
        return "color: green"

    styled = tasks.style.map(highlight_priority, subset=["priority"])

    st.dataframe(styled, use_container_width=True)

    st.divider()

    # ======================================================
    # 4️⃣ MARK COMPLETED (STREAMLIT BACKUP)
    # ======================================================

    st.subheader("Mark Task Completed (Manual Backup)")

    pending = tasks[tasks["status"] == "Pending"]

    if pending.empty:
        st.info("No pending tasks.")
    else:
        options = pending.apply(
            lambda x: f"{x['id']} - {x['name']} - {x['task_description']}",
            axis=1
        )

        selected = st.selectbox("Select Task", options)

        if st.button("Mark Completed"):

            task_id = int(selected.split(" - ")[0])

            execute_query("""
                UPDATE tasks
                SET status = 'Completed',
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (task_id,))

            st.success("Task marked as completed!")
            st.rerun()

    st.divider()

    # ======================================================
    # 5️⃣ PERFORMANCE SNAPSHOT
    # ======================================================

    st.subheader("Performance Snapshot")

    perf = get_staff_performance_summary()

    if not perf.empty:
        st.dataframe(perf, use_container_width=True)
from database.db_manager import fetch_data
import pandas as pd


def get_staff_performance_summary():

    perf = fetch_data("""
        SELECT 
            s.staff_id,
            s.name,
            COUNT(t.id) as total_tasks,
            SUM(CASE WHEN t.completed_at IS NOT NULL 
                     THEN 1 ELSE 0 END) as completed_tasks
        FROM staff s
        LEFT JOIN tasks t
        ON s.staff_id = t.staff_id
        GROUP BY s.staff_id, s.name
        ORDER BY s.name
    """)

    if perf.empty:
        return perf

    perf["total_tasks"] = perf["total_tasks"].fillna(0)
    perf["completed_tasks"] = perf["completed_tasks"].fillna(0)

    perf["Completion Rate (%)"] = perf.apply(
        lambda r: round((r["completed_tasks"] / r["total_tasks"]) * 100, 2)
        if r["total_tasks"] > 0 else 0,
        axis=1
    )

    perf["Pending Tasks"] = (
        perf["total_tasks"] - perf["completed_tasks"]
    )

    return perf


def get_task_level_details():
    return fetch_data("""
        SELECT 
            t.id as iid,
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
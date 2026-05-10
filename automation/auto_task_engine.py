from database.db_manager import fetch_data, execute_query
from modules.staff.telegram_service import send_task_notification


# =========================
# SMART STAFF SELECTION
# =========================
def get_best_staff():

    staff = fetch_data("""
        SELECT 
            s.staff_id,
            s.name,
            COUNT(t.id) as total_tasks,
            SUM(CASE WHEN t.status='Completed' THEN 1 ELSE 0 END) as completed_tasks,
            MAX(t.assigned_time) as last_task_time
        FROM staff s
        JOIN attendance_logs a ON s.staff_id = a.staff_id
        LEFT JOIN tasks t ON s.staff_id = t.staff_id
        WHERE a.check_out IS NULL
        AND DATE(a.check_in) = DATE('now')
        AND a.status != 'Leave'
        GROUP BY s.staff_id, s.name
    """)

    if staff.empty:
        return None

    # Clean
    staff["total_tasks"] = staff["total_tasks"].fillna(0)
    staff["completed_tasks"] = staff["completed_tasks"].fillna(0)
    staff["last_task_time"] = staff["last_task_time"].fillna("1900-01-01")

    # Remove overworked staff
    avg_completed = staff["completed_tasks"].mean()

    if avg_completed > 0:
        staff = staff[staff["completed_tasks"] <= 3 * avg_completed]

    if staff.empty:
        return None

    # Oldest assignment first
    staff = staff.sort_values(by=["last_task_time"], ascending=True)

    # Fair window
    staff = staff.head(3)

    # Least tasks
    staff = staff.sort_values(by=["total_tasks"], ascending=True)

    return staff.iloc[0]


# =========================
# CREATE TASK (MAIN FIXED)
# =========================
def create_auto_task(product_name, shelf_id):

    task_desc = f"Restock {product_name} on shelf {shelf_id}"

    # 🚫 STRICT duplicate prevention
    existing = fetch_data("""
        SELECT * FROM tasks
        WHERE task_description = ?
        AND status = 'Pending'
    """, (task_desc,))

    if not existing.empty:
        print("⛔ Task already exists (Pending)")
        return

    staff = get_best_staff()

    if staff is None:
        print("⚠️ No available staff")
        return

    staff_id = int(staff["staff_id"])
    staff_name = staff["name"]

    priority = "High"

    execute_query("""
        INSERT INTO tasks
        (staff_id, task_description, priority, deadline, status)
        VALUES (?, ?, ?, DATE('now'), 'Pending')
    """, (staff_id, task_desc, priority))

    # Get task id
    task_id = fetch_data("SELECT MAX(id) as id FROM tasks")["id"].iloc[0]

    # Telegram notify
    send_task_notification(
        task_id,
        staff_name,
        task_desc,
        priority,
        "Today"
    )

    print(f"✅ Task Assigned to {staff_name}")
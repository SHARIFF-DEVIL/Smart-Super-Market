from datetime import datetime, time
from database.db_manager import fetch_data, execute_query


def login_staff(staff_id):

    now = datetime.now()

    existing = fetch_data("""
        SELECT * FROM attendance_logs
        WHERE staff_id = ?
        AND DATE(check_in, 'localtime') = DATE('now', 'localtime')
        AND check_out IS NULL
    """, (staff_id,))

    if not existing.empty:
        return "Already Logged In"

    company_start = time(10, 0)
    leave_cutoff = time(14, 0)

    if now.time() > leave_cutoff:
        status = "Leave"
        late_minutes = 0
        fine = 0

    elif now.time() > company_start:
        delay = datetime.combine(now.date(), now.time()) - datetime.combine(now.date(), company_start)
        late_minutes = int(delay.total_seconds() / 60)
        fine = (late_minutes / 60) * 0.05
        status = "Late"

    else:
        status = "Present"
        late_minutes = 0
        fine = 0

    execute_query("""
        INSERT INTO attendance_logs
        (staff_id, late_minutes, fine, status)
        VALUES (?, ?, ?, ?)
    """, (staff_id, late_minutes, fine, status))

    return f"Logged In ({status})"


def logout_staff(staff_id):

    existing = fetch_data("""
        SELECT * FROM attendance_logs
        WHERE staff_id = ?
        AND check_out IS NULL
    """, (staff_id,))

    if existing.empty:
        return "Not Logged In"

    execute_query("""
        UPDATE attendance_logs
        SET check_out = CURRENT_TIMESTAMP
        WHERE staff_id = ?
        AND check_out IS NULL
    """, (staff_id,))

    return "Logged Out"
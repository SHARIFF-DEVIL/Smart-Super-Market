import streamlit as st
import cv2
import face_recognition
import sqlite3
import pickle
import numpy as np
from datetime import datetime, time

DB_PATH = "database/supermarket.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def face_attendance():

    st.header("📸 Smart Face Attendance System")

    mode = st.radio("Select Mode", ["Entry", "Exit"])

    if st.button("Scan Face"):

        # =========================
        # CAPTURE IMAGE
        # =========================
        cap = cv2.VideoCapture(0)

        for _ in range(15):
            ret, frame = cap.read()

        ret, frame = cap.read()
        cap.release()

        if not ret:
            st.error("Camera error")
            return

        # =========================
        # FACE ENCODING
        # =========================
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_encodings(rgb)

        if len(faces) != 1:
            st.error("Ensure only one face is visible")
            return

        unknown = faces[0]
        unknown = unknown / np.linalg.norm(unknown)

        # =========================
        # FETCH REGISTERED FACES
        # =========================
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT staff_id, name, face_encoding
            FROM staff
            WHERE face_encoding IS NOT NULL
        """)

        rows = cursor.fetchall()

        if not rows:
            st.error("No registered faces found")
            return

        # =========================
        # MATCH FACE
        # =========================
        best = None
        min_dist = 999

        for staff_id, name, blob in rows:

            known = pickle.loads(blob)
            dist = np.linalg.norm(known - unknown)

            st.write(f"{name} → {round(dist, 3)}")

            if dist < min_dist:
                min_dist = dist
                best = (staff_id, name)

        if min_dist >= 0.7:
            st.error("❌ Face not recognized")
            return

        staff_id, name = best
        st.success(f"✅ {name} recognized")

        # =========================
        # CHECK EXISTING SESSION
        # =========================
        cursor.execute("""
            SELECT * FROM attendance_logs
            WHERE staff_id = ?
            AND DATE(check_in, 'localtime') = DATE('now', 'localtime')
            AND check_out IS NULL
        """, (staff_id,))

        existing = cursor.fetchall()

        # =========================
        # ENTRY LOGIC
        # =========================
        if mode == "Entry":

            if existing:
                st.warning(f"⚠️ {name} already inside")
                conn.close()
                return

            now = datetime.now()
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

            cursor.execute("""
                INSERT INTO attendance_logs (staff_id, status, late_minutes, fine)
                VALUES (?, ?, ?, ?)
            """, (staff_id, status, late_minutes, fine))

            st.success(f"🟢 {name} Logged IN ({status})")

        # =========================
        # EXIT LOGIC
        # =========================
        elif mode == "Exit":

            if not existing:
                st.warning(f"⚠️ {name} is not inside")
                conn.close()
                return

            cursor.execute("""
                UPDATE attendance_logs
                SET check_out = CURRENT_TIMESTAMP
                WHERE staff_id = ?
                AND check_out IS NULL
            """, (staff_id,))

            st.success(f"🔴 {name} Logged OUT")

        conn.commit()
        conn.close()
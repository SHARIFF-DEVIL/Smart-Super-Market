import cv2
import face_recognition
import sqlite3
import pickle
import numpy as np

DB_PATH = "database/supermarket.db"


def register():
    name = input("Enter staff name: ").strip()
    role = input("Enter role (Manager/Worker/etc): ").strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO staff (name, role) VALUES (?, ?)",
        (name, role)
    )

    staff_id = cursor.lastrowid
    conn.commit()

    print("📸 Capturing face... Look at camera")

    cap = cv2.VideoCapture(0)
    encodings = []

    for i in range(20):
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_encodings(rgb)

        print(f"Frame {i}: Faces = {len(faces)}")

        if len(faces) == 1:
            encodings.append(faces[0])

    cap.release()

    if len(encodings) < 5:
        print("❌ Face capture failed. Try again.")
        return

    encoding = np.mean(encodings, axis=0)
    encoding = encoding / np.linalg.norm(encoding)

    cursor.execute(
        "UPDATE staff SET face_encoding=? WHERE staff_id=?",
        (pickle.dumps(encoding), staff_id)
    )

    conn.commit()
    conn.close()

    print(f"✅ {name} registered as {role}")


if __name__ == "__main__":
    register()
import serial
import time
from database.db_manager import execute_query

PORT = "COM5"       # Change to your Arduino COM port (e.g. /dev/ttyUSB0 on Linux)
BAUD = 9600
UNIT_WEIGHT = 5     # Grams per item (adjust to your product)
THRESHOLD = 5       # Minimum quantity before low-stock alert


def run():
    ser = serial.Serial(PORT, BAUD)
    time.sleep(2)

    print("Connected to Arduino...")

    while True:
        try:
            line = ser.readline().decode().strip()

            if not line or "SYSTEM_READY" in line:
                continue

            weight, motion = line.split(",")
            weight = float(weight)
            motion = int(motion)
            quantity = int(weight / UNIT_WEIGHT)

            print(f"Weight: {weight} | Qty: {quantity} | Motion: {motion}")

            execute_query("""
                INSERT INTO stock_logs (shelf_id, weight, quantity)
                VALUES ('S1', ?, ?)
            """, (weight, quantity))

            if motion == 1:
                execute_query("""
                    INSERT INTO traffic_logs (shelf_id, traffic_count)
                    VALUES ('S1', 1)
                """)

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    run()

from database.db_manager import fetch_data
from modules.staff.auto_assign import create_auto_task

# Store last weights per shelf
last_weights = {}

# Cooldown to prevent repeated tasks
last_trigger_time = {}

import time


def get_shelf_config(shelf_id):
    data = fetch_data("""
        SELECT product_name, threshold_weight
        FROM shelves
        WHERE shelf_id = ?
    """, (shelf_id,))

    if data.empty:
        return None

    return data.iloc[0]


def should_trigger(shelf_id, cooldown=30):
    now = time.time()

    if shelf_id in last_trigger_time:
        if now - last_trigger_time[shelf_id] < cooldown:
            return False

    last_trigger_time[shelf_id] = now
    return True


def detect_event(shelf_id, current_weight):
    config = get_shelf_config(shelf_id)

    if config is None:
        return None, None

    threshold = config["threshold_weight"]
    product_name = config["product_name"]

    last_weight = last_weights.get(shelf_id, None)
    event = None

    if last_weight is not None:

        drop = last_weight - current_weight

        # ===== EVENT RULES =====

        # 1. Out of stock
        if current_weight <= 0:
            event = "OUT_OF_STOCK"

        # 2. Sudden drop (product fall)
        elif drop > (0.4 * threshold):
            event = "PRODUCT_FALL"

        # 3. Low stock
        elif current_weight < threshold:
            event = "LOW_STOCK"

    last_weights[shelf_id] = current_weight

    return event, product_name


def process_weight(shelf_id, current_weight):

    event, product_name = detect_event(shelf_id, current_weight)

    if event is None:
        return

    if not should_trigger(shelf_id):
        return

    # Map event → task
    if event == "PRODUCT_FALL":
        task = f"Check fallen items and fix shelf for {product_name}"

    elif event == "LOW_STOCK":
        task = f"Restock {product_name}"

    elif event == "OUT_OF_STOCK":
        task = f"URGENT: Refill {product_name}"

    else:
        return

    # Create task (your existing system)
    create_auto_task(product_name, shelf_id)
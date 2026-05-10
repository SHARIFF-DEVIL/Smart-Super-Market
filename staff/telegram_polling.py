import requests
import time
from database.db_manager import execute_query

BOT_TOKEN = "8640303414:AAFskSR-Ss9pTYufaqo9Qeacfb2zxPN7dqk"

last_update_id = 0


def process_updates():
    global last_update_id

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id+1}"
    res = requests.get(url).json()

    if not res.get("ok"):
        return

    for upd in res.get("result", []):
        last_update_id = upd["update_id"]

        if "callback_query" in upd:
            cb = upd["callback_query"]
            data = cb.get("data", "")

            if data.startswith("complete_"):
                task_id = int(data.split("_")[1])

                # ✅ Update DB
                execute_query("""
                    UPDATE tasks
                    SET status = 'Completed',
                        completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (task_id,))

                # ✅ Acknowledge button click
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                    json={
                        "callback_query_id": cb["id"],
                        "text": "✅ Task marked as completed!"
                    }
                )

                print(f"Task {task_id} marked completed.")


def run_polling():
    print("🔁 Telegram polling started...")
    while True:
        process_updates()
        time.sleep(2)
import requests

BOT_TOKEN = "8640303414:AAFskSR-Ss9pTYufaqo9Qeacfb2zxPN7dqk"
GROUP_CHAT_ID = "-1003723852238"


def send_task_notification(task_id, staff_name, task_description, priority, deadline):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    message = (
        f"📝 *New Task Assigned*\n\n"
        f"👤 *Staff:* {staff_name}\n"
        f"📌 *Task:* {task_description}\n"
        f"⚡ *Priority:* {priority}\n"
        f"📅 *Deadline:* {deadline}"
    )

    payload = {
        "chat_id": GROUP_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "reply_markup": {
            "inline_keyboard": [[
                {
                    "text": "✅ Mark Completed",
                    "callback_data": f"complete_{task_id}"
                }
            ]]
        }
    }

    res = requests.post(url, json=payload)
    print("Telegram send:", res.text)
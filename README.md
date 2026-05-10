# AI-Driven Smart Retail Intelligence Platform

A modular Streamlit application that brings AI-powered insights to retail store management — covering stock monitoring, staff attendance, sales analytics, demand prediction, basket analysis, and more.

---

## Features

| Module | Description |
|--------|-------------|
| **Executive Overview** | KPI summary — total products, units, traffic, brand-wise stock & sales |
| **Shelf Configuration** | Add / update shelf products, unit weights, thresholds, pricing |
| **Load Cell Simulation** | Simulate IoT weight-sensor readings; auto-detect SALE / RESTOCK events |
| **Smart PIR Monitoring** | Simulate footfall traffic with debounce logic |
| **Staff Management** | Work task assignment, performance tracking, face-recognition attendance |
| **Sales Intelligence** | Cumulative sales chart per shelf |
| **Sales Velocity** | Units-per-hour velocity per shelf |
| **Revenue & Profit** | Revenue, cost, profit, and margin per product |
| **ML Demand Prediction** | Linear regression on historical daily sales; 7-day forecast |
| **Product Clustering** | KMeans clustering on product co-occurrence matrix |
| **Basket Analysis** | Apriori association rules — frequent itemsets & product recommendations |
| **Customer Dashboard** | Product search + personalised "customers also buy" recommendations |
| **Sensor Dashboard** | Live shelf stock status + traffic bar chart |
| **Telegram Integration** | Auto-notify staff of tasks; mark-complete via inline button |
| **Arduino Sensor Reader** | Serial reader for real load cell + PIR sensor hardware |

---

## Project Structure

```
AI_Market_Analysis/
├── app.py                        # Main Streamlit entry point
├── sensor_dashboard.py           # Standalone single-shelf dashboard
├── sensor_reader.py              # Arduino serial reader
├── telegram_runner.py            # Start Telegram bot polling
├── requirements.txt
├── .gitignore
│
├── database/
│   ├── db_manager.py             # SQLite helpers (get_connection, fetch_data, execute_query)
│   └── schema.sql                # All CREATE TABLE definitions
│
└── modules/
    ├── analytics/
    │   └── recommendation_engine.py   # Shelf placement recommendations
    ├── automation/
    │   └── auto_task_engine.py        # Smart staff selection & auto task creation
    ├── customer/
    │   └── customer_dashboard.py      # Product search + basket recommendations
    ├── dashboard/
    │   └── sensor_dashboard.py        # Multi-shelf sensor monitoring dashboard
    ├── executive/
    │   └── executive_overview.py      # Top-level KPI overview
    ├── ml/
    │   ├── demand_prediction.py       # Linear regression demand forecast
    │   ├── load_online_retail.py      # Load UK Online Retail CSV dataset
    │   └── product_clustering.py     # KMeans product clustering
    ├── sales/
    │   ├── revenue_engine.py          # Revenue & profit per product
    │   ├── sales_intelligence.py      # Cumulative sales chart
    │   └── velocity_engine.py         # Sales velocity (units/hour)
    ├── sensors/
    │   ├── load_cell.py               # Load cell simulation + auto task trigger
    │   └── smart_pir.py               # PIR traffic simulation
    ├── shelves/
    │   ├── auto_event_engine.py       # Event detection (LOW_STOCK, PRODUCT_FALL, OUT_OF_STOCK)
    │   ├── shelf_config.py            # Shelf CRUD UI
    │   └── stock_monitor.py           # Simplified stock monitor
    ├── staff/
    │   ├── attendance_dashboard.py    # Today's attendance summary
    │   ├── attendance_engine.py       # Login / logout with late fine calculation
    │   ├── face_attendance.py         # Face-recognition entry / exit
    │   ├── performance.py             # Staff performance dashboard
    │   ├── performance_engine.py      # Performance data queries
    │   ├── register_face.py           # CLI tool to register a staff face
    │   ├── telegram_polling.py        # Poll Telegram for task completion callbacks
    │   ├── telegram_service.py        # Send task notification via Telegram bot
    │   └── work_management.py         # Assign tasks, mark complete, performance snapshot
    └── transactions/
        ├── basket_analysis.py         # Apriori basket analysis UI
        ├── basket_engine.py           # Apriori logic (mlxtend)
        └── generate_transactions.py   # Synthetic transaction generator
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/AI_Market_Analysis.git
cd AI_Market_Analysis
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `face-recognition` requires `cmake` and `dlib`. On Windows install [CMake](https://cmake.org/) and Visual Studio Build Tools first. On Linux: `sudo apt install cmake build-essential`.

### 4. Configure Telegram (optional)

Open `modules/staff/telegram_service.py` and `modules/staff/telegram_polling.py` and replace the placeholders:

```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
GROUP_CHAT_ID = "YOUR_GROUP_CHAT_ID"
```

Create a bot via [@BotFather](https://t.me/BotFather) and get the chat ID using the Telegram API.

### 5. Configure Arduino serial port (optional)

Open `sensor_reader.py` and set your COM port:

```python
PORT = "COM5"       # Linux: /dev/ttyUSB0
UNIT_WEIGHT = 5     # grams per item
```

---

## Running the App

```bash
streamlit run app.py
```

To run the Telegram polling bot in a separate terminal:

```bash
python telegram_runner.py
```

To run the Arduino serial reader:

```bash
python sensor_reader.py
```

---

## Database

The app uses **SQLite** (`database/supermarket.db`), auto-created on first run via `schema.sql`.

Key tables:

| Table | Purpose |
|-------|---------|
| `shelves` | Product configuration per shelf |
| `stock_logs` | Raw weight / quantity readings |
| `stock_movements` | SALE / RESTOCK events |
| `traffic_logs` | PIR footfall counts |
| `staff` | Staff records + face encodings |
| `attendance_logs` | Check-in / check-out records |
| `tasks` | Assigned tasks with status |
| `transactions` | Transaction-product records |
| `transaction_items` | Normalised transaction items |

> The `.db` file is excluded from version control via `.gitignore`. It is created automatically on first launch.

---

## Loading the Online Retail Dataset

The **ML → Load Retail Dataset** module accepts the [UCI Online Retail dataset](https://archive.ics.uci.edu/ml/datasets/online+retail) (`online_retail.csv`). Upload it directly via the file uploader in the UI.

---

## Tech Stack

- **Frontend / UI:** Streamlit
- **Database:** SQLite
- **ML:** scikit-learn (Linear Regression, KMeans), mlxtend (Apriori)
- **Computer Vision:** face_recognition, OpenCV
- **Notifications:** Telegram Bot API
- **Hardware:** Arduino (via pyserial)

---

## License

MIT

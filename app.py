import streamlit as st

from database.db_manager import initialize_database

from modules.executive.executive_overview import executive_overview
from modules.shelves.shelf_config import shelf_configuration
from modules.sensors.load_cell import stock_monitoring
from modules.sensors.smart_pir import traffic_monitoring
from modules.staff.work_management import work_management
from modules.staff.performance import staff_performance
from modules.staff.attendance_dashboard import dashboard
from modules.staff.face_attendance import face_attendance
from modules.sales.sales_intelligence import sales_intelligence
from modules.sales.velocity_engine import sales_velocity_dashboard
from modules.sales.revenue_engine import revenue_dashboard
from modules.ml.demand_prediction import demand_prediction_dashboard
from modules.ml.load_online_retail import load_online_retail_dataset
from modules.transactions.generate_transactions import generate_transactions
from modules.transactions.basket_analysis import basket_analysis
from modules.analytics.recommendation_engine import shelf_recommendation
from modules.customer.customer_dashboard import customer_dashboard
from modules.dashboard.sensor_dashboard import sensor_dashboard


def main():
    initialize_database()

    st.title("AI-Driven Smart Retail Intelligence Platform")

    category = st.sidebar.selectbox(
        "Select Module",
        [
            "Executive Overview",
            "Shelf Configuration",
            "Sensors",
            "Staff Management",
            "Sales & Revenue Intelligence",
            "ML Demand Prediction",
            "Transactions & Basket Analysis",
            "Load Retail Dataset",
            "Smart Shelf Recommendation",
            "Customer Smart Dashboard",
            "Sensor Dashboard"
        ]
    )

    if category == "Executive Overview":
        executive_overview()

    elif category == "Shelf Configuration":
        shelf_configuration()

    elif category == "Sensors":
        sub = st.sidebar.radio(
            "Sensors Module",
            [
                "Load Cell (Stock Monitoring)",
                "Smart PIR (Traffic Monitoring)"
            ]
        )
        if sub == "Load Cell (Stock Monitoring)":
            stock_monitoring()
        else:
            traffic_monitoring()

    elif category == "Staff Management":
        sub = st.sidebar.radio(
            "Staff Module",
            [
                "Work Management",
                "Staff Performance",
                "Attendance Dashboard",
                "Face Attendance"
            ]
        )
        if sub == "Work Management":
            work_management()
        elif sub == "Staff Performance":
            staff_performance()
        elif sub == "Attendance Dashboard":
            dashboard()
        elif sub == "Face Attendance":
            face_attendance()

    elif category == "Sales & Revenue Intelligence":
        sub = st.sidebar.radio(
            "Sales Module",
            [
                "Sales Intelligence",
                "Sales Velocity Engine",
                "Revenue & Profit Intelligence"
            ]
        )
        if sub == "Sales Intelligence":
            sales_intelligence()
        elif sub == "Sales Velocity Engine":
            sales_velocity_dashboard()
        elif sub == "Revenue & Profit Intelligence":
            revenue_dashboard()

    elif category == "ML Demand Prediction":
        demand_prediction_dashboard()

    elif category == "Transactions & Basket Analysis":
        sub = st.sidebar.radio(
            "Transaction Module",
            [
                "Generate Transactions",
                "Basket Analysis"
            ]
        )
        if sub == "Generate Transactions":
            generate_transactions()
        elif sub == "Basket Analysis":
            basket_analysis()

    elif category == "Load Retail Dataset":
        load_online_retail_dataset()

    elif category == "Smart Shelf Recommendation":
        shelf_recommendation()

    elif category == "Customer Smart Dashboard":
        customer_dashboard()

    elif category == "Sensor Dashboard":
        sensor_dashboard()


if __name__ == "__main__":
    main()

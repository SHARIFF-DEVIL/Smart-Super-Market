import streamlit as st
import pandas as pd
from database.db_manager import execute_query, fetch_data


def load_online_retail_dataset():

    st.header("Load Online Retail Dataset (UK - 50K)")

    try:
        df = pd.read_csv("D:\CLG PROJECT\Projects\AI Market Analysis\database\online_retail.csv", encoding="ISO-8859-1")
    except:
        st.error("Place online_retail.csv in project root folder.")
        return

    # 🔹 Clean dataset
    df = df.dropna(subset=["InvoiceNo", "Description"])
    df = df[df["Quantity"] > 0]
    df = df[df["Country"] == "United Kingdom"]

    df["InvoiceNo"] = df["InvoiceNo"].astype(str)

    # 🔹 Limit to first 50,000 invoices
    unique_invoices = df["InvoiceNo"].unique()[:50000]
    df = df[df["InvoiceNo"].isin(unique_invoices)]

    st.write("Filtered Rows:", len(df))
    st.write("Unique Transactions:", len(unique_invoices))

    # 🔹 Optional clear
    if st.checkbox("Clear existing transaction tables before loading"):
        execute_query("DELETE FROM transaction_items")
        execute_query("DELETE FROM transactions")
        st.info("Old transaction data cleared.")

    if not st.button("Load Dataset into Database"):
        return

    invoice_groups = df.groupby("InvoiceNo")

    inserted = 0

    for invoice, group in invoice_groups:

        # Insert transaction
        execute_query("""
            INSERT INTO transactions (timestamp)
            VALUES (CURRENT_TIMESTAMP)
        """)

        tid = fetch_data(
            "SELECT MAX(transaction_id) as id FROM transactions"
        ).iloc[0]["id"]

        # Insert unique products per invoice
        for item in group["Description"].unique():

            execute_query("""
                INSERT INTO transaction_items (transaction_id, product_name)
                VALUES (?, ?)
            """, (tid, item))

        inserted += 1

    st.success(f"{inserted} transactions inserted successfully.")
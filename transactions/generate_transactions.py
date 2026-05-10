import streamlit as st
import random
import uuid
from datetime import datetime
from database.db_manager import get_connection


def generate_transactions():

    st.header("🧾 Generate Retail Transactions")

    num_transactions = st.number_input(
        "Number of Transactions",
        min_value=100,
        max_value=2000,
        value=300,
        step=100
    )

    if st.button("Generate Transactions"):

        conn = get_connection()
        cursor = conn.cursor()

        products = [
            "Milk", "Bread", "Butter",
            "Eggs", "Cheese",
            "Rice", "Dal",
            "Chips", "Cola",
            "Shampoo", "Conditioner",
            "Soap", "Toothpaste"
        ]

        insert_data = []

        for _ in range(num_transactions):

            transaction_id = str(uuid.uuid4())
            basket = []

            # Base item
            item = random.choice(products)
            basket.append(item)

            # Strong patterns
            if item == "Milk":
                basket.extend(["Bread", "Butter"])

            if item == "Bread":
                basket.append("Butter")

            if item == "Chips":
                basket.append("Cola")

            if item == "Rice":
                basket.append("Dal")

            if item == "Shampoo":
                basket.append("Conditioner")

            # Add random noise
            for _ in range(random.randint(1, 2)):
                basket.append(random.choice(products))

            for product in basket:
                insert_data.append((
                    transaction_id,
                    product,
                    random.randint(1, 3),
                    datetime.now()
                ))

        cursor.executemany("""
            INSERT INTO transactions
            (transaction_id, product_name, quantity, timestamp)
            VALUES (?, ?, ?, ?)
        """, insert_data)

        conn.commit()
        conn.close()

        st.success(f"{num_transactions} transactions generated!")
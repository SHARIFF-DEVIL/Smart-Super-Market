import streamlit as st
from database.db_manager import fetch_data
from modules.transactions.basket_engine import (
    load_transactions,
    prepare_basket,
    run_apriori
)


def customer_dashboard():

    st.title("🛍 Customer Smart Dashboard")

    # =========================
    # LOAD PRODUCTS
    # =========================
    products = fetch_data("""
        SELECT DISTINCT product_name
        FROM shelves
    """)

    if products.empty:
        st.warning("No products available")
        return

    product_list = products["product_name"].tolist()

    # =========================
    # 🔍 SEARCH ENGINE
    # =========================
    search = st.text_input("🔍 Search Product")

    filtered = [
        p for p in product_list
        if search.lower() in p.lower()
    ] if search else product_list

    st.subheader("📦 Available Products")

    st.dataframe(
        {"Products": filtered},
        use_container_width=True
    )

    # =========================
    # SELECT PRODUCT
    # =========================
    selected = st.selectbox(
        "Select Product for Recommendations",
        filtered if filtered else product_list
    )

    # =========================
    # LOAD TRANSACTIONS
    # =========================
    df = load_transactions()

    if df.empty:
        st.warning("No transaction data")
        return

    basket_df = prepare_basket(df)

    _, rules = run_apriori(basket_df, 0.02)

    # =========================
    # 🎯 RECOMMENDATION ENGINE
    # =========================
    st.subheader("🎯 Customers Also Buy")

    if rules.empty:
        st.info("No recommendations available")
        return

    recs = []

    for _, row in rules.iterrows():

        antecedents = list(row["antecedents"])
        consequents = list(row["consequents"])

        if selected in antecedents:
            recs.extend(consequents)

    recs = list(set(recs))

    if recs:
        for r in recs:
            st.success(f"👉 {r}")
    else:
        st.info("No strong association found")

    # =========================
    # 📊 POPULAR PRODUCTS
    # =========================

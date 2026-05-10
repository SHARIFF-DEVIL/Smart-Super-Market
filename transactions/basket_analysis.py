import streamlit as st
from database.db_manager import fetch_data
from modules.transactions.basket_engine import (
    load_transactions,
    prepare_basket,
    run_apriori
)


def basket_analysis():

    st.header("🛒 Market Basket Analysis")

    # =========================
    # DEBUG
    # =========================
    total_rows = fetch_data(
        "SELECT COUNT(*) as c FROM transactions"
    )["c"][0]

    st.write("Total Transaction Rows:", total_rows)

    if total_rows == 0:
        st.warning("No transaction data found. Generate transactions first.")
        return

    # =========================
    # LOAD DATA
    # =========================
    df = load_transactions()

    if df.empty:
        st.warning("Transaction table is empty.")
        return

    st.subheader("📄 Sample Transactions")
    st.dataframe(df.head(10), use_container_width=True)

    # =========================
    # PREPARE BASKET
    # =========================
    basket_df = prepare_basket(df)

    st.subheader("🧮 Basket Matrix Info")
    st.write("Transactions:", basket_df.shape[0])
    st.write("Products:", basket_df.shape[1])

    # =========================
    # PARAMETERS
    # =========================
    min_support = st.slider(
        "Minimum Support",
        min_value=0.01,
        max_value=0.5,
        value=0.02,
        step=0.01
    )

    frequent_itemsets, rules = run_apriori(
        basket_df,
        min_support
    )

    st.divider()

    # =========================
    # FREQUENT ITEMSETS
    # =========================
    st.subheader("📦 Frequent Itemsets")

    if frequent_itemsets.empty:
        st.warning("No frequent itemsets found. Lower support.")
    else:
        st.dataframe(
            frequent_itemsets.sort_values("support", ascending=False),
            use_container_width=True
        )

    st.divider()

    # =========================
    # ASSOCIATION RULES
    # =========================
    st.subheader("🔗 Association Rules")

    if rules.empty:
        st.warning("No rules found. Lower support.")
    else:

        rules_display = rules[[
            "antecedents",
            "consequents",
            "support",
            "confidence",
            "lift"
        ]].sort_values("confidence", ascending=False)

        st.dataframe(rules_display, use_container_width=True)

        # =========================
        # RECOMMENDATION ENGINE
        # =========================
        st.subheader("🎯 Product Recommendations")

        top_rules = rules_display.head(5)

        for _, row in top_rules.iterrows():
            st.write(
                f"If customer buys {list(row['antecedents'])} → "
                f"recommend {list(row['consequents'])}"
            )

        st.subheader("📊 Top Confidence Rules")
        st.bar_chart(top_rules.set_index(top_rules.index)["confidence"])
import pandas as pd
from database.db_manager import fetch_data
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


def load_transactions():
    df = fetch_data("""
        SELECT transaction_id, product_name
        FROM transactions
    """)
    return df


def prepare_basket(df):

    if df.empty:
        return pd.DataFrame()

    basket = (
        df.groupby("transaction_id")["product_name"]
        .apply(list)
        .tolist()
    )

    if len(basket) == 0:
        return pd.DataFrame()

    te = TransactionEncoder()
    te_array = te.fit(basket).transform(basket)

    basket_df = pd.DataFrame(te_array, columns=te.columns_)

    return basket_df


def run_apriori(basket_df, min_support=0.02):

    if basket_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    frequent_itemsets = apriori(
        basket_df,
        min_support=min_support,
        use_colnames=True
    )

    if frequent_itemsets.empty:
        return frequent_itemsets, pd.DataFrame()

    # 🔥 FIXED: use confidence instead of strict lift
    rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=0.3
    )

    return frequent_itemsets, rules
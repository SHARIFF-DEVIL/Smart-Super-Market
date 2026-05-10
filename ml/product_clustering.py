import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from database.db_manager import fetch_data


def product_clustering():

    st.header("Product Clustering (Unsupervised ML)")

    # 🔹 Load transaction items
    data = fetch_data("""
        SELECT transaction_id, product_name
        FROM transaction_items
    """)

    if data.empty:
        st.warning("No transaction data available.")
        return

    # 🔹 Create Basket Matrix
    basket = (
        data.groupby(['transaction_id', 'product_name'])['product_name']
        .count().unstack().fillna(0)
    )

    basket = basket.applymap(lambda x: 1 if x > 0 else 0)

    # 🔹 Product Co-occurrence Matrix
    product_matrix = basket.T.dot(basket)

    # Remove self-correlation bias
    np.fill_diagonal(product_matrix.values, 0)

    # 🔹 Feature Engineering
    features = product_matrix.values

    if len(features) < 2:
        st.warning("Not enough products for clustering.")
        return

    # 🔹 Choose cluster count dynamically
    k = st.slider("Select Number of Clusters", 2, min(6, len(features)), 3)

    model = KMeans(n_clusters=k, random_state=42)
    model.fit(features)

    labels = model.labels_

    clustering_result = pd.DataFrame({
        "Product": product_matrix.index,
        "Cluster": labels
    })

    st.subheader("Clustered Products")
    st.dataframe(clustering_result.sort_values("Cluster"),
                 use_container_width=True)

    # 🔹 Display Cluster Groups
    st.subheader("Cluster Groups")

    for cluster_id in sorted(clustering_result["Cluster"].unique()):
        products = clustering_result[
            clustering_result["Cluster"] == cluster_id
        ]["Product"].tolist()

        st.success(f"Cluster {cluster_id}: {products}")
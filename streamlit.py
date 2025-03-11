import streamlit as st
import faiss
import ollama
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

all_docs = pd.read_csv('/Users/abhinav.sunderrajan/Desktop/finacial_fraudsters/csv/all_docs.csv')
all_docs = list(all_docs['all_docs'])
all_embeddings = np.load('/Users/abhinav.sunderrajan/Desktop/finacial_fraudsters/all_embeddings.npy') # load
index = faiss.IndexFlatL2(768)
index.add(np.array(all_embeddings))

# Streamlit UI
st.title("🔎 FAISS Financial Crime News Retrieval with Visualizations")

# User Input
query = st.text_input("Enter your query:", "Bank fined for fraud")
k = st.selectbox("Select number of nearest neighbors:", [5, 10, 15, 20], index=2)

# Search and Display Results
if st.button("Search"):
    # Encode query
    query_embedding = np.array(ollama.embeddings(model='nomic-embed-text',prompt=query).embedding)
    query_embedding = np.expand_dims(query_embedding, axis=0)

    # Search FAISS index
    D, I = index.search(query_embedding, k)

    # Compute Cosine Similarity
    similarities = cosine_similarity(query_embedding, all_embeddings[I[0]])[0]

    # Prepare Results Table
    results_df = pd.DataFrame({
        "News Article": [all_docs[idx] for idx in I[0]],
        "FAISS Distance": D[0],  # Lower is better in L2 search
        "Cosine Similarity": similarities  # Higher is better
    })

    # Display results
    st.subheader("📌 Retrieved Articles")
    st.dataframe(results_df.style.format({
        "FAISS Distance": "{:.4f}",
        "Cosine Similarity": "{:.4f}"
    }))

    # Bar Chart for Cosine Similarity
    st.subheader("📊 Cosine Similarity of Retrieved Articles")
    fig, ax = plt.subplots()
    ax.barh(range(len(similarities)), similarities, color='skyblue', edgecolor='black')
    ax.set_yticks(range(len(similarities)))
    ax.set_yticklabels([all_docs[idx][:50] + "..." for idx in I[0]])  # Shortened text
    ax.set_xlabel("Cosine Similarity (Higher is Better)")
    ax.set_title("Cosine Similarity of Retrieved News Articles")
    st.pyplot(fig)

    # Scatter Plot for FAISS Distance vs Cosine Similarity
    st.subheader("📈 FAISS Distance vs. Cosine Similarity")
    fig, ax = plt.subplots()
    ax.scatter(D[0], similarities, color='red', alpha=0.7)
    for i, txt in enumerate([all_docs[idx][:30] + "..." for idx in I[0]]):
        ax.annotate(txt, (D[0][i], similarities[i]), fontsize=8, alpha=0.7)
    ax.set_xlabel("FAISS Distance (Lower is Better)")
    ax.set_ylabel("Cosine Similarity (Higher is Better)")
    ax.set_title("Relationship Between FAISS Distance & Cosine Similarity")
    st.pyplot(fig)

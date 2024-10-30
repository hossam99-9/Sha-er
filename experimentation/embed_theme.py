import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import faiss

# List of Arabic poem themes
themes = [
    "قصيدة اعتذار",
    "قصيدة الاناشيد",
    "قصيدة المعلقات",
    "قصيدة حزينه",
    "قصيدة دينية",
    "قصيدة ذم",
    "قصيدة رثاء",
    "قصيدة رومنسيه",
    "قصيدة سياسية",
    "قصيدة شوق",
    "قصيدة عامه",
    "قصيدة عتاب",
    "قصيدة غزل",
    "قصيدة فراق",
    "قصيدة قصيره",
    "قصيدة مدح",
    "قصيدة هجاء",
    "قصيدة وطنيه"
]

# Load a pre-trained model that supports Arabic
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

with open('./data_folder/theme_embeddings.pkl', 'rb') as f:
    embeddings = pickle.load(f)
print("loaded embeddings")

# Normalize the embeddings
faiss.normalize_L2(embeddings)

# Create a FAISS index
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

def find_similar_themes(query, k=5):
    # Encode the query
    query_vector = model.encode([query])
    faiss.normalize_L2(query_vector)

    # Perform the search
    distances, indices = index.search(query_vector, k)

    # Return the results
    return [(themes[i], distances[0][j]) for j, i in enumerate(indices[0])]

# Example usage
query = "قصيدةالفراق"
results = find_similar_themes(query)
print(f"Query: {query}")
print("Similar themes:")
for theme, score in results:
    print(f"{theme}: {score:.4f}")
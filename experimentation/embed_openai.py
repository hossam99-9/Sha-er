from openai import OpenAI

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

client = OpenAI(api_key='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')

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

# Get embeddings for each theme
def get_embeddings(texts, model="text-embedding-3-small"):
   texts = (text.replace("\n", " ") for text in texts)
   return [client.embeddings.create(input = [text], model=model).data[0].embedding for text in texts]

# Generate embeddings for the themes
theme_embeddings = get_embeddings(themes)

# Function to find the closest theme
def find_closest_theme(input_text):
    # Get embedding for the input text
    input_embedding = get_embeddings([input_text])[0]

    # Calculate cosine similarity with all theme embeddings
    similarities = cosine_similarity([input_embedding], theme_embeddings)

    # Find the index of the highest similarity
    closest_index = np.argmax(similarities)
    return themes[closest_index], similarities[0][closest_index]

# Example usage
input_text = "قصيدة عن الحب"
closest_theme, similarity_score = find_closest_theme(input_text)

print(f"Closest theme: {closest_theme} with similarity score: {similarity_score:.4f}")

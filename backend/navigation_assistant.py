import os
import re
import psycopg2
import nltk
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

nltk.download('wordnet')

load_dotenv()

PGHOST = os.getenv("PGHOST")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
ENDPOINT = os.getenv('ENDPOINT')

conn = psycopg2.connect(
    host=PGHOST,
    database=PGDATABASE,
    user=PGUSER,
    password=PGPASSWORD,
    port=5432,
    sslmode="require",
    options=f"endpoint={ENDPOINT}"  # Fixes the SNI error
)
cursor = conn.cursor()

def get_synonyms(word):
    """
    Return a set of synonyms for a given word using NLTK WordNet.
    """
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().lower().replace('_', ' '))
    return synonyms

def expand_keywords(query):
    """
    Expand the user query by adding synonyms for each word.
    """
    words = re.findall(r'\w+', query.lower())
    expanded = set()
    for word in words:
        expanded.add(word)
        expanded.update(get_synonyms(word))
    return expanded

def search_table(input_query, table_name):
    """
    Searches for the best matching row in both tables using TF-IDF vectorization and cosine similarity between the expanded user query and the question.
    """
    expanded_keywords = expand_keywords(input_query)
    expanded_query = " ".join(expanded_keywords)
    
    if table_name == "faq_embeddings":
        cursor.execute("SELECT id, question, answer FROM faq_embeddings")
    elif table_name == "nav_assistant":
        cursor.execute("SELECT id, question, webpage FROM nav_assistant")
    else:
        return None, 0.0

    results = cursor.fetchall()
    if not results:
        return None, 0.0

    corpus = [row[1] for row in results]
    
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    query_vector = vectorizer.transform([expanded_query])
    
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    best_index = cosine_similarities.argmax()
    best_score = cosine_similarities[best_index]
    best_row = results[best_index]
    
    return best_row, best_score

def rag_and_nav_agent(input_query, threshold=0.1):
    """
    Returns the answer / webpage from the best matching row if the score is above the threshold.
    """
    faq_row, faq_score = search_table(input_query, "faq_embeddings")
    nav_row, nav_score = search_table(input_query, "nav_assistant")
    
    #Determine the best match between the two tables
    if faq_row and nav_row:
        if faq_score >= nav_score and faq_score >= threshold:
            return faq_row[2] 
        elif nav_score >= threshold:
            return f" You can find what you're looking for here: {nav_row[2]}"
    elif faq_row and faq_score >= threshold:
        return faq_row[2]
    elif nav_row and nav_score >= threshold:
        return nav_row[2]
    
    return "I'm sorry, I couldn't find an answer to that question."

if __name__ == "__main__":
    print("Hi! How may I assist you today?", end="\n\n")
    goAgain = True

    while goAgain:
        userInput = input()
        if userInput.lower() == 'no':
            goAgain = False
            break
        result = rag_and_nav_agent(userInput, 0.5)
        print(result)
        print("Is there anything else I can help you with?", end="\n\n")
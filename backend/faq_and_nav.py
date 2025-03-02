import os
import psycopg2
import re
from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

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
    options=f"endpoint={ENDPOINT}" 
)
cursor = conn.cursor()

kw_model = KeyBERT()

def extract_keywords(text, top_n=7):
    """
    Extract keywords using KeyBERT.
    """
    if not text:
        return ""
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english')
    return " ".join([kw[0] for kw in keywords])

def search_table(input_query, table_name):
    """
    Searches for the best matching row based on keywords then refines results with TF-IDF and cosine similarity.
    """
    query_keywords = extract_keywords(input_query)

    # Run PostgreSQL full-text search to filter relevant rows
    if table_name == "faq_embeddings":
        cursor.execute("""
            SELECT id, question, answer
            FROM faq_embeddings
            WHERE to_tsvector('english', question) @@ websearch_to_tsquery('english', %s)
            ORDER BY ts_rank(to_tsvector('english', question), websearch_to_tsquery('english', %s)) DESC
        """, (query_keywords, query_keywords))

    elif table_name == "nav_assistant":
        cursor.execute("""
            SELECT id, question, webpage
            FROM nav_assistant
            WHERE to_tsvector('english', question) @@ websearch_to_tsquery('english', %s)
            ORDER BY ts_rank(to_tsvector('english', question), websearch_to_tsquery('english', %s)) DESC
        """, (query_keywords, query_keywords))
    else:
        return None, 0.0

    results = cursor.fetchall()
    if not results:
        return None, 0.0

    questions = [row[1] for row in results]
    keyword_questions = [extract_keywords(q) for q in questions]

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(keyword_questions)

    query_vector = vectorizer.transform([query_keywords])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    best_index = cosine_similarities.argmax()
    best_score = cosine_similarities[best_index]
    best_row = results[best_index]

    return best_row, best_score

def rag_and_nav_agent(input_query, threshold=0.5):
    """
    Returns the best matching answer from either faq_embeddings or nav_assistant based on PostgreSQL full-text search
    followed by TF-IDF similarity scoring.
    """
    faq_row, faq_score = search_table(input_query, "faq_embeddings")
    nav_row, nav_score = search_table(input_query, "nav_assistant")
    
    # Determine best match
    if faq_row and nav_row:
        if faq_score >= nav_score and faq_score >= threshold:
            return faq_row[2] 
        elif nav_score >= threshold:
            return f"You can find what you're looking for here: {nav_row[2]}"
    elif faq_row and faq_score >= threshold:
        return faq_row[2]
    elif nav_row and nav_score >= threshold:
        return f"You can find what you're looking for here: {nav_row[2]}"
    
    return "I'm sorry, I couldn't find an answer to that question."

if __name__ == "__main__":
    print("Hi! How may I assist you today?", end="\n\n")
    goAgain = True

    while goAgain:
        userInput = input()
        if userInput.lower() == 'no':
            goAgain = False
            break
        result = rag_and_nav_agent(userInput, 0.2)
        print(result)
        print("Is there anything else I can help you with?", end="\n\n")

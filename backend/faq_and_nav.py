import os
import psycopg2
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

def extract_keywords_tfidf(text, top_n=7):
    """
    Extracts top N keywords from the text using TF-IDF.
    """
    if not text:
        return ""

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([text])

    feature_array = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]

    top_indices = tfidf_scores.argsort()[-top_n:][::-1]
    keywords = [feature_array[i] for i in top_indices]

    return " ".join(keywords)  

def search_table(input_query, is_faq):
    """
    Searches for the best matching row based on keywords and refines results with TF-IDF and cosine similarity.
    """
    query_keywords = extract_keywords_tfidf(input_query)

    cursor.execute("""
        SELECT id, question, answer, link, faq
        FROM faq_embeddings
        WHERE faq::INTEGER = %s
        AND to_tsvector('english', question) @@ websearch_to_tsquery('english', %s)
        ORDER BY ts_rank(to_tsvector('english', question), websearch_to_tsquery('english', %s)) DESC
    """, (is_faq, query_keywords, query_keywords))

    results = cursor.fetchall()
    if not results:
        return None, 0.0

    questions = [row[1] for row in results]

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(questions)
    
    query_vector = vectorizer.transform([query_keywords])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    
    best_index = cosine_similarities.argmax()
    best_score = cosine_similarities[best_index]
    best_row = results[best_index]

    return best_row, best_score

def rag_and_nav_agent(input_query, threshold=0.5):
    """
    Returns the best matching answer from the `faq_embeddings` table.
    Determines if the best match is from FAQ (faq=1) or Navigation (faq=0).
    """
    tmpID = "5e655314-c264-4999-83ad-67c43cc6db5b"  
    faq_row, faq_score = search_table(input_query, 1) 
    nav_row, nav_score = search_table(input_query, 0)
    
    if faq_row and faq_score >= threshold:
        response = f"Answer: {faq_row[2]}" 
        if faq_row[3]:  
            response += f"\nYou can find more information here: {faq_row[3]}"
        return response
    
    elif nav_row and nav_score >= threshold:
        return f"{nav_row[2]}\nhttp://localhost:5173/details/{tmpID}/{nav_row[3]}" 
    
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

import os
import psycopg2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from utils.database import connection_pool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

def search_table_once(table_name):
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor()
        if table_name == "faq_embeddings":
            cursor.execute("SELECT id, question, answer FROM faq_embeddings")
        else:
            return None, None, None
        results = cursor.fetchall()
        if not results:
            return None, None, None
        corpus = ['' if row[1] is None else row[1] for row in results]
        vector_store = FAISS.from_texts(texts=corpus, embedding=embeddings)
        return corpus, vector_store, results
    finally:
        connection_pool.putconn(conn)

def embedding_and_similarity_search(input_query, corpus, vector_store, results):
    query_embedding = embeddings.embed_query(input_query)
    answer = vector_store.similarity_search_by_vector(query_embedding, 1)
    question = answer[0].page_content
    answers = dict(zip(corpus, results))
    return answers[question][2]

def extract_keywords_tfidf(text, top_n=7):
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
    query_keywords = extract_keywords_tfidf(input_query)
    conn = connection_pool.getconn()
    try:
        cursor = conn.cursor()
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
    finally:
        connection_pool.putconn(conn)

def rag_and_nav_agent(input_query, frontend_url="", threshold=0.5):
    faq_row, faq_score = search_table(input_query, 1)
    nav_row, nav_score = search_table(input_query, 0)
    if faq_row and faq_score >= threshold:
        response = f"{faq_row[2]}"
        if faq_row[3]:
            response += f"\nYou can find more information [here]({faq_row[3]})"
        return response
    elif nav_row and nav_score >= threshold:
        return f"You can find this information [here]({nav_row[3]})"
    return "I'm sorry, I couldn't find an answer to that question."

if __name__ == "__main__":
    userInput = input("(1) tfidf or (2) similarity search w/ embeddings: ")
    if userInput == '2':
        corpus, vector_store, results = search_table_once("faq_embeddings")
        if not corpus:
            print("Could not load data.")
        else:
            print("Hi, you are now using similarity search! How may I assist you today?\n")
            while True:
                userInput = input()
                if userInput.lower() == 'no':
                    break
                result = embedding_and_similarity_search(userInput, corpus, vector_store, results)
                print(result)
                print("Is there anything else I can help you with?\n")
    else:
        print("Hi, you are now using TF-IDF! How may I assist you today?\n")
        while True:
            userInput = input()
            if userInput.lower() == 'no':
                break
            result = rag_and_nav_agent(userInput)
            print(result)
            print("Is there anything else I can help you with?\n")

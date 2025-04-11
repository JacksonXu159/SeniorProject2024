from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from database import connection_pool
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

load_dotenv()

embeddings = OpenAIEmbeddings()

def summarize_article(text):
    """Summarizes the article to make it short and chat-friendly."""
    summary_prompt = f"Summarize the following article in 3-5 sentences, sounding professional:\n\n{text}"
    return llm.invoke(summary_prompt).content


def financial_advisor_agent(input_query, threshold=0.5):
    """
    Retrieves financial advice from the database based on semantic similarity and returns a professional response.
    """
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()

        query_embedding = embeddings.embed_query(input_query)

        cursor.execute("""
            SELECT title, article, link, embedding <=> %s::vector AS distance
            FROM vanguard_knowledge_base
            ORDER BY embedding <=> %s::vector
            LIMIT 1
        """, (query_embedding, query_embedding))


        result = cursor.fetchone()

        cursor.close()
        connection_pool.putconn(conn)

        if result:
            title, article, link, distance = result
            article = summarize_article(article)

            advisor_response = (
                f"**Financial Advisor Insights**\n\n"
                f"**{title}**\n\n"
                f"{article}\n\n"
                f"[Click here to learn more.]({link})\n\n"
                f"---\n"
                f"*As your financial advisor, remember that your individual situation may vary. "
                f"For personal advice, please consult with a certified professional.*"
            )

            if distance <= threshold:
                return advisor_response
            else:
                return f"(Low confidence, but here’s the best match)\n\n{advisor_response}"

        else:
            return "I'm sorry, I couldn't find any related information."

    except Exception as e:
        print(f"Error in financial_advisor_agent: {e}")
        return "I'm sorry, something went wrong while retrieving the information."

if __name__ == "__main__":
    # quick manual test
    user_question = input("Ask your financial question: ")
    response = financial_advisor_agent(user_question)
    print("\nResponse:\n")
    print(response)

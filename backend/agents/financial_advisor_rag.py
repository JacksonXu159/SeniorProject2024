from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from utils.database import connection_pool
from langchain_openai import ChatOpenAI
from utils.queries import get_user_info
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

load_dotenv()

embeddings = OpenAIEmbeddings()

def personalize_financial_query(input_query, user_id):
    user_data = get_user_info(user_id)
    user_profile = ""
    if not user_data:
        return input_query
    print(user_data)
    portfolio_info = "\n".join([f"- {p['portfolioType']}: ${p['balance']:,.2f}" for p in user_data.get("portfolios", [])])
    user_profile = f"""This is the user's profile:
- Name: {user_data["accountName"]}
- Age: {user_data["age"]}
- Gender: {user_data["gender"]}
- Balance: {user_data["totalBalance"]:,.2f}
- Risk Tolerance: {user_data["risktolerance"]}
- Marital Status: {user_data["maritalstatus"]}
- Tax Filing Status: {user_data["taxFilingStatus"]}
- Income Bracket: {user_data["taxFilingIncomeBracket"]}
- Tax Filing State: {user_data["taxFilingState"]}
- Estimated Retirement Age: {user_data["estimatedRetirementAge"]}
- Spending Variation Tolerance: {user_data["spendingVariationTolerance"]}
- Short-Term Loss Sensitivity: {user_data["shortTermLossSensitivity"]}
-Portfolios:
{portfolio_info}
Use this data to provide finanical advice and answer their question"""

    return f"{input_query}\n\n{user_profile}"

def summarize_article(text):
    """Summarizes the article to make it short and chat-friendly."""
    summary_prompt = f"Summarize the following article in 2-4 sentences, make it short, concise, and sounds professional:\n\n{text}"
    return llm.invoke(summary_prompt).content

def generate_financial_advice(text, user_profile):
    prompt = f"""
    Based on the following financial article, provide **actionable financial advice** tailored to this user's profile.
    **Article:** {text}

    **User Profile:**
    {user_profile}

    Focus on their **risk tolerance** (low, medium, high) and balance. Suggest VANGUARD ETFs or strategies, but avoid specific stock picks. Keep it **short, clear, professional**, and under 350 characters.
    """
    return llm.invoke(prompt).content

def financial_advisor_agent(input_query, user_id, threshold=0.5):
    """
    Retrieves financial advice from the database based on semantic similarity and returns a professional response.
    """
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()

        personalized_query = personalize_financial_query(input_query, user_id)

        query_embedding = embeddings.embed_query(personalized_query)

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
            advice = generate_financial_advice(article, personalize_financial_query)

            advisor_response = (
                f"**Financial Advisor Insights**\n\n"
                f"Potential Advice: {advice}\n\n"
                f"Here is a summary of an article related to your question:\n"
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
    user_question = input("Ask your financial question:\n")
    response = financial_advisor_agent(user_question)
    print("\nResponse:\n")
    print(response)

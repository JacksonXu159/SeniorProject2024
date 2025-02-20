import os
import asyncio
import psycopg2
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import (
    create_openai_functions_agent,
    AgentExecutor,
)
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from agents.assistant import assistant_chain

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

PGHOST = os.getenv('PGHOST')
PGDATABASE = os.getenv('PGDATABASE')
PGUSER = os.getenv('PGUSER')
PGPASSWORD = os.getenv('PGPASSWORD')

conn = psycopg2.connect(
    host=PGHOST,
    database=PGDATABASE,
    user=PGUSER,
    password=PGPASSWORD,
    port=5432,
    sslmode='require'  
)

cursor = conn.cursor()

def get_user_data(account_id: str):
    """Fetch user account details including balance, marital status, risk tolerance, and portfolio details."""
    cursor.execute("""
        SELECT accountname, gender, age, risktolerance, maritalstatus
        FROM Accounts
        WHERE accountID = %s
    """, (account_id,))
    account_data = cursor.fetchone()
    
    cursor.execute("""
        SELECT SUM(balance) FROM Portfolio WHERE accountID = %s
    """, (account_id,))
    total_balance = cursor.fetchone()[0] or 0.0
    
    cursor.execute("""
        SELECT portfolioType, balance FROM Portfolio WHERE accountID = %s
    """, (account_id,))
    portfolios = cursor.fetchall()
    
    return {
        "accountName": account_data[0],
        "gender": account_data[1],
        "age": account_data[2],
        "risktolerance": account_data[3],
        "maritalstatus": account_data[4],
        "totalBalance": total_balance,
        "portfolios": [{"portfolioType": p[0], "balance": p[1]} for p in portfolios]
    }

def user_data_agent_func(account_id: str, query: str):
    """Respond to user queries related to their account information."""
    user_data = get_user_data(account_id)
    
    normalized_query = query.lower().replace('_', ' ')
    
    if "balance" in normalized_query:
        return f"Your total balance is ${user_data['totalBalance']:.2f}."
    if "marital" in normalized_query and "status" in normalized_query:
        return f"Your marital status is {user_data['maritalstatus']}."
    if "portfolio" in normalized_query:
        portfolios_info = "\n".join([f"{p['portfolioType']}: ${p['balance']:.2f}" for p in user_data['portfolios']])
        return f"Here are your portfolios:\n{portfolios_info}"
    if "risk" in normalized_query and "tolerance" in normalized_query:
        return f"Your risk tolerance level is {user_data['risktolerance']}."
    return "I'm sorry, I couldn't find an answer to that question."


tmpID = "5e655314-c264-4999-83ad-67c43cc6db5b"
tools = [
    Tool(
        name="UserDataLookup",
        func=lambda query: user_data_agent_func(tmpID, query),
        description="""Useful for retrieving:
        - balance (query with 'balance')
        - marital status (query with 'marital status')
        - portfolios (query with 'portfolios')
        - risk tolerance (query with 'risk tolerance')"""
    ),
    Tool(
        name="Consultant",
        func=assistant_chain.invoke,
        description="""Useful when you need to answer general finance-related questions. 
        Not useful for any data or user-specific questions such as account balance, statements,
        user's investments, etc."""
    )
]

chatbot_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful chatbot assistant"),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)

chat_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

chatbot_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=chatbot_agent_prompt,
    tools=tools,
)

chatbot_agent_executor = AgentExecutor(
    agent=chatbot_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
)

async def main():
    input_data = {"input": "what is my user id"}
    result = await chatbot_agent_executor.ainvoke(input_data)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

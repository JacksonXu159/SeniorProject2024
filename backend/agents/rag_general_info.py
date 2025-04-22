import os
import asyncio
import openai
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
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.assistant import assistant_chain
from dotenv import load_dotenv
from utils.queries import (
    get_user_info,
    get_user_balance,
    get_user_services,
    add_service,
    remove_service
)

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")


def user_data_agent_func(account_id: str, query: str):
    user_data = get_user_info(account_id)
    
    print(query)
    intents = {
        "balance": lambda: f"Your total balance is ${user_data['totalBalance']:.2f}.",
        "marital status": lambda: f"Your marital status is {user_data['maritalstatus']}.",
        "portfolio": lambda: "\n".join([f"{p['portfolioType']}: ${p['balance']:.2f}" for p in user_data['portfolios']]),
        "risk tolerance": lambda: f"Your risk tolerance level is {user_data['risktolerance']}.",
        "services": lambda: "Your services are: " + ", ".join(user_data['services']) if user_data['services'] else "You are not subscribed to any services."
    }

    normalized_query = query.lower()
    for key in intents.keys():
        if key in normalized_query:
            print(f"Exact match intent: {key}, returning result.")
            return intents[key]() 
    
    return "I'm sorry, I couldn't find an answer to that question."

    # documents = [Document(page_content=intent, metadata={"action": intent}) for intent in intents]
    # embeddings = OpenAIEmbeddings()
    # vector_store = FAISS.from_documents(documents, embeddings)

    # similar_docs_with_scores = vector_store.similarity_search_with_score(query, k=1)
    
    # if similar_docs_with_scores:
    #     best_doc, best_score = similar_docs_with_scores[0]
    #     best_intent = best_doc.metadata["action"]
        
    #     print(f"Similarity score for '{best_intent}': {best_score:.4f}")
        
    #     return intents[best_intent]()
    # else:
    #     print("No suitable match found.")
    #     return "I'm sorry, I couldn't find an answer to that question."


def user_services_agent_func(account_id: str, query: str):
    """Respond to the user queries regarding services they have."""

    services = get_user_services(account_id)
    normalized_query = query.lower()

    list_words = ["list", "what", "which", "subscribed"]
    add_words = ["add", "subcribe", "enroll", "get", "buy", "apply", "start"]
    remove_words = ["remove", "unsubscribe", "cancel", "stop", "end", "terminate", "drop"]

    services_dict = {
        "Financial Planning" : "https://investor.vanguard.com/advice/personal-financial-advisor",
        "Retirement Planning" : "https://investor.vanguard.com/investor-resources-education/retirement",
        "Investment Management" : "https://investor.vanguard.com/advice",
        "Wealth Management" : "https://investor.vanguard.com/wealth-management/personal-advisor-wealth-management",
        "Self-Managed" : "https://www.vanguard.com/"
    }

    current_service = None

    for service in services_dict.keys():
        if service.lower() in normalized_query:
            current_service=service

    if not services:
        services_str = '\n'.join([f"{service}: {link}" for service, link in services_dict.items()])
        return f"You currently do not have any services.\nHere are all the possible services and the links to them:\n{services_str}"
    
    if any(word in normalized_query for word in list_words):
        services_list = ", ".join(services)
        return f"You are subscribed to the following services: {services_list}."
    elif any(word in normalized_query for word in add_words):
        if current_service is not None:
            return f"To add the {current_service}, please visit our {services_dict[current_service]} for more information or contact customer support"
        return f"To add a new service, please visit our website or contact customer support."
    elif any(word in normalized_query for word in remove_words):
        if current_service is not None:
            return f"To remove the {current_service}, please visit our {services_dict[current_service]} for more information or contact customer support"
        return f"To add a remove service, please visit our website or contact customer support."
    else:
        return "I'm here to help you with any inquires regarding your services. Could you please clarify your request?"
    


tmpID = "5e655314-c264-4999-83ad-67c43cc6db5b"
tools = [
    Tool(
        name="UserDataLookup",
        func=lambda query: user_data_agent_func(tmpID, query),
        description="""Useful for retrieving:
        - balance (query with 'balance')
        - marital status (query with 'marital status')
        - portfolios (query with 'portfolios')
        - risk tolerance (query with 'risk tolerance')
        - services (query with 'services')"""
    ),
    # Tool(
    #     name="Consultant",
    #     func=assistant_chain.invoke,
    #     description="""Useful when you need to answer general finance-related questions. 
    #     Not useful for any data or user-specific questions such as account balance, statements,
    #     user's investments, etc."""
    # ),
    # Tool(
    #     name="UserServicesLookup",
    #     func=lambda query: user_services_agent_func(tmpID, query),
    #     description="""User for handling queries related to services or the services the user has.
    #     Examples:
    #     - List services
    #     - Adding Services
    #     - Removing Services
    #     """
    # ),
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


def test_service():
    test_queries = [
        "whats my money, can i afford a dog?",
        # "I want to subscribe to Financial Planning",
        # "How can I unsubscribe from Investment Management?",
        # "List all my services",
        # "Remove my subscription to Retirement Planning"
    ]
    for query in test_queries:
        result = asyncio.run(chatbot_agent_executor.ainvoke({"input": query}))
        print(f"Query: {query}\nResponse: {result['output']}\n")


if __name__ == "__main__":
    test_service()
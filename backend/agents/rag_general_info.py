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
from agents.assistant import assistant_chain
from dotenv import load_dotenv
from queries import (
    get_user_info,
    get_user_balance,
    get_user_services,
    add_service,
    remove_service
)
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

services_intent_ex = {
    "list_services": [
        "What services do I have?",
        "Show me my subscriptions",
        "Which services am I using?",
        "List all my services"
    ],
    "add_service": [
        "I want to add a new service",
        "How do I subscribe to Financial Planning?",
        "Can I enroll in Wealth Management?",
        "Sign me up for Retirement Planning"
    ],
    "remove_service": [
        "How do I cancel my subscription?",
        "I want to unsubscribe from Investment Management",
        "Remove my service",
        "Stop my Retirement Planning subscription"
    ]
}

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.expand_dims(response.data[0].embedding, axis=0) 

def embedd_intent(intent_dict):
    embedded_intent = {
        intent: [get_embedding(example) for example in examples] for intent, examples in intent_dict.items()
    }
    return embedded_intent

def get_intent_from_query(query, intent_embeddings):
    query_embedding = get_embedding(query)
    query_embedding = np.array(query_embedding).reshape(1, -1)

    best_intent = None
    best_similarity = -1

    for intent, embeddings in intent_embeddings.items():
        for current_embedding in embeddings:
            similarity = cosine_similarity(query_embedding, current_embedding)[0][0]
            if similarity > best_similarity:
                best_similarity = similarity
                best_intent = intent

    return best_intent

services_intent_embeddings = embedd_intent(services_intent_ex)


def user_data_agent_func(account_id: str, query: str):
    """Respond to user queries related to their account information."""
    user_data = get_user_info(account_id)

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

def user_services_agent_func(account_id: str, query: str):
    """Respond to the user queries regarding services they have."""

    services = get_user_services(account_id)
    intent = get_intent_from_query(query, services_intent_embeddings)
    normalized_query = query.lower()

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
    
    if intent=="list_services":
        services_list = ", ".join(services)
        return f"You are subscribed to the following services: {services_list}."
    elif intent=="add_service":
        if current_service is not None:
            return f"To add the {current_service}, please visit our {services_dict[current_service]} for more information or contact customer support"
        return f"To add a new service, please visit our website or contact customer support."
    elif intent=="remove_service":
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
        - risk tolerance (query with 'risk tolerance')"""
    ),
    Tool(
        name="Consultant",
        func=assistant_chain.invoke,
        description="""Useful when you need to answer general finance-related questions. 
        Not useful for any data or user-specific questions such as account balance, statements,
        user's investments, etc."""
    ),
    Tool(
        name="UserServicesLookup",
        func=lambda query: user_services_agent_func(tmpID, query),
        description="""User for handling queries related to services or the services the user has.
        Examples:
        - List services
        - Adding Services
        - Removing Services
        """
    ),
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
        "What services am I subscribed to?",
        "I want to subscribe to Financial Planning",
        "How can I unsubscribe from Investment Management?",
        "List all my services",
        "Remove my subscription to Retirement Planning"
    ]
    for query in test_queries:
        result = asyncio.run(chatbot_agent_executor.ainvoke({"input": query}))
        print(f"Query: {query}\nResponse: {result['output']}\n")


if __name__ == "__main__":
    test_service()
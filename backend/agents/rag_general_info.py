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

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

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
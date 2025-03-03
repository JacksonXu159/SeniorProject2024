import os
import asyncio
from langchain.agents import Tool
from langchain_openai import ChatOpenAI
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agents.assistant import assistant_chain

from agents.rag_general_info import user_data_agent_func, user_services_agent_func

from faq_and_nav import rag_and_nav_agent

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")
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
    Tool(
        name="NavAndFaq",
        func=lambda query: rag_and_nav_agent(query, 0.5),
        description="""User for handling queries related where services are located or finace related questions.
        Examples:
        - Where are my transactions?
        - What are stocks?
        """
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
    input_data = {"input": "What are bonds?"}
    result = await chatbot_agent_executor.ainvoke(input_data)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

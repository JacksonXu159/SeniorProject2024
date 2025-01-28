import os
import asyncio
from langchain.agents import Tool
from langchain_community.chat_models import ChatOpenAI
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

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

tools = [
    Tool(
        name="Consultant",
        func=assistant_chain.invoke,
        description="""Useful when you need to answer general finance related questions. 
        not useful for any data or user specific questions such as account balance, statements,
        user's investments and etc. Pass the entire question as input to the tool. For intance,
        if the question is "What are stocks and how they work?", the input should be "What are stocks and how they work?"
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

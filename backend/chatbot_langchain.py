import os
from langchain_openai import ChatOpenAI
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from financial_advisor_rag import financial_advisor_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agents.rag_general_info import user_data_agent_func

from faq_and_nav import rag_and_nav_agent

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

current_user_id = "5e655314-c264-4999-83ad-67c43cc6db5b"  # Default ID

def set_user_id(user_id):
    """Update the current user ID"""
    global current_user_id
    current_user_id = user_id
    return current_user_id

def get_current_user_id():
    """Get the current user ID"""
    global current_user_id
    return current_user_id

def get_user_id_from_input(input_data=None):
    """Gets user ID from input data or falls back to current user ID"""
    if input_data and "userId" in input_data:
        return input_data.get("userId")
    return get_current_user_id()

tools = [
    Tool(
        name="UserDataLookup",
        func=lambda query: user_data_agent_func(current_user_id, query),
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
    Tool(
        name="NavAndFaq",
        func=lambda query: rag_and_nav_agent(query, 0.5),
        return_direct=True,
        description="""Use for **navigational or FAQ-related questions only**.
    Examples:
    - Where are my transactions?
    - How do I view my account statements?
    - Where can I update my profile?
    - What are stocks?
    - How does investing work?
    - What is a mutual fund?
    **Do NOT use for personalized financial advice or investment strategies** (e.g., IRA tax benefits, portfolio allocation)**
    """
    ),
    Tool(
        name="FinancialAdvisorLookup",
        func=lambda query: financial_advisor_agent(query),
        return_direct=True,
        description="""Use for **advanced financial concepts and personalized investment strategy such as: **.
    - diversification
    - expense ratios
    - IRA contributions
    - retirement withdrawals
    - risk tolerance
    - Roth IRA vs Traditional IRA
    - investment strategy that best fits my risk tolerence
    **Do NOT use for general finance definitions** like "What are stocks?" or "How does investing work?"
    **Do NOT give specific stock picks or trading recommendations.**    """
    )
]
chatbot_agent_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful chatbot assistant."),
        ("system", "Here is the conversation history so far: {chat_history}"),
        MessagesPlaceholder("chat_history"),
        ("human", "User said previously: {chat_history}. Now the user says: {input}"),
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
    tool_kwargs={"input_data": lambda x: x}
)

# for testing only
async def main():
    print("Starting multi-question chatbot test...\n")

    chat_history = []

    # List of user questions to simulate
    user_questions = [
        "How do I save for retirement?",                    # FinancialAdvisorLookup
        "What is my current balance?",                      # UserDataLookup
        "Where can I find my transaction history?",         # NavAndFaq
        "What is a Roth IRA?"                               # FinancialAdvisorLookup again
    ]

    for user_input in user_questions:
        input_data = {
            "input": user_input,
            "chat_history": chat_history
        }

        print(f"\nUser: {user_input}")

        result = await chatbot_agent_executor.ainvoke(input_data)

        print("\nBot:")
        print(result["output"])

        # Append this exchange to chat history
        chat_history.append({"role": "human", "content": user_input})
        chat_history.append({"role": "ai", "content": result["output"]})

        # Show intermediate steps
        print("\nIntermediate Steps (Tools Used):")
        for idx, step in enumerate(result["intermediate_steps"], 1):
            print(f"Step {idx}: {step}")

    print("\nMulti-question chatbot test complete.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

import os
from langchain_openai import ChatOpenAI
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agents.financial_advisor_rag import financial_advisor_agent
from agents.rag_general_info import user_data_agent_func
from agents.faq_and_nav import rag_and_nav_agent

from langchain.callbacks.base import AsyncCallbackHandler

class WebSocketStreamHandler(AsyncCallbackHandler):
    def __init__(self, websocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs):
        """Handle new token from LLM"""
        try:
            await self.websocket.send_text(token)
        except Exception as e:
            print(f"Error sending token: {e}")

    async def on_llm_end(self, response, **kwargs):
        """Handle end of LLM response"""
        try:
            await self.websocket.send_text("[END]")
        except Exception as e:
            print(f"Error sending end token: {e}")

class ChatbotLangchain:
    def __init__(self):
        self.current_user_id = "5e655314-c264-4999-83ad-67c43cc6db5b"  # Default ID
        self.CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")
        
        # Initialize tools
        self.tools = [
            Tool(
                name="UserDataLookup",
                func=lambda query: self._user_data_agent_wrapper(query),
                description="""Useful for retrieving:
                - balance (query with 'balance')
                - marital status (query with 'marital status')
                - portfolios (query with 'portfolios')
                - risk tolerance (query with 'risk tolerance')
                - services (query with 'services')"""
            ),
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
                func=lambda query: financial_advisor_agent(query, self.current_user_id),
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
        
        # Initialize prompt template
        self.chatbot_agent_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful chatbot assistant."),
                ("system", "Here is the conversation history so far: {chat_history}"),
                MessagesPlaceholder("chat_history"),
                ("human", "User said previously: {chat_history}. Now the user says: {input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        
        # Initialize chat model
        self.chat_model = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)
        
        # Create agent and executor
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the agent and agent executor"""
        self.chatbot_agent = create_openai_functions_agent(
            llm=self.chat_model,
            prompt=self.chatbot_agent_prompt,
            tools=self.tools,
        )
        
        self.chatbot_agent_executor = AgentExecutor(
            agent=self.chatbot_agent,
            tools=self.tools,
            return_intermediate_steps=True,
            verbose=True,
            tool_kwargs={"input_data": lambda x: x}
        )
    
    def set_user_id(self, user_id):
        """Update the current user ID"""
        self.current_user_id = user_id
        return self.current_user_id
    
    def get_current_user_id(self):
        """Get the current user ID"""
        return self.current_user_id
    
    def get_user_id_from_input(self, input_data=None):
        """Gets user ID from input data or falls back to current user ID"""
        if input_data and "userId" in input_data:
            return input_data.get("userId")
        return self.get_current_user_id()
    
    def _user_data_agent_wrapper(self, query):
        """Wrapper for the user data agent to use the current user ID"""
        return user_data_agent_func(self.current_user_id, query)
    
    async def ainvoke(self, input_data):
        """Async invocation of the agent executor"""
        return await self.chatbot_agent_executor.ainvoke(input_data)
    
    def invoke(self, input_data):
        """Synchronous invocation of the agent executor"""
        return self.chatbot_agent_executor.invoke(input_data)


# for testing only
async def main():
    print("Starting multi-question chatbot test...\n")
    
    chatbot = ChatbotLangchain()
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

        result = await chatbot.ainvoke(input_data)

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
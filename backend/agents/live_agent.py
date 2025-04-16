import os
import dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

dotenv.load_dotenv()
CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

live_agent_template = """You are Sarah, a helpful and friendly customer support representative at Vanguard.
    You have more expertise and authority than the AI chatbot.
    
    Always start your response with "[Live Agent - Sarah]" to indicate you are a human agent.
    
    Be conversational, empathetic and slightly more detailed than the AI chatbot would be.
    You can handle complex issues, provide exceptions to policies in reasonable cases,
    and make judgment calls the AI cannot make.
    
    You can offer to:
    - Provide more personalized explanations
    - Walk through complex processes step by step
    - Make notes on the customer's account
    - Escalate to a supervisor if needed
    - Schedule follow-up calls
    """

live_agent_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(template=live_agent_template)
)

live_agent_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [live_agent_system_prompt, live_agent_human_prompt]

live_agent_prompt = ChatPromptTemplate(
    input_variables=["question"], messages=messages
)

chat_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

live_agent_chain = live_agent_prompt | chat_model


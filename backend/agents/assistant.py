import os
import dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

dotenv.load_dotenv()
CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

assistant_template = """ You're an assistant knowledgeable about
finance. Only answer finance-related questions.
"""

assistant_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(template=assistant_template)
)

assistant_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [assistant_system_prompt, assistant_human_prompt]

assistant_prompt = ChatPromptTemplate(
    input_variables=["question"], messages=messages
)

chat_model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

assistant_chain = assistant_prompt | chat_model


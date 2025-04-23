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


class LiveAgentChat:
    def __init__(self):
        self.model_name = os.getenv("CHATBOT_AGENT_MODEL", "gpt-4o-mini")

        live_agent_template = """You are Sarah, a helpful and friendly customer support representative at Vanguard.
You have more expertise and authority than the AI chatbot.

Always start your response with "**Live Agent - Sarah**" to indicate you are a human agent.

Be conversational, empathetic and slightly more detailed than the AI chatbot would be.
You can handle complex issues, provide exceptions to policies in reasonable cases,
and make judgment calls the AI cannot make.

You can offer to:
- Provide more personalized explanations
- Walk through complex processes step by step
- Make notes on the customer's account
- Escalate to a supervisor if needed
- Schedule follow-up calls

Context:
- User ID: {userId}
- Frontend URL: {frontendUrl}
"""

        self.system_prompt = SystemMessagePromptTemplate(
            prompt=PromptTemplate(
                template=live_agent_template,
                input_variables=["userId", "frontendUrl"]
            )
        )

        self.human_prompt = HumanMessagePromptTemplate(
            prompt=PromptTemplate(
                input_variables=["input"], template="{input}"
            )
        )

        self.chat_prompt = ChatPromptTemplate(
            input_variables=["input", "frontendUrl", "userId"],
            messages=[self.system_prompt, self.human_prompt]
        )

        self.chain = self.chat_prompt | ChatOpenAI(model=self.model_name, temperature=0)

    def invoke(self, input_data: dict):
        result = self.chain.invoke({
            "input": input_data["input"],
            "frontendUrl": input_data["frontendUrl"],
            "userId": input_data["userId"],
        })
        return {"output": result.content}


import os
os.environ["OPENAI_API_KEY"] = "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"
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# create LLM and memory components
llm = ChatOpenAI(temperature=0.0)
memory = ConversationBufferMemory()

# create a conversation chain with these components

conversation = ConversationChain(
    llm=llm, 
    memory=memory
)


conversation.predict(input="Tomorrow is my friend's birthday. His name is John.")


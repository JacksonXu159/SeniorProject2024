import os
import asyncio
import numpy as np
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
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.assistant import assistant_chain
from dotenv import load_dotenv
from utils.queries import (
    get_user_info,
    get_user_services,
)

from langchain_openai import OpenAIEmbeddings

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

CHATBOT_AGENT_MODEL = os.getenv("CHATBOT_AGENT_MODEL")

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

intents = {
    "account name": {
        "phrases": ["account name", "what is my name", "name on file"],
        "response": lambda u: f"Your name is {u['accountName']}."
    },
    "balance": {
        "phrases": ["balance", "account balance", "how much money do i have", "total balance"],
        "response": lambda u: f"Your total balance is ${u['totalBalance']:.2f}."
    },
    "marital status": {
        "phrases": ["marital status", "relationship status", "am i married"],
        "response": lambda u: f"Your marital status is {u['maritalstatus']}."
    },
    "portfolio": {
        "phrases": ["portfolio", "investments", "my assets"],
        "response": lambda u: "\n".join([f"{p['portfolioType']}: ${p['balance']:.2f}" for p in u['portfolios']])
    },
    "risk tolerance": {
        "phrases": ["risk tolerance", "risk appetite", "how much risk can i take"],
        "response": lambda u: f"Your risk tolerance level is {u['risktolerance']}."
    },
    "tax filing status": {
        "phrases": ["tax filing status", "filing status"],
        "response": lambda u: f"Your tax filing status is {u['taxFilingStatus']}."
    },
    "tax filing income bracket": {
        "phrases": [
            "tax filing income bracket",
            "tax bracket",
            "income bracket",
            "tax income bracket",
            "bracket"
        ],
        "response": lambda u: f"Your tax filing income bracket is {u['taxFilingIncomeBracket']}."
    },
    "tax filing state": {
        "phrases": ["tax filing state", "filing state", "state of filling taxes", "tax state"],
        "response": lambda u: f"Your tax filing state is {u['taxFilingState']}."
    },
    "estimated retirement age": {
        "phrases": ["estimated retirement age", "when will i retire", "retirement age", "how old will i be when i retire"],
        "response": lambda u: f"Your estimated retirement age is {u['estimatedRetirementAge']}."
    },
    "spending variation tolerance": {
        "phrases": ["spending variation tolerance", "spending tolerance", "vartion of spending tolerance", "spending tolerance variation"],
        "response": lambda u: f"Your spending variation tolerance is {u['spendingVariationTolerance']}."
    },
    "short-term loss sensitivity": {
        "phrases": ["short-term loss sensitivity", "short term loss sensitivity", "sensitivity to short-term losses", "sensitivity to short term losses", "loss sensitivity short term","loss sensitivity short-term"],
        "response": lambda u: f"Your short-term loss sensitivity is {u['shortTermLossSensitivity']}."
    },
    "services": {
        "phrases": ["services", "subscribed services", "my services"],
        "response": lambda u: "Your services are: " + ", ".join(u['services']) if u['services'] else "You are not subscribed to any services."
    }
}

phrases = []
phrases_to_intent = {}
for intent_key, intent_info in intents.items():
    for phrase in intent_info["phrases"]:
        phrases.append(phrase)
        phrases_to_intent[phrase] = intent_key

PHRASE_EMBEDDINGS = embeddings_model.embed_documents(phrases)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def user_data_agent_func(account_id: str, query: str):
    user_data = get_user_info(account_id)

    query_embedding = embeddings_model.embed_query(query)

    best_score = -1
    best_phrase = None
    for i, phrase_embedding in enumerate(PHRASE_EMBEDDINGS):
        score = cosine_similarity(query_embedding, phrase_embedding)
        if score > best_score:
            best_score = score
            best_phrase = phrases[i]

    if best_score > 0.65:
        intent_key = phrases_to_intent[best_phrase]
        response_func = intents[intent_key]["response"]
        return response_func(user_data)
    
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
        - risk tolerance (query with 'risk tolerance')
        - services (query with 'services')
        - account name (query with 'account name', 'my name', 'profile name')
        - gender (query with 'gender') — response restricted for privacy
        - age (query with 'age', 'how old') — response restricted for privacy
        - tax filing status (query with 'tax filing status', 'filing status')
        - tax income bracket (query with 'tax income bracket', 'income bracket', 'tax bracket')
        - tax filing state (query with 'tax state', 'tax filing state')
        - estimated retirement age (query with 'retirement age', 'estimate retirement')
        - spending variation tolerance (query with 'spending variation', 'spending tolerance')
        - short-term loss sensitivity (query with 'loss sensitivity', 'short-term loss tolerance')"""
    ),
    # Tool(
    #     name="Consultant",
    #     func=assistant_chain.invoke,
    #     description="""Useful when you need to answer general finance-related questions. 
    #     Not useful for any data or user-specific questions such as account balance, statements,
    #     user's investments, etc."""
    # ),
    # Tool(
    #     name="UserServicesLookup",
    #     func=lambda query: user_services_agent_func(tmpID, query),
    #     description="""User for handling queries related to services or the services the user has.
    #     Examples:
    #     - List services
    #     - Adding Services
    #     - Removing Services
    #     """
    # ),
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

# def user_data_agent_func(account_id: str, query: str):
#     user_data = get_user_info(account_id)

    
#     print(query)
#     intents = {
#         "account name": lambda: f"Your name is {user_data['accountName']}.",
#         "balance": lambda: f"Your total balance is ${user_data['totalBalance']:.2f}.",
#         "marital status": lambda: f"Your marital status is {user_data['maritalstatus']}.",
#         "portfolio": lambda: "\n".join([f"{p['portfolioType']}: ${p['balance']:.2f}" for p in user_data['portfolios']]),
#         "risk tolerance": lambda: f"Your risk tolerance level is {user_data['risktolerance']}.",
#         "tax filing status": lambda: f"Your tax filing status is {user_data['taxFilingStatus']}.",
#         "tax filing income bracket": lambda: f"Your tax filing income bracket is {user_data['taxFilingIncomeBracket']}.",
#         "tax bracket": lambda: f"Your tax filing income bracket is {user_data['taxFilingIncomeBracket']}.",
#         "income bracket": lambda: f"Your tax filing income bracket is {user_data['taxFilingIncomeBracket']}.",
#         "bracket": lambda: f"Your tax filing income bracket is {user_data['taxFilingIncomeBracket']}.",
#         "tax income bracket": lambda: f"Your tax filing income bracket is {user_data['taxFilingIncomeBracket']}.", 
#         "tax filing state": lambda: f"Your tax filing state is {user_data['taxFilingState']}.",
#         "estimated retirement age": lambda: f"Your estimated retirement age is {user_data['estimatedRetirementAge']}.",
#         "spending variation tolerance": lambda: f"Your spending variation tolerance is {user_data['spendingVariationTolerance']}.",
#         "short-term loss sensitivity": lambda: f"Your short-term loss sensitivity is {user_data['shortTermLossSensitivity']}.",
#         "services": lambda: "Your services are: " + ", ".join(user_data['services']) if user_data['services'] else "You are not subscribed to any services."
#     }

#     normalized_query = query.lower()
#     for key in intents.keys():
#         if key in normalized_query:
#             print(f"Exact match intent: {key}, returning result.")
#             return intents[key]() 
    
#     return "I'm sorry, I couldn't find an answer to that question."

    # documents = [Document(page_content=intent, metadata={"action": intent}) for intent in intents]
    # embeddings = OpenAIEmbeddings()
    # vector_store = FAISS.from_documents(documents, embeddings)

    # similar_docs_with_scores = vector_store.similarity_search_with_score(query, k=1)
    
    # if similar_docs_with_scores:
    #     best_doc, best_score = similar_docs_with_scores[0]
    #     best_intent = best_doc.metadata["action"]
        
    #     print(f"Similarity score for '{best_intent}': {best_score:.4f}")
        
    #     return intents[best_intent]()
    # else:
    #     print("No suitable match found.")
    #     return "I'm sorry, I couldn't find an answer to that question."


async def main():
    input_data = {"input": "what is my user id"}
    result = await chatbot_agent_executor.ainvoke(input_data)
    print(result)


def test_service():
    test_queries = [
        "whats my money, can i afford a dog?",
        "What is my account name?",
        "What is my gender?",
        "What is my age?",
        "What is my risk tolerance?",
        "What is my marital status?",
        "What is my tax filing status?",
        "What is my tax filing income bracket?",
        "What is my tax filing state?",
        "What is my estimated retirement age?",
        "What is my spending variation tolerance?",
        "What is my short-term loss sensitivity?",
        "What is my short term loss sensitivity?",
        # "I want to subscribe to Financial Planning",
        # "How can I unsubscribe from Investment Management?",
        # "List all my services",
        # "Remove my subscription to Retirement Planning"
    ]
    for query in test_queries:
        result = asyncio.run(chatbot_agent_executor.ainvoke({"input": query}))
        print(f"Query: {query}\nResponse: {result['output']}\n")


if __name__ == "__main__":
    test_service()
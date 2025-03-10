from collections import defaultdict
from langchain_core.messages import HumanMessage, AIMessage
from chatbot_langchain import chatbot_agent_executor

# Store chat history per session
chat_histories = defaultdict(list)

def process_message(user_message: str, frontend_url: str):
    session_id = frontend_url

    # Retrieve existing chat history
    raw_chat_history = chat_histories[session_id]

    # Convert chat history to LangChain format
    chat_history = []
    for entry in raw_chat_history:
        if entry["role"] == "human":
            chat_history.append(HumanMessage(content=entry["content"]))
        elif entry["role"] == "ai":
            chat_history.append(AIMessage(content=entry["content"]))

    print(f"Converted chat history for LangChain (Session {session_id}): {chat_history}")

    # Prepare input data for chatbot
    input_data = {
        "input": user_message,
        "frontendUrl": frontend_url,
        "chat_history": chat_history
    }

    print(f"Final input to chatbot_agent_executor: {input_data}")

    # Process the message using the AI chatbot
    try:
        result = chatbot_agent_executor.invoke(input_data)
        print(f"Raw result from chatbot_agent_executor: {result}")
        bot_message = result['output']
    except Exception as e:
        print(f"ERROR in chatbot execution: {e}")
        bot_message = "Sorry, something went wrong."

    # Append to raw chat history for persistence
    raw_chat_history.append({"role": "human", "content": user_message})
    raw_chat_history.append({"role": "ai", "content": bot_message})

    # Store updated history
    chat_histories[session_id] = raw_chat_history
    print(f"Updated chat history for session {session_id}: {chat_histories[session_id]}")

    return bot_message

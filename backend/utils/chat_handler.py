from collections import defaultdict
from langchain_core.messages import HumanMessage, AIMessage

class ChatHandler:
    def __init__(self, chatbot):
        # Store chat history per session
        self.chat_histories = defaultdict(list)
        self.chatbot = chatbot
    
    def process_message(self, user_message: str, frontend_url: str, user_id: str):
        session_id = frontend_url
        
        # Set the user ID in the chatbot
        self.chatbot.set_user_id(user_id)

        # Retrieve existing chat history
        raw_chat_history = self.chat_histories[session_id]

        live_agent = "Off"

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
            "userId": user_id,
            "chat_history": chat_history,
            "live_agent_status": live_agent,
        }

        print(f"Final input to chatbot_agent_executor: {input_data}")

        # Process the message using the AI chatbot
        try:
            result = self.chatbot.invoke(input_data)
            print(f"Raw result from chatbot_agent_executor: {result}")
            bot_message = result['output']
        except Exception as e:
            print(f"ERROR in chatbot execution: {e}")
            bot_message = "Sorry, something went wrong."

        # Append to raw chat history for persistence
        raw_chat_history.append({"role": "human", "content": user_message})
        raw_chat_history.append({"role": "ai", "content": bot_message})

        # Store updated history
        self.chat_histories[session_id] = raw_chat_history
        print(f"Updated chat history for session {session_id}: {self.chat_histories[session_id]}")

        return bot_message
    
    def get_chat_history(self, session_id):
        """Get the chat history for a specific session"""
        return self.chat_histories.get(session_id, [])
    
    def clear_chat_history(self, session_id):
        """Clear the chat history for a specific session"""
        if session_id in self.chat_histories:
            self.chat_histories[session_id] = []
            return True
        return False
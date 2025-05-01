from collections import defaultdict
from langchain_core.messages import HumanMessage, AIMessage
from agents.live_agent import LiveAgentChat
from utils.message_analyzer import MessageAnalyzer

class ChatHandler:
    def __init__(self, chatbot):
        # Store chat history per session
        self.chat_histories = defaultdict(list)
        self.chatbot = chatbot
        self.live_agent_status = False
        self.live_agent = LiveAgentChat()
        self.message_analyzer = MessageAnalyzer()  # Initialize the MessageAnalyzer
        self.waiting_for_live_agent_response = defaultdict(bool)  # Track if we're waiting for a response about live agent
    
    def process_message(self, user_message: str, frontend_url: str, user_id: str):
        session_id = frontend_url
        
        # Set the user ID in the chatbot
        if user_id != self.chatbot.get_current_user_id():
            self.chat_histories[session_id] = []  # Clear history for new user
            self.chatbot.set_user_id(user_id)
            self.waiting_for_live_agent_response[session_id] = False

        # Retrieve existing chat history
        raw_chat_history = self.chat_histories[session_id]

        # Check if we're waiting for a response about live agent
        if self.waiting_for_live_agent_response[session_id]:
            # Check if user accepted the live agent
            if self.message_analyzer.check_for_live_agent_acceptance(user_message):
                self.live_agent_status = True
                bot_message = '''You're now connected with a live agent.
                    **Live Agent - Sarah**
                    How can I help you today?'''
            else:
                bot_message = "I'll continue to assist you. What can I help you with?"
            
            # No longer waiting for response
            self.waiting_for_live_agent_response[session_id] = False
            
            # Append to raw chat history
            raw_chat_history.append({"role": "human", "content": user_message})
            raw_chat_history.append({"role": "ai", "content": bot_message})
            
            # Store updated history
            self.chat_histories[session_id] = raw_chat_history
            
            return bot_message

        # Check if user wants to end live agent session
        if self.live_agent_status and self.message_analyzer.check_for_live_agent_termination(user_message):
            self.live_agent_status = False
            bot_message = "Live agent session has ended. You're now connected with the AI assistant again. How can I help you?"
            
            # Append to raw chat history
            raw_chat_history.append({"role": "human", "content": user_message})
            raw_chat_history.append({"role": "ai", "content": bot_message})
            
            # Store updated history
            self.chat_histories[session_id] = raw_chat_history
            
            return bot_message

        # Convert chat history to LangChain format
        chat_history = []
        for entry in raw_chat_history:
            if entry["role"] == "human":
                chat_history.append(HumanMessage(content=entry["content"]))
            elif entry["role"] == "ai":
                chat_history.append(AIMessage(content=entry["content"]))

        print(f"Converted chat history for LangChain (Session {session_id}): {chat_history}")

        # Analyze sentiment and check if live agent should be offered
        if not self.live_agent_status and self.message_analyzer.should_offer_live_agent(user_message):
            bot_message = self.message_analyzer.format_live_agent_proposal()
            self.waiting_for_live_agent_response[session_id] = True
            
            # Append to raw chat history
            raw_chat_history.append({"role": "human", "content": user_message})
            raw_chat_history.append({"role": "ai", "content": bot_message})
            
            # Store updated history
            self.chat_histories[session_id] = raw_chat_history
            
            return bot_message

        # Prepare input data for chatbot
        input_data = {
            "input": user_message,
            "frontendUrl": frontend_url,
            "userId": user_id,
            "chat_history": chat_history,
        }

        print(f"Final input to chatbot_agent_executor: {input_data}")

        # Process the message using the AI chatbot
        try:
            if self.live_agent_status:
                # Use the live agent if the status is set
                result = self.live_agent.invoke(input_data)
                print(f"Raw result from live agent: {result}")
            else:
                # Use the default chatbot agent executor
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
            self.waiting_for_live_agent_response[session_id] = False
            return True
        return False
    
    def reset_live_agent_status(self):
        """Reset the live agent status back to AI chatbot"""
        self.live_agent_status = False
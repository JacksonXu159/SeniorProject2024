from collections import defaultdict
from langchain_core.messages import HumanMessage, AIMessage
import asyncio

class ChatHandler:
    def __init__(self, chatbot):
        self.chat_histories = defaultdict(list)
        self.chatbot = chatbot
        
        # Import here to avoid circular imports
        from utils.live_agent_manager import LiveAgentManager
        from utils.response_handler import ResponseHandler
        
        self.live_agent_manager = LiveAgentManager()
        self.response_handler = ResponseHandler(chatbot)
    
    def add_to_history(self, session_id, role, content):
        """Add a message to the chat history"""
        self.chat_histories[session_id].append({"role": role, "content": content})
    
    def get_chat_history(self, session_id):
        """Get the chat history for a specific session"""
        return self.chat_histories.get(session_id, [])
    
    def clear_chat_history(self, session_id):
        """Clear the chat history for a specific session"""
        if session_id in self.chat_histories:
            self.chat_histories[session_id] = []
            self.live_agent_manager.set_waiting_status(session_id, False)
            return True
        return False
    
    def convert_to_langchain_format(self, raw_history):
        """Convert raw chat history to LangChain format"""
        result = []
        for entry in raw_history:
            if entry["role"] == "human":
                result.append(HumanMessage(content=entry["content"]))
            elif entry["role"] == "ai":
                result.append(AIMessage(content=entry["content"]))
        return result
    
    async def process_websocket_message(self, websocket, message, user_id, session_id):
        """Process a message received via WebSocket"""
        # Add user message to history
        self.add_to_history(session_id, "human", message)
        
        # Get chat history
        chat_history = self.get_chat_history(session_id)
        langchain_history = self.convert_to_langchain_format(chat_history)
        
        # Process based on conversation state
        if self.live_agent_manager.is_live_agent_active():
            # CASE 1: Live agent mode is active
            if self.live_agent_manager.check_for_termination(message):
                bot_response = "Live agent session has ended. You're now connected with the AI assistant again. How can I help you?"
                self.live_agent_manager.set_live_agent_status(False)
            else:
                result = self.live_agent_manager.handle_message({
                    "input": message,
                    "frontendUrl": session_id,
                    "userId": user_id,
                    "chat_history": langchain_history,
                })
                bot_response = result['output']
            
            # Add response to chat history
            self.add_to_history(session_id, "ai", bot_response)
            
            # Stream the response
            await self.response_handler.stream_response(websocket, bot_response)
            
        elif self.live_agent_manager.is_waiting_for_response(session_id):
            # CASE 2: Waiting for response to live agent offer
            if self.live_agent_manager.check_for_acceptance(message):
                self.live_agent_manager.set_waiting_status(session_id, False)
                self.live_agent_manager.set_live_agent_status(True)
                bot_response = "You're now connected with a live agent who will assist you. Feel free to explain your issue in detail."
            else:
                self.live_agent_manager.set_waiting_status(session_id, False)
                bot_response = "I'll continue to assist you as an AI assistant. What else can I help you with?"
            
            # Add response to chat history
            self.add_to_history(session_id, "ai", bot_response)
            
            # Stream the response
            await self.response_handler.stream_response(websocket, bot_response)
            
        elif self.live_agent_manager.should_offer_live_agent(message):
            # CASE 3: Should offer live agent based on message
            bot_response = self.live_agent_manager.format_proposal()
            self.live_agent_manager.set_waiting_status(session_id, True)
            
            # Add response to chat history
            self.add_to_history(session_id, "ai", bot_response)
            
            # Stream the response
            await self.response_handler.stream_thinking(websocket)
            await self.response_handler.stream_response(websocket, bot_response)
            
        else:
            # CASE 4: Standard AI chatbot processing
            await self.response_handler.stream_thinking(websocket)
            
            result = await self.response_handler.get_ai_response(
                message, user_id, session_id, langchain_history, websocket
            )
            
            if result.get('intermediate_steps'):
                last_step = result['intermediate_steps'][-1]
                tool_name = last_step[0].tool
                await self.response_handler.stream_tool_usage(websocket, tool_name)
            
            bot_response = result['output']
            
            # Add response to chat history
            self.add_to_history(session_id, "ai", bot_response)
            
            # Stream the response
            for word in bot_response.split():
                await websocket.send_text(word + " ")
                await asyncio.sleep(0.05) 
            
            await websocket.send_text("[END]")
    
    def process_http_message(self, message, frontend_url, user_id):
        """Process a message received via HTTP"""
        session_id = frontend_url
        
        # Set the user ID in the chatbot
        if user_id != self.chatbot.get_current_user_id():
            self.clear_chat_history(session_id)
            self.chatbot.set_user_id(user_id)
        
        # Add user message to history
        self.add_to_history(session_id, "human", message)
        
        # Get chat history
        chat_history = self.get_chat_history(session_id)
        langchain_history = self.convert_to_langchain_format(chat_history)
        
        # Process based on conversation state - similar logic to process_websocket_message
        # but without streaming and using synchronous calls
        
        if self.live_agent_manager.is_live_agent_active():
            # Handle live agent case
            if self.live_agent_manager.check_for_termination(message):
                bot_response = "Live agent session has ended. You're now connected with the AI assistant again. How can I help you?"
                self.live_agent_manager.set_live_agent_status(False)
            else:
                result = self.live_agent_manager.handle_message({
                    "input": message,
                    "frontendUrl": session_id,
                    "userId": user_id,
                    "chat_history": langchain_history,
                })
                bot_response = result['output']
                
        elif self.live_agent_manager.is_waiting_for_response(session_id):
            # Handle live agent acceptance/rejection
            if self.live_agent_manager.check_for_acceptance(message):
                self.live_agent_manager.set_waiting_status(session_id, False)
                self.live_agent_manager.set_live_agent_status(True)
                bot_response = "You're now connected with a live agent who will assist you. Feel free to explain your issue in detail."
            else:
                self.live_agent_manager.set_waiting_status(session_id, False)
                bot_response = "I'll continue to assist you as an AI assistant. What else can I help you with?"
                
        elif self.live_agent_manager.should_offer_live_agent(message):
            # Offer live agent
            bot_response = self.live_agent_manager.format_proposal()
            self.live_agent_manager.set_waiting_status(session_id, True)
            
        else:
            # Standard AI chatbot processing
            try:
                result = self.response_handler.get_ai_response(
                    message, user_id, session_id, langchain_history
                )
                bot_response = result['output']
            except Exception as e:
                print(f"ERROR in chatbot execution: {e}")
                bot_response = "Sorry, something went wrong."
        
        # Add response to chat history
        self.add_to_history(session_id, "ai", bot_response)
        
        return bot_response

import asyncio
from langchain.agents import AgentExecutor

class ResponseHandler:
    def __init__(self, chatbot):
        self.chatbot = chatbot
        
    async def stream_response(self, websocket, response_text):
        await websocket.send_text(response_text)
        await websocket.send_text("[END]")

    async def stream_typing(self, websocket):
        await websocket.send_text("⌨️ Typing ...")
        await asyncio.sleep(0.5)
        
    async def stream_thinking(self, websocket):
        await websocket.send_text("🤔 Thinking...")
        await asyncio.sleep(0.5)
        
    async def stream_tool_usage(self, websocket, tool_name):
        await websocket.send_text(f"🔍 Using {tool_name}...")
        await asyncio.sleep(0.5)
        
    async def get_ai_response(self, message, user_id, session_id, chat_history, websocket=None):
        # Create a handler if websocket is provided
        handler = None
        if websocket:
            from chatbot_langchain import WebSocketStreamHandler
            handler = WebSocketStreamHandler(websocket)
            callbacks = [handler]
        else:
            callbacks = []
        
        # Initialize the agent executor
        agent_with_streaming = AgentExecutor(
            agent=self.chatbot.chatbot_agent,
            tools=self.chatbot.tools,
            return_intermediate_steps=True, 
            verbose=True,
            callbacks=callbacks,
        )
        
        # Prepare input data for the agent
        input_data = {
            "input": message,
            "userId": user_id,
            "frontendUrl": session_id,
            "chat_history": chat_history,
            "live_agent_status": "Off",
        }
        
        # Use agent with streaming
        if websocket:
            return await agent_with_streaming.ainvoke(input_data)
        else:
            return agent_with_streaming.invoke(input_data)
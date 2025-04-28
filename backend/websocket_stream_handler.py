from langchain.callbacks.base import AsyncCallbackHandler

class WebSocketStreamHandler(AsyncCallbackHandler):
    def __init__(self, websocket):
        self.websocket = websocket
        self.current_tool = None

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.websocket.send_text(token)
        
    async def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when a tool is about to be used"""
        self.current_tool = serialized.get("name", "unknown tool")
        await self.websocket.send_text(f"\n🔧 Using tool: {self.current_tool}\n")
        
    async def on_tool_end(self, output, **kwargs):
        """Called when a tool has finished"""
        if self.current_tool:
            await self.websocket.send_text(f"\n✅ Tool {self.current_tool} completed\n")
            self.current_tool = None
            
    async def on_agent_action(self, action, **kwargs):
        """Called when the agent is taking an action"""
        if action.get("tool"):
            await self.websocket.send_text(f"\n🤔 Thinking about using: {action.get('tool')}\n")
            
    async def on_agent_finish(self, finish, **kwargs):
        """Called when the agent has finished"""
        await self.websocket.send_text("\n✨ Response complete\n")
        
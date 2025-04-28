from langchain.callbacks.base import AsyncCallbackHandler

class WebSocketStreamHandler(AsyncCallbackHandler):
    def __init__(self, websocket):
        self.websocket = websocket
        self.current_tool = None
        self.last_output = None  # Track the last output to prevent duplicates
        self.tool_output_sent = False  # Track if we've sent a tool output
        self.current_output = ""  # Track the current output being built
        self.is_thinking = False  # Track if we're in a thinking state
        self.thinking_complete = False  # Track if thinking is complete

    async def on_llm_new_token(self, token: str, **kwargs):
        self.current_output += token
        await self.websocket.send_text(token)
        
    async def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when a tool is about to be used"""
        self.current_tool = serialized.get("name", "unknown tool")
        self.tool_output_sent = False  # Reset the flag when a new tool starts
        await self.websocket.send_text(f"\n[THINKING]🤔 Thinking about using: {self.current_tool}[/THINKING]\n")
        
    async def on_tool_end(self, output, **kwargs):
        """Called when a tool has finished"""
        if self.current_tool:
            # Always send the tool output if it exists and we haven't sent it yet
            if output and not self.tool_output_sent:
                # Send a marker to indicate the end of thinking and start of answer
                if not self.thinking_complete:
                    await self.websocket.send_text("[END_THINKING]")
                    self.thinking_complete = True
                
                # Stream the tool's output to the client
                await self.websocket.send_text(f"\n{output}\n")
                self.tool_output_sent = True
                self.last_output = output
                self.current_output = output  # Update the current output
            await self.websocket.send_text(f"\n✅ Tool {self.current_tool} completed\n")
            self.current_tool = None
            
    async def on_agent_action(self, action, **kwargs):
        """Called when the agent is taking an action"""
        if action.get("tool"):
            # Use a special marker for thinking text
            await self.websocket.send_text(f"\n[THINKING]🤔 Thinking about using: {action.get('tool')}[/THINKING]\n")
            
    async def on_agent_finish(self, finish, **kwargs):
        """Called when the agent has finished"""
        # Send a marker to indicate the end of thinking and start of answer if not already sent
        if not self.thinking_complete:
            await self.websocket.send_text("[END_THINKING]")
            self.thinking_complete = True
            
        # Always send the completion message
        # await self.websocket.send_text("\n✨ Response complete\n")
        
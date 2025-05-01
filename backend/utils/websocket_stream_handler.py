from langchain.callbacks.base import AsyncCallbackHandler

class WebSocketStreamHandler(AsyncCallbackHandler):
    def __init__(self, websocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs):
        await self.websocket.send_text(token)

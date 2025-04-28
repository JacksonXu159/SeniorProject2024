from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
from chatbot_langchain import chatbot_agent_executor
from fastapi.middleware.cors import CORSMiddleware


from websocket_stream_handler import WebSocketStreamHandler
from langchain.agents import AgentExecutor
from chatbot_langchain import chatbot_agent, tools, chatbot_agent_prompt
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_openai_functions_agent

async def stream_agent_response(websocket, message):
    handler = WebSocketStreamHandler(websocket)
    
    streaming_model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        streaming=True,
        callbacks=[handler]
    )
    
    streaming_agent = create_openai_functions_agent(
        llm=streaming_model,
        prompt=chatbot_agent_prompt,
        tools=tools,
    )
    
    agent_with_streaming = AgentExecutor(
        agent=streaming_agent,
        tools=tools,
        return_intermediate_steps=False, 
        verbose=True,
        callbacks=[handler],
    )

    await websocket.send_text("🤔 Thinking...\n")
    
    result = await agent_with_streaming.ainvoke({"input": message})
    
    await websocket.send_text("[END]")

load_dotenv()

class Message(BaseModel):
    message: str
    frontendUrl: str
    
class MessageResponse(BaseModel):
    message: str
    sender: str = "Bot"
    direction: str = "incoming"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@app.post("/")
async def root():
    return {"message": "Welcome to Vanguard APP!"}

@app.post("/message/")
async def create_message(message: Message):
    input_data = {"input": message.message, "frontendUrl": message.frontendUrl}  
    
    result = await chatbot_agent_executor.ainvoke(input_data)
    bot_message = result['output']
    
    return MessageResponse(
        message=bot_message,
        sender="Bot",
        direction="incoming"
    )

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            message = await websocket.receive_text()
            print(f"Client says: {message}")
            
            await stream_agent_response(websocket, message)
    except Exception as e:
        print("Disconnected:", e)

from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from page_suggestions import get_page_suggestions
import asyncio
from utils.queries import get_user_info, get_all_users, get_user_services
from chatbot_langchain import ChatbotLangchain, WebSocketStreamHandler
from utils.chat_handler import ChatHandler
from langchain.agents import AgentExecutor
from typing import Optional

load_dotenv()

chatbot = ChatbotLangchain()
chat_handler = ChatHandler(chatbot)

async def stream_agent_response(websocket, message):
    handler = WebSocketStreamHandler(websocket)
    
    agent_with_streaming = AgentExecutor(
        agent=chatbot.chatbot_agent,
        tools=chatbot.tools,
        return_intermediate_steps=True, 
        verbose=True,
        callbacks=[handler],
    )

    input_data = {
        "input": message,
        "chat_history": [], 
        "live_agent_status": "Off", 
    }

    try:
        await websocket.send_text("🤔 Thinking...")
        await asyncio.sleep(0.5) 

        result = await agent_with_streaming.ainvoke(input_data)
        
        if result.get('intermediate_steps'):
            last_step = result['intermediate_steps'][-1]
            tool_name = last_step[0].tool
            await websocket.send_text(f"🔍 Using {tool_name}...")
            await asyncio.sleep(0.5) 
        
        words = result['output'].split()
        for word in words:
            await websocket.send_text(word + " ")
            await asyncio.sleep(0.05) 
        
        await websocket.send_text("[END]")
    except Exception as e:
        print(f"Error in stream_agent_response: {e}")
        await websocket.send_text("Sorry, I encountered an error. Please try again.")
        await websocket.send_text("[END]")

class UserRequest(BaseModel):
    user_id: str

class Message(BaseModel):
    message: str
    frontendUrl: str
    userId: str
    
class MessageResponse(BaseModel):
    message: str
    sender: str = "Bot"
    direction: str = "incoming"

class ServicesResponse(BaseModel):
    services: list[str]

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
    bot_response = chat_handler.process_message(
        message.message, 
        message.frontendUrl,
        message.userId
    )

    return MessageResponse(
        message=bot_response,
        sender="Bot",
        direction="incoming"
    )

@app.post("/get_user/")
async def fetch_user_data(request: UserRequest):
    user_data = get_user_info(request.user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    return user_data

@app.get("/users/")
async def fetch_all_users():
    users = get_all_users()
    if not users:
        return {"users": []}
    return {"users": users}

@app.get("/user/{user_id}/services/")
async def fetch_user_services(user_id: str):
    services = get_user_services(user_id)
    if services is None:
        raise HTTPException(status_code=500, detail="Error fetching user services")
    return ServicesResponse(services=services)

@app.post("/get_suggestions/{url:path}") 
async def fetch_suggestions(url: Optional[str] = ""):
    print("suggestion url: ", url)
    suggestions = get_page_suggestions(url)
    if not suggestions:
        raise HTTPException(status_code=404, detail="No suggestions found")
    return suggestions


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
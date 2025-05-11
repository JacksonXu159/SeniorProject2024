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
import json

load_dotenv()

chatbot = ChatbotLangchain()
chat_handler = ChatHandler(chatbot)

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
    bot_response = chat_handler.process_http_message(
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
            message_data = await websocket.receive_text()
            print(f"Client sent data: {message_data}")
            
            try:
                data = json.loads(message_data)
                message = data.get("message", "")
                user_id = data.get("userId", "")
            except json.JSONDecodeError:
                message = message_data
                user_id = chatbot.get_current_user_id()
            
            # Set user ID in chatbot
            if user_id:
                chatbot.set_user_id(user_id)
            
            # Get the session identifier
            session_id = str(id(websocket))
            
            # Process the message using the unified handler
            await chat_handler.process_websocket_message(
                websocket, message, user_id, session_id
            )
            
    except Exception as e:
        print("Disconnected:", e)
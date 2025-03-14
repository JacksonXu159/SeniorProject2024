from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from chat_handler import process_message
import asyncio
from chatbot_langchain import chatbot_agent_executor, set_user_id 
from queries import get_user_info, get_all_users, get_user_services # Added imports

load_dotenv()

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
    set_user_id(message.userId)
    bot_response = process_message(message.message, message.frontendUrl)

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
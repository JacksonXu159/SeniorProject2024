from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from chat_handler import process_message

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
    bot_response = process_message(message.message, message.frontendUrl)

    return MessageResponse(
        message=bot_response,
        sender="Bot",
        direction="incoming"
    )

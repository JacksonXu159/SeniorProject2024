from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
from chatbot_langchain import chatbot_agent_executor
from sqlalchemy.orm import Session
from fastapi import Depends
from database import Base, engine, get_db
import os

database_url = os.getenv("DATABASE_URL")
Base.metadata.create_all(bind=engine)


load_dotenv()

class Message(BaseModel):
    message: str
    
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
# @app.post("/")
async def root(db: Session = Depends(get_db)):
    result = db.execute("SELECT NOW()").fetchone()
    return {"message": "Welcome to Vanguard APP!", "current_time": result[0]}


@app.post("/message/")
async def create_message(message: Message):
    input_data = {"input": message.message}
    
    result = await chatbot_agent_executor.ainvoke(input_data)
    bot_message = result['output']
    
    return MessageResponse(
        message=bot_message,
        sender="Bot",
        direction="incoming"
    )

from fastapi import FastAPI
from pydantic import BaseModel


class Message(BaseModel):
    message: str


app = FastAPI()


@app.post("/message/")
async def create_message(message: Message):
    return message
from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import asyncio
from utils.queries import get_user_info, get_all_users, get_user_services
from chatbot_langchain import ChatbotLangchain
from utils.chat_handler import ChatHandler
from fastapi.middleware.cors import CORSMiddleware


from websocket_stream_handler import WebSocketStreamHandler
from langchain.agents import AgentExecutor
from langchain.chat_models import ChatOpenAI
from langchain.agents import create_openai_functions_agent

async def stream_agent_response(websocket, message):
    handler = WebSocketStreamHandler(websocket)
    
    # Create a ChatbotLangchain instance
    chatbot = ChatbotLangchain()
    
    # Get the tools and prompt from the chatbot instance
    tools = chatbot.tools
    chatbot_agent_prompt = chatbot.chatbot_agent_prompt
    
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

    # Use a special marker for the initial thinking message
    await websocket.send_text("[THINKING]🤔 Thinking...[/THINKING]\n")
    
    # Provide the missing variables required by the prompt template
    input_data = {
        "input": message,
        "live_agent_status": "offline",  # Default value
        "chat_history": []  # Empty chat history for now
    }
    
    try:
        # The handler will send the response token by token
        result = await agent_with_streaming.ainvoke(input_data)
        
        # If the result contains an output and it's different from what we've already sent
        if result and "output" in result and result["output"] != handler.current_output:
            # Send a marker to indicate the end of thinking and start of answer if not already sent
            if not handler.thinking_complete:
                await websocket.send_text("[END_THINKING]")
                handler.thinking_complete = True
                
            await websocket.send_text(f"\n{result['output']}\n")
    except Exception as e:
        print(f"Error in stream_agent_response: {e}")
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        # Always send the [END] marker to signal the end of the response
        await websocket.send_text("[END]")

load_dotenv()

# Initialize the chatbot and chat handler
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
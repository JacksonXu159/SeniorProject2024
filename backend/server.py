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

load_dotenv()

chatbot = ChatbotLangchain()
chat_handler = ChatHandler(chatbot)

async def stream_agent_response(websocket, message_data):
    handler = WebSocketStreamHandler(websocket)
    
    # Parse message_data as JSON to extract message and userId
    import json
    try:
        data = json.loads(message_data)
        message = data.get("message", "")
        user_id = data.get("userId", "")
        print(f"Processing message: {message} from user: {user_id}")
    except json.JSONDecodeError:
        # Fallback if not JSON
        message = message_data
        user_id = chatbot.get_current_user_id()
        print(f"Warning: Non-JSON message: {message}")
    
    # Set user ID in chatbot
    if user_id:
        chatbot.set_user_id(user_id)
    
    # Get the session identifier (using websocket id as a simple solution)
    session_id = str(id(websocket))
    
    # Get chat history for this session
    chat_history = chat_handler.get_chat_history(session_id)
    
    # Convert raw history to LangChain format
    from langchain_core.messages import HumanMessage, AIMessage
    langchain_history = []
    for entry in chat_history:
        if entry["role"] == "human":
            langchain_history.append(HumanMessage(content=entry["content"]))
        elif entry["role"] == "ai":
            langchain_history.append(AIMessage(content=entry["content"]))
    
    agent_with_streaming = AgentExecutor(
        agent=chatbot.chatbot_agent,
        tools=chatbot.tools,
        return_intermediate_steps=True, 
        verbose=True,
        callbacks=[handler],
    )

    input_data = {
        "input": message,
        "userId": user_id,
        "frontendUrl": session_id,  # Using session_id as frontendUrl
        "chat_history": langchain_history,
        "live_agent_status": "On" if chat_handler.live_agent_status else "Off", 
    }

    try:
        # Check if message should be handled by chat_handler directly
        # (for live agent interactions, etc.)
        if chat_handler.waiting_for_live_agent_response.get(session_id, False) or \
           (chat_handler.live_agent_status and chat_handler.message_analyzer.check_for_live_agent_termination(message)):
            
            # Process with chat_handler
            bot_response = chat_handler.process_message(message, session_id, user_id)
            
            # Stream the response word by word
            await websocket.send_text("Typing ...")
            await asyncio.sleep(0.5)
            
            words = bot_response.split()
            for word in words:
                await websocket.send_text(word + " ")
                await asyncio.sleep(0.05)
            
            await websocket.send_text("[END]")
            return
        
        # Check if we should offer live agent based on message
        if not chat_handler.live_agent_status and chat_handler.message_analyzer.should_offer_live_agent(message):
            bot_response = chat_handler.message_analyzer.format_live_agent_proposal()
            chat_handler.waiting_for_live_agent_response[session_id] = True
            
            # Update chat history
            chat_handler.chat_histories[session_id].append({"role": "human", "content": message})
            chat_handler.chat_histories[session_id].append({"role": "ai", "content": bot_response})
            
            # Stream the response word by word
            await websocket.send_text("🤔 Thinking...")
            await asyncio.sleep(0.5)
            
            words = bot_response.split()
            for word in words:
                await websocket.send_text(word + " ")
                await asyncio.sleep(0.05)
            
            await websocket.send_text("[END]")
            return
        
        # Standard agent processing
        await websocket.send_text("🤔 Thinking...")
        await asyncio.sleep(0.5) 

        # Use agent with streaming
        result = await agent_with_streaming.ainvoke(input_data)
        
        if result.get('intermediate_steps'):
            last_step = result['intermediate_steps'][-1]
            tool_name = last_step[0].tool
            await websocket.send_text(f"🔍 Using {tool_name}...")
            await asyncio.sleep(0.5) 
        
        # Get the final output
        bot_response = result['output']
        
        # Update chat history
        chat_handler.chat_histories[session_id].append({"role": "human", "content": message})
        chat_handler.chat_histories[session_id].append({"role": "ai", "content": bot_response})
        
        # Stream the response word by word
        words = bot_response.split()
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

@app.post("/get_suggestions/{url}")
async def fetch_suggestions(url: str):
    print("suggestion url: ", url)
    suggestions = get_page_suggestions(url)
    return suggestions


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            message_data = await websocket.receive_text()
            print(f"Client sent data: {message_data}")
            
            await stream_agent_response(websocket, message_data)
    except Exception as e:
        print("Disconnected:", e)
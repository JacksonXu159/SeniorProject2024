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

async def stream_agent_response(websocket, message_data):
    handler = WebSocketStreamHandler(websocket)
    
    # Parse message_data as JSON to extract message and userId
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
    print(f"Current chat history: {chat_history}")
    
    # Add the current user message to history immediately
    chat_handler.chat_histories[session_id].append({"role": "human", "content": message})
    
    # Convert raw history to LangChain format
    from langchain_core.messages import HumanMessage, AIMessage
    langchain_history = []
    for entry in chat_history:
        if entry["role"] == "human":
            langchain_history.append(HumanMessage(content=entry["content"]))
        elif entry["role"] == "ai":
            langchain_history.append(AIMessage(content=entry["content"]))
    
    try:
        # CASE 1: Live agent mode is active
        if chat_handler.live_agent_status:
            print("Live agent mode is active, bypassing AI chatbot")
            
            # Check for live agent termination command
            if chat_handler.message_analyzer.check_for_live_agent_termination(message):
                bot_response = "Live agent session has ended. You're now connected with the AI assistant again. How can I help you?"
                chat_handler.set_live_agent_status(False)
            else:
                # Live agent handles the message
                result = chat_handler.live_agent.invoke({
                    "input": message,
                    "frontendUrl": session_id,
                    "userId": user_id,
                    "chat_history": langchain_history,
                })

                bot_response = result['output']
            
            # Add response to chat history
            chat_handler.chat_histories[session_id].append({"role": "ai", "content": bot_response})
            
            # Stream the response
            await websocket.send_text("Typing ...")
            await asyncio.sleep(0.5)
            for word in bot_response.split():
                await websocket.send_text(word + " ")
                await asyncio.sleep(0.05)
            await websocket.send_text("[END]")
            return
            
        # CASE 2: Check for pending live agent acceptance
        elif session_id in chat_handler.waiting_for_live_agent_response and chat_handler.waiting_for_live_agent_response[session_id]:
            print("Processing response to live agent offer")
            
            # Check if user accepted live agent help
            if chat_handler.message_analyzer.check_for_live_agent_acceptance(message):
                # User accepted live agent
                chat_handler.waiting_for_live_agent_response[session_id] = False
                chat_handler.set_live_agent_status(True)
                
                bot_response = "You're now connected with a live agent who will assist you. Feel free to explain your issue in detail."
            else:
                # User declined live agent
                chat_handler.waiting_for_live_agent_response[session_id] = False
                
                bot_response = "I'll continue to assist you as an AI assistant. What else can I help you with?"
            
            # Add response to chat history
            chat_handler.chat_histories[session_id].append({"role": "ai", "content": bot_response})
            
            # Stream the response
            await websocket.send_text("Typing ...")
            await asyncio.sleep(0.5)
            for word in bot_response.split():
                await websocket.send_text(word + " ")
                await asyncio.sleep(0.05)
            await websocket.send_text("[END]")
            return
            
        # CASE 3: Check if should offer live agent based on message
        elif chat_handler.message_analyzer.should_offer_live_agent(message):
            print("Offering live agent based on message analysis")
            
            bot_response = chat_handler.message_analyzer.format_live_agent_proposal()
            chat_handler.waiting_for_live_agent_response[session_id] = True
            
            # Add response to chat history
            chat_handler.chat_histories[session_id].append({"role": "ai", "content": bot_response})
            
            # Stream the response
            await websocket.send_text("🤔 Thinking...")
            await asyncio.sleep(0.5)
            
            words = bot_response.split()
            for word in words:
                await websocket.send_text(word + " ")
                await asyncio.sleep(0.05)
            
            await websocket.send_text("[END]")
            return
            
        # CASE 4: Standard AI chatbot processing
        else:
            print("Using standard AI chatbot processing")
            
            await websocket.send_text("🤔 Thinking...")
            await asyncio.sleep(0.5) 

            # Initialize the agent executor
            agent_with_streaming = AgentExecutor(
                agent=chatbot.chatbot_agent,
                tools=chatbot.tools,
                return_intermediate_steps=True, 
                verbose=True,
                callbacks=[handler],
            )

            # Prepare input data for the agent
            input_data = {
                "input": message,
                "userId": user_id,
                "frontendUrl": session_id,
                "chat_history": langchain_history,
                "live_agent_status": "Off",  # Explicitly set to Off in AI mode
            }
            
            # Use agent with streaming
            result = await agent_with_streaming.ainvoke(input_data)
            
            if result.get('intermediate_steps'):
                last_step = result['intermediate_steps'][-1]
                tool_name = last_step[0].tool
                await websocket.send_text(f"🔍 Using {tool_name}...")
                await asyncio.sleep(0.5) 
            
            # Get the final output
            bot_response = result['output']
            
            # Add response to chat history
            chat_handler.chat_histories[session_id].append({"role": "ai", "content": bot_response})
            
            # Stream the response
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
            
            await stream_agent_response(websocket, message_data)
    except Exception as e:
        print("Disconnected:", e)
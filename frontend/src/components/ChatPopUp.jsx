import { useState } from "react"; 
import { Box, Button } from "@mui/material";
import ChatIcon from "@mui/icons-material/Chat";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  MessageInput,
  TypingIndicator,
} from "@chatscope/chat-ui-kit-react";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import ReactMarkdown from "react-markdown";

import "./ChatPopup.css";
import useGenAI from "../hooks/useGenAI";
import { useUserStore } from "../hooks/useUserStore";
import getSuggestionList from "../hooks/getSuggestionList";

const style = {
  background: "#c8042c",
  position: "fixed",
  bottom: 10,
  right: 10,
  borderRadius: "1000%",
  width: "48px",
  height: "48px",
  minWidth: "48px",
  fontSize: "12px",
  fontWeight: "bold",
};

const boxStyle = {
  position: "fixed",
  bottom: 65,
  right: 10,
  height: "400px",
  width: "300px",
  zIndex: 1000,
  backgroundColor: "white",
  display: "block",
  flexDirection: "column",
};

const defaultSuggestions = ["Hello!", "What's the weather?", "Tell me a joke"];

const MarkdownMessage = ({ content }) => (
  <div className="markdown-message">
    <ReactMarkdown rehypePlugins={[]}>{content}</ReactMarkdown>
  </div>
);

export default function ChatPopUp() {
  const { userId } = useUserStore();
  const [messages, setMessages] = useState([
    { message: "Hi", sender: "Bot", direction: "incoming" },
  ]);
  const [typing, setTyping] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [currentSuggestionIndex, setCurrentSuggestionIndex] = useState(0);
  const { sendMessage } = useGenAI();
  const { getSuggestions } = getSuggestionList();

  const handleSuggestions = async (url) => {
    console.log("getting suggestions");
    const response = await getSuggestions();
    if(response) {
      console.log("response: ", response);
      if (Array.isArray(response)) {
        console.log("setting suggestions");
        setSuggestions(response);
      }
    }
  }

  const toggleChat = () => {
    console.log("Chat Open:", isChatOpen);
    setIsChatOpen((open) => !open);
    setCurrentSuggestionIndex(0);
    handleSuggestions();
  };

  const handleSend = async (message) => {
    setTyping(true);

    // send to backend
    const response = await sendMessage(message, userId);
    const userMsg = { message, sender: "user", direction: "outgoing" };

    if (response) {
      const botMsg = {
        message: response.message,
        sender: "Bot",
        direction: "incoming",
        suggestions: Array.isArray(response.suggestions)
                ? response.suggestions
        : [],
      };
      
      setMessages((prev) => [...prev, userMsg, botMsg]);

      // pull out suggestions array if your API returns one
      if (Array.isArray(response.suggestions)) {
        setSuggestions(response.suggestions);
      }
    } else {
      setMessages((prev) => [...prev, userMsg]);
    }

    setTyping(false);
  };

  const nextSuggestion = () => {
    setCurrentSuggestionIndex((prevIndex) => (prevIndex + 1) % suggestions.length);
  };

  const prevSuggestion = () => {
    setCurrentSuggestionIndex((prevIndex) => (prevIndex - 1 + suggestions.length) % suggestions.length);
  };
  
  console.log("📋 suggestions state:", suggestions);

  return (
    <>
      {isChatOpen && (
        <Box sx={boxStyle} display="flex">
          <div className="chat-header">
            Chat Assistant
            <button className="chat-close-btn" onClick={toggleChat}>
              ✖
            </button>
          </div>
          <div className="suggestions-container">
            <button className="nav-button" onClick={prevSuggestion}>{"<"}</button>
            <button className="suggestion-button" onClick={() => handleSend(suggestions[currentSuggestionIndex])}>
              {suggestions[currentSuggestionIndex]}
            </button>
            <button className="nav-button" onClick={nextSuggestion}>{">"}</button>
          </div>

          <MainContainer style={{ maxHeight: "345px", bottom: "5px", flex: 1 }}>
            <ChatContainer style={{  padding: "10px", display: "flex", flexDirection: "column", flex: 1 }}>
              <MessageList
                typingIndicator={
                  typing ? <TypingIndicator content="Bot is typing" /> : null
                }
                style={{ flex: 1 }}
              >
                {messages.map((msg, i) => (
                  <Message
                    key={i}
                    model={{
                      sender: msg.sender,
                      direction: msg.direction,
                      position: "single",
                    }}
                  >
                    <Message.CustomContent>
                      <MarkdownMessage content={msg.message} />
                    </Message.CustomContent>
                  </Message>
                ))}
              </MessageList>
 

              <MessageInput
                placeholder="Input text here"
                onSend={handleSend}
                attachButton={false}
              />
            </ChatContainer>
          </MainContainer>
        </Box>
      )}

      <Button variant="contained" sx={style} onClick={toggleChat}>
        <ChatIcon />
      </Button>
    </>
  );
}
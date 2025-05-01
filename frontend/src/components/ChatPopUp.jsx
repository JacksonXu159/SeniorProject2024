import { useEffect, useState } from "react";
import { Box, Button, Typography } from "@mui/material";
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
import { useLocation } from "react-router-dom";

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

const SystemMessage = ({ content }) => (
  <div className="system-message">
    <div className="system-message-content">{content}</div>
  </div>
);

const ToolMessage = ({ content }) => (
  <div className="tool-message">
    <div className="tool-message-content">{content}</div>
  </div>
);

const MarkdownMessage = ({ content }) => {
  // Check if message is from live agent and add special styling
  const isLiveAgent = content.includes("**Live Agent");
  
  return (
    <div className={`markdown-message ${isLiveAgent ? "live-agent-message" : ""}`}>
      <ReactMarkdown rehypePlugins={[]}>{content}</ReactMarkdown>
    </div>
  );
};

export default function ChatPopUp() {
  const { userId } = useUserStore();
  const [messages, setMessages] = useState([
    { message: "Hi", sender: "Bot", direction: "incoming" },
  ]);
  const [typing, setTyping] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [currentSuggestionIndex, setCurrentSuggestionIndex] = useState(0);
  const { sendMessage, setOnComplete } = useGenAI();
  const { getSuggestions } = getSuggestionList();
  const [systemMessages, setSystemMessages] = useState([]);
  const [toolMessages, setToolMessages] = useState([]);
  const location = useLocation();

  const handleSuggestions = async (url) => {
    console.log("getting suggestions");
    const response = await getSuggestions();
    if (response) {
      console.log("response: ", response);
      if (Array.isArray(response)) {
        console.log("setting suggestions");
        setSuggestions(response);
      }
    }
  };

  const toggleChat = () => {
    console.log("Chat Open:", isChatOpen);
    setIsChatOpen((open) => !open);
    setCurrentSuggestionIndex(0);
    handleSuggestions();
  };

  useEffect(() => {
    setOnComplete(() => {
      setToolMessages([]);
      setSystemMessages([]);
    });
  }, [setOnComplete]);

  const handleSend = async (message) => {
    const newUserMessage = {
      message,
      sender: "user",
      direction: "outgoing",
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setTyping(true);

    let botMessage = { message: "", sender: "Bot", direction: "incoming" };
    setMessages((prev) => [...prev, botMessage]);

    try {
      // Pass userId along with the message
      await sendMessage(message, userId, (partialResponse) => {
        if (partialResponse.includes("🤔")) {
          setSystemMessages((prev) => [...prev, partialResponse]);
        } else if (
          partialResponse.includes("🔍") ||
          partialResponse.includes("Invoking:")
        ) {
          setToolMessages([partialResponse]);
        } else if (partialResponse === "[END]") {
          setTyping(false);
          setToolMessages([]);
          setSystemMessages([]);
        } else {
          setSystemMessages([]);
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...botMessage,
              message: prev[prev.length - 1].message + partialResponse,
            };
            return updated;
          });
        }
      });
    } catch (err) {
      console.error("Streaming error:", err);
      setTyping(false);
      setToolMessages([]);
      setSystemMessages([]);
    }
  };

  const nextSuggestion = () => {
    setCurrentSuggestionIndex(
      (prevIndex) => (prevIndex + 1) % suggestions.length
    );
  };

  const prevSuggestion = () => {
    setCurrentSuggestionIndex(
      (prevIndex) => (prevIndex - 1 + suggestions.length) % suggestions.length
    );
  };

  console.log("📋 suggestions state:", suggestions);

  useEffect(() => {
    // Reset all messages when userId changes
    setMessages([
      {
        message: "Hi! How can I help you today?",
        sender: "Bot",
        direction: "incoming",
      },
    ]);
    setSystemMessages([]);
    setToolMessages([]);
  }, [userId]);

    useEffect(() => {
        if (isChatOpen) {
            handleSuggestions();
        }
    }, [location.pathname, isChatOpen]);
    

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
            <button className="nav-button" onClick={prevSuggestion}>
              {"<"}
            </button>
            <button
              className="suggestion-button"
              onClick={() => handleSend(suggestions[currentSuggestionIndex])}
            >
              {suggestions[currentSuggestionIndex]}
            </button>
            <button className="nav-button" onClick={nextSuggestion}>
              {">"}
            </button>
          </div>

          <MainContainer style={{ maxHeight: "345px", bottom: "5px", flex: 1 }}>
            <ChatContainer
              style={{
                padding: "10px",
                display: "flex",
                flexDirection: "column",
                flex: 1,
              }}
            >
              <MessageList style={{ flex: 1 }}>
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
                {systemMessages.map((msg, i) => (
                  <SystemMessage key={`system-${i}`} content={msg} />
                ))}
                {toolMessages.map((msg, i) => (
                  <ToolMessage key={`tool-${i}`} content={msg} />
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

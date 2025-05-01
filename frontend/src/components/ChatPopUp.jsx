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
import OpenInFullIcon from "@mui/icons-material/OpenInFull";
import CloseFullscreenIcon from "@mui/icons-material/CloseFullscreen";
import CloseIcon from "@mui/icons-material/Close";


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
  const [isExpanded, setIsExpanded] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [currentSuggestionIndex, setCurrentSuggestionIndex] = useState(0);
  const { sendMessage, setOnComplete } = useGenAI();
  const { getSuggestions } = getSuggestionList();
  const [systemMessages, setSystemMessages] = useState([]);
  const [toolMessages, setToolMessages] = useState([]);
  const location = useLocation();

  const handleSuggestions = async () => {
    const response = await getSuggestions();
    if (Array.isArray(response)) setSuggestions(response);
  };

  const toggleChat = () => {
    setIsChatOpen((open) => !open);
    setCurrentSuggestionIndex(0);
    handleSuggestions();
  };

  const toggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  useEffect(() => {
    setOnComplete(() => {
      setToolMessages([]);
      setSystemMessages([]);
    });
  }, [setOnComplete]);

  useEffect(() => {
    if (isChatOpen && isExpanded) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isChatOpen, isExpanded]);

  const handleSend = async (message) => {
    const newUserMessage = { message, sender: "user", direction: "outgoing" };
    setMessages((prev) => [...prev, newUserMessage]);
    setTyping(true);

    const botMessage = { message: "", sender: "Bot", direction: "incoming" };
    setMessages((prev) => [...prev, botMessage]);

    try {
      await sendMessage(message, userId, (partial) => {
        if (partial.includes("🤔")) setSystemMessages((prev) => [...prev, partial]);
        else if (partial.includes("🔍") || partial.includes("Invoking:")) setToolMessages([partial]);
        else if (partial === "[END]") {
          setTyping(false);
          setToolMessages([]);
          setSystemMessages([]);
        } else {
          setSystemMessages([]);
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...botMessage,
              message: prev[prev.length - 1].message + partial,
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

  const nextSuggestion = () => setCurrentSuggestionIndex((i) => (i + 1) % suggestions.length);
  const prevSuggestion = () => setCurrentSuggestionIndex((i) => (i - 1 + suggestions.length) % suggestions.length);

  useEffect(() => {
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
    if (isChatOpen) handleSuggestions();
  }, [location.pathname, isChatOpen]);

  const chatBoxStyle = {
    position: "fixed",
    bottom: 65,
    right: 10,
    height: isExpanded ? "80vh" : "400px",
    width: isExpanded ? "600px" : "300px",
    zIndex: 1100,
    backgroundColor: "white",
    display: "flex",
    flexDirection: "column",
    borderRadius: "10px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
    overflow: "hidden",
    transition: "height 0.5s ease, width 0.5s ease", // Only animate size
  };

  return (
      <>
        {isChatOpen && isExpanded && (
            <Box
                onClick={toggleExpand}
                sx={{
                  position: "fixed",
                  top: 0,
                  left: 0,
                  width: "100vw",
                  height: "100vh",
                  backgroundColor: "rgba(0,0,0,0.4)",
                  zIndex: 1000,
                }}
            />
        )}

        {isChatOpen && (
            <Box sx={chatBoxStyle}>
              <div className="chat-header">
                Chat Assistant
                <div style={{ display: "flex", gap: "4px" }}>
                  <button className="chat-close-btn" onClick={toggleExpand}>
                    {isExpanded ? <CloseFullscreenIcon /> : <OpenInFullIcon />}
                  </button>
                  <Button onClick={toggleChat} size="small" variant="contained"
                          sx={{
                            minWidth: "32px",
                            padding: "2px",
                            backgroundColor: "white",
                            color: "black",
                          }}
                  >
                    <CloseIcon fontSize="small" />
                  </Button>
                </div>
              </div>

              <div className="suggestions-container">
                <button className="nav-button" onClick={prevSuggestion}>{"<"}</button>
                <button
                    className="suggestion-button"
                    onClick={() => handleSend(suggestions[currentSuggestionIndex])}
                >
                  {suggestions[currentSuggestionIndex]}
                </button>
                <button className="nav-button" onClick={nextSuggestion}>{">"}</button>
              </div>

              <MainContainer style={{ flex: 1, borderRadius: "10px", overflow: "hidden" }}>
                <ChatContainer style={{ padding: "10px", display: "flex", flexDirection: "column", flex: 1 }}>
                  <MessageList style={{ flex: 1 }}>
                    {messages.map((msg, i) => (
                        <Message
                            key={i}
                            model={{ sender: msg.sender, direction: msg.direction, position: "single" }}
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

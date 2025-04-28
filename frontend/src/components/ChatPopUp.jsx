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

let style = {
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

let boxStyle = {
  position: "fixed",
  bottom: 65,
  right: 10,
  height: "400px",
  width: "300px",
  zIndex: 1000,
  backgroundColor: "white",
  display: "block",
};

const MarkdownMessage = ({ content }) => {
  return (
    <div className="markdown-message">
      <ReactMarkdown rehypePlugins={[]}>{content}</ReactMarkdown>
    </div>
  );
};

function ChatPopUp({}) {
  const { userId, userData, fetchUserData } = useUserStore();

  const [messages, setMessages] = useState([
    {
      message: "Hi",
      sender: "Bot",
      direction: "incoming",
    },
  ]);

  const [typing, setTyping] = useState(false);

  const [isChatOpen, setIsChatOpen] = useState(false);

  const { sendMessage, data, loading } = useGenAI();

  const toggleChat = () => {
    if (!isChatOpen) {
      setIsChatOpen(true);
    } else {
      setIsChatOpen(false);
    }
  };

  const handleSend = async (message) => {
    setTyping(true);

    // Add user message to the chat
    const newUserMessage = {
      message,
      sender: "user",
      direction: "outgoing",
    };
    setMessages((prev) => [...prev, newUserMessage]);

    // Create an empty bot message that will be updated with partial responses
    let botMessage = { message: "", sender: "Bot", direction: "incoming" };
    setMessages((prev) => [...prev, botMessage]);

    try {
      // Call sendMessage once with the callback to update the UI
      await sendMessage(message, userId, (partialResponse) => {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...botMessage,
            message: partialResponse,
          };
          return updated;
        });
      });
    } catch (err) {
      console.error("Streaming error:", err);
    } finally {
      setTyping(false);
    }
  };

  useEffect(() => {
    setMessages([
      {
        message: "Hi",
        sender: "Bot",
        direction: "incoming",
      },
    ]);
  }, [userId]);

  return (
    <>
      {isChatOpen && (
        <Box sx={boxStyle}>
          <div className="chat-header">
            Chat Assistant
            <button className="chat-close-btn" onClick={toggleChat}>
              ✖
            </button>
          </div>
          <MainContainer style={{ height: "100%" }}>
            <ChatContainer style={{ padding: "10px" }}>
              <MessageList
                typingIndicator={
                  typing ? <TypingIndicator content="Bot is typing" /> : null
                }
              >
                {messages.map((message, i) => {
                  return (
                    <Message
                      key={i}
                      model={{
                        sender: message.sender,
                        direction: message.direction,
                        position: "single",
                      }}
                    >
                      <Message.CustomContent>
                        <MarkdownMessage content={message.message} />
                      </Message.CustomContent>
                    </Message>
                  );
                })}
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

export default ChatPopUp;

import { useState } from "react";
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
import "./ChatPopup.css";
import useGenAI from "../hooks/useGenAI";

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

function ChatPopUp({}) {
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
    const response = await sendMessage(message);
    console.log(response)
    const newUserMessage = {
      message: message,
      sender: "user",
      direction: "outgoing",
    };

    if (response) {
      const botResponse = {
        message: response.message,
        sender: "Bot",
        direction: "incoming",
      };
      setMessages([...messages, newUserMessage, botResponse]);
    } else {
      setMessages([...messages, newUserMessage]);
    }

    setTyping(false);
  };

  return (
    <>
      {isChatOpen && (
        <Box sx={boxStyle}>
          <MainContainer>
            <ChatContainer>
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
                        message: message.message,
                        sender: message.sender,
                        direction: message.direction,
                        position: "single",
                      }}
                    />
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

import { useState } from "react";
import axios from "axios";
import { API_URL } from "../config";

const url = `${API_URL}/message/`;

const useGenAI = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  const sendMessage = (userMessage, userId, onTokenReceived) => {
    setLoading(true);

    return new Promise((resolve, reject) => {
      const socket = new WebSocket("ws://127.0.0.1:8000/ws/chat");

      let fullMessage = "";
      let thinkingMessage = "";
      let answerMessage = "";
      let isThinking = true;

      socket.onopen = () => {
        const frontendUrl = window.location.origin;
        const messageJSON = {
          message: userMessage,
          frontendUrl: frontendUrl,
          userId: userId,
        };

        socket.send(JSON.stringify(messageJSON));
      };

      socket.onmessage = (event) => {
        if (event.data === "[END]") {
          setLoading(false);
          resolve({ message: fullMessage });
          socket.close();
        } else if (event.data === "[END_THINKING]") {
          // Switch from thinking to answer mode
          isThinking = false;
          // Send the thinking message to the UI
          if (onTokenReceived) {
            onTokenReceived(thinkingMessage, true);
          }
        } else {
          // Accumulate the full message
          fullMessage += event.data;

          // If in thinking mode, accumulate thinking message
          if (isThinking) {
            thinkingMessage += event.data;
            // Send partial update to UI for thinking
            if (onTokenReceived) {
              onTokenReceived(thinkingMessage, true);
            }
          } else {
            // In answer mode, accumulate answer message
            answerMessage += event.data;
            // Send partial update to UI for answer
            if (onTokenReceived) {
              onTokenReceived(answerMessage, false);
            }
          }
        }
      };

      socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        setLoading(false);
        reject(error);
        socket.close();
      };
    });
  };

  return { sendMessage, data, error, loading };
};

export default useGenAI;

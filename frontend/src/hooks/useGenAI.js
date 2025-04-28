import { useState } from "react";

const useGenAI = () => {
  const [loading, setLoading] = useState(false);

  const sendMessage = (userMessage, onTokenReceived) => {
    setLoading(true);

    return new Promise((resolve, reject) => {
      const socket = new WebSocket("ws://127.0.0.1:8000/ws/chat");

      let fullMessage = "";

      socket.onopen = () => {
        const frontendUrl = window.location.origin;
        const messageJSON = {
          message: userMessage,
          frontendUrl,
        };

        socket.send(JSON.stringify(messageJSON));
      };

      socket.onmessage = (event) => {
        if (event.data === "[END]") {
          setLoading(false);
          resolve({ message: fullMessage });
          socket.close();
        } else {
          fullMessage += event.data;
          if (onTokenReceived) {
            onTokenReceived(fullMessage); // Send partial update to UI
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

  return { sendMessage, loading };
};

export default useGenAI;

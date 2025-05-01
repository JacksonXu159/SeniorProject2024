import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { API_URL } from "../config";

const useGenAI = () => {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const wsRef = useRef(null);
  const onCompleteRef = useRef(null);

  useEffect(() => {
    // Initialize WebSocket connection
    wsRef.current = new WebSocket(
      `ws://${API_URL.replace("http://", "")}/ws/chat`
    );

    wsRef.current.onopen = () => {
      console.log("WebSocket connected");
    };

    wsRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      setError(error);
    };

    wsRef.current.onclose = () => {
      console.log("WebSocket closed");
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const sendMessage = async (message, onPartialResponse) => {
    setLoading(true);
    setError(null);

    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setError(new Error("WebSocket not connected"));
      setLoading(false);
      return;
    }

    try {
      // Send the message
      wsRef.current.send(message);

      // Set up message handler for streaming
      const messageHandler = (event) => {
        if (event.data === "[END]") {
          wsRef.current.removeEventListener("message", messageHandler);
          setLoading(false);
          if (onCompleteRef.current) {
            onCompleteRef.current();
          }
        } else {
          onPartialResponse(event.data);
        }
      };

      wsRef.current.addEventListener("message", messageHandler);
    } catch (err) {
      setError(err);
      console.error("Error in sendMessage:", err);
      setLoading(false);
    }
  };

  const setOnComplete = (callback) => {
    onCompleteRef.current = callback;
  };

  return { sendMessage, data, error, loading, setOnComplete };
};

export default useGenAI;

import { useState } from "react";
import axios from "axios";
import { API_URL } from '../config'

const url = `${API_URL}/message/`; 

const useGenAI = () => {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const sendMessage = async (userMessage, userId) => {
        setLoading(true);
        setError(null);
        const frontendUrl = window.location.origin;      // e.g. "https://app.example.com"
        const currentPath   = window.location.pathname;    // e.g. "/transactions"
        console.log("Frontend URL:", frontendUrl);
        console.log("Current path:", currentPath);
    
        const messageJSON = {
            message: userMessage,
            frontendUrl,
            currentPath, 
            userId,
          };
        
        console.log("Sending request with:", messageJSON);
    
        try {
            const response = await axios.post(url, messageJSON);
            console.log("Received response:", response.data);
            setData(response.data);
            return response.data;
        } catch (err) {
            setError(err);
            console.error("Error in sendMessage:", err);
            return null;
        } finally {
            setLoading(false);
        }
    };
    
    return { sendMessage, data, error, loading };
};

export default useGenAI;
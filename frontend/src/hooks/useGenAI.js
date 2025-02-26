import { useState } from "react";
import axios from "axios";

const url = "http://44.193.233.90/message";

const useGenAI = () => {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const sendMessage = async (userMessage) => {
        setLoading(true);
        setError(null);

        const messageJSON = { message: userMessage };

        try {
            const response = await axios.post(url, messageJSON);
            setData(response.data);
            return response.data;
        } catch (err) {
            setError(err);
            console.error(err);
            return null;
        } finally {
            setLoading(false);
        }
    };

    return { sendMessage, data, error, loading };
};

export default useGenAI;

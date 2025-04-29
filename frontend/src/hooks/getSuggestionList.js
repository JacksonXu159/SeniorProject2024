import { useState } from "react";
import axios from "axios";
import { API_URL } from '../config'

const url = `${API_URL}/get_suggestions`; 

const getSuggestionList = () => {
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const getSuggestions = async () => {
        setLoading(true);
        setError(null);
        const currentPath   = window.location.pathname.toString().trim();    // e.g. "/transactions"
        // currentPath = currentPath.toString().trim();
        console.log("sending:", url + currentPath);
    
    
        try {
            const response = await axios.post(`${url}${currentPath}`);
            console.log("Received response:", response.data);
            setData(response.data);
            return response.data;
        } catch (err) {
            setError(err);
            console.error("Error in getSuggestions:", err);
            return null;
        } finally {
            setLoading(false);
        }
    };
    
    return { getSuggestions, data, error, loading };
};

export default getSuggestionList;
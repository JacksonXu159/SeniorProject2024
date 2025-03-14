import { useState, useEffect } from "react";
import axios from "axios";
import { API_URL } from '../config'

const url = `${API_URL}/get_user/`;

const useUserData = (userId) => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) return;

    const fetchUserData = async () => {
      setLoading(true);
      try {
        const response = await axios.post(
          url,
          {
            user_id: userId,
          },
          {
            headers: { "Content-Type": "application/json" }, // Ensure JSON request
          }
        );
        setUserData(response.data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || "Failed to fetch user data");
        setUserData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [userId]);

  return { userData, loading, error };
};

export default useUserData;

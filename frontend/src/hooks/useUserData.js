import { useState, useEffect } from "react";
import axios from "axios";

const url = "http://127.0.0.1:8000/get_user"; // Local
// const url = "http://44.193.233.90/get_user"; // Production

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

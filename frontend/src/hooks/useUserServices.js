import { useState, useEffect } from 'react'; 
import { API_URL } from '../config'

const url = API_URL;

export const useUserServices = (userId, { fetchOnMount = true } = {}) => {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchServices = async () => {
    if (!userId) {
      setError('User ID is required');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${url}/user/${userId}/services/`);
      
      if (!response.ok) {
        throw new Error(`Error fetching services: ${response.status}`);
      }
      
      const data = await response.json();
      setServices(data.services || []);
    } catch (err) {
      console.error(`Failed to fetch services for user ${userId}:`, err);
      setError(err.message || 'Failed to fetch user services');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userId && fetchOnMount) {
      fetchServices();
    }
  }, [userId, fetchOnMount]);

  return { services, loading, error, refetch: fetchServices };
};

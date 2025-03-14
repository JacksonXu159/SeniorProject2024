import { useState, useEffect } from 'react';
import { API_URL } from '../config'

const url = `${API_URL}/users/`;

export const useUsers = ({ fetchOnMount = true } = {}) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`Error fetching users: ${response.status}`);
      }
      
      const data = await response.json();
      setUsers(data.users || []);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError(err.message || 'Failed to fetch users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (fetchOnMount) {
      fetchUsers();
    }
  }, [fetchOnMount]);

  return { users, loading, error, refetch: fetchUsers };
};


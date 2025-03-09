import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import axios from 'axios';

// const url = "http://localhost:8000/get_user"; // Local
const url = "http://44.193.233.90/get_user"; // Production

export const useUserStore = create(
  persist(
    (set, get) => ({
      userId: "5e655314-c264-4999-83ad-67c43cc6db5b",
      userData: null,
      loading: false,
      error: null,

      // New method just for fetching data
      fetchUserData: async () => {
        const currentUserId = get().userId;
        set({ loading: true, error: null });
        
        try {
          const response = await axios.post(
            url,
            { user_id: currentUserId },
            { headers: { "Content-Type": "application/json" } }
          );
          
          set({
            userData: response.data,
            loading: false,
            error: null
          });
        } catch (err) {
          set({
            userData: null,
            loading: false,
            error: err.response?.data?.detail || "Failed to fetch user data"
          });
        }
      },

      // Updated to use the new fetchUserData method
      setUserId: (newUserId) => {
        set({ userId: newUserId });
        get().fetchUserData();
      },

      // Reset store if needed
      reset: () => set({ 
        userId: "5e655314-c264-4999-83ad-67c43cc6db5b", 
        userData: null, 
        loading: false, 
        error: null 
      })
    }),
    {
      name: 'user-storage', // unique name
      storage: createJSONStorage(() => localStorage), // data will be stored in localStorage
      partialize: (state) => ({
        userId: state.userId,
        userData: state.userData
      }) // only persist these specific fields
    }
  )
);
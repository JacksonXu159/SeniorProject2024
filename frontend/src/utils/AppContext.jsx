import { createContext, useContext, useState, useEffect } from "react";
import useUserData from "../hooks/useUserData";

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [userId, setUserId] = useState("5e655314-c264-4999-83ad-67c43cc6db5b");
  const { userData, loading, error } = useUserData(userId); 

  useEffect(() => {
    console.log("Fetching user data for:", userId);
  }, [userId]); 

  return (
    <AppContext.Provider value={{ userId, setUserId, userData, loading, error }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => useContext(AppContext);

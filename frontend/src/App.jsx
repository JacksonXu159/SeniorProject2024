import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "./utils/theme";
import { Routes, Route } from "react-router-dom";
import { AppProvider } from "./utils/AppContext";
import { useEffect} from "react";

import Dashboard from "./pages/Dashboard";
import Account from "./pages/Account";
import Services from "./pages/Services";
import Settings from "./pages/Settings";
import Navbar from "./components/Navbar";
import ChatPopUp from "./components/ChatPopUp";
import FinancialAccountDetail from "./pages/FinancialAccountDetail";
import { useUserStore } from "./hooks/useUserStore";

function App() {
  const { userId, setUserId, userData, loading, error, fetchUserData } = useUserStore();
  
  
  useEffect(() => {
    // Fetch user data when app starts
    fetchUserData();
  }, [userId, fetchUserData]);

  return (
    <div className="App">
      <AppProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Navbar />

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/Dashboard" element={<Dashboard />} />
            <Route path="/Account" element={<Account />} />
            <Route path="/Services" element={<Services />} />
            <Route path="/Settings" element={<Settings />} />
            <Route path="/Transactions" element={<FinancialAccountDetail />} />
          </Routes>

          <ChatPopUp />
        </ThemeProvider>
      </AppProvider>
    </div>
  );
}

export default App;

import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "./utils/theme";
import { Routes, Route } from "react-router-dom";
import { AppProvider } from "./utils/AppContext";
import { useState } from "react";

import Dashboard from "./pages/Dashboard";
import Account from "./pages/Account";
import Services from "./pages/Services";
import Settings from "./pages/Settings";
import Navbar from "./components/Navbar";
import ChatPopUp from "./components/ChatPopUp";
import FinancialAccountDetail from "./pages/FinancialAccountDetail";

function App() {
  return (
    <div className="App">
      <AppProvider>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Navbar />

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/account" element={<Account />} />
            <Route path="/services" element={<Services />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/details/:accountId" element={<FinancialAccountDetail />} />
          </Routes>

          <ChatPopUp />
        </ThemeProvider>
      </AppProvider>
    </div>
  );
}

export default App;

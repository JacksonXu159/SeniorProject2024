import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "./utils/theme";
import { Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Account from "./pages/Account"
import Services from "./pages/Services"
import Settings from "./pages/Settings"
import Navbar from "./components/Navbar";
import ChatPopUp from "./components/ChatPopUp";

function App() {
  return (
    <div className="App">
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Navbar />

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/account" element={<Account/>} />
          <Route path="/services" element={<Services/>} />
          <Route path="/settings" element={<Settings/>} />
        </Routes>
        
        <ChatPopUp />
      </ThemeProvider>
    </div>
  );
}

export default App;

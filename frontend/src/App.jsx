import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "./utils/theme";
import { Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
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
        </Routes>
        
        <ChatPopUp />
      </ThemeProvider>
    </div>
  );
}

export default App;

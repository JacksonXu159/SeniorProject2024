import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "./utils/theme";

import Dashboard from "./components/Dashboard";
import Navbar from "./components/Navbar";
import ChatPopUp from "./components/ChatPopUp";
function App() {
    return (
        <div className="App">
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <Navbar />
                <Dashboard />
            </ThemeProvider>
            <ChatPopUp />
        </div>
    );
}

export default App;

import { ThemeProvider, CssBaseline } from "@mui/material";
import theme from "./utils/theme";

import Dashboard from "./components/Dashboard";
import Navbar from "./components/Navbar";

function App() {
  return (
    <div className="App">
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Navbar />
        <Dashboard />
      </ThemeProvider>
    </div>
  );
}

export default App;

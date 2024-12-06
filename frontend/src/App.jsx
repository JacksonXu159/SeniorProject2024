import "./App.css";
import { Box, Button, Typography } from "@mui/material";
import { ThemeProvider, CssBaseline } from "@mui/material";

import theme from "./utils/theme";
import Navbar from "./components/Navbar";

function App() {
  const accounts = [
    {
      type: "Individual",
      value: "$38,558.92",
      account: "47376967",
      status: "",
    },
    {
      type: "Individual",
      value: "",
      account: "",
      status: "(closed)",
      description: "View past statements & transactions",
    },
    { type: "Super", value: "$125,929.09", account: "233360627", status: "" },
    { type: "Kids (John)", value: "$0.00", account: "57280059", status: "" },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ height: "100vh", display: "flex", flexDirection: "column" }}>
        <Navbar />
        <Box sx={{ margin: "64px", padding: "16px" }}>
          <Typography variant="h1">Hello world!</Typography>
          <Button variant="contained" color="primary">
            Hi there
          </Button>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;

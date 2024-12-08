import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: {
      main: "#8a2423", 
      contrastText: "#ffffff", 
    },
    background: {
      default: "#f4f6f8", 
      paper: "#ffffff", 
    },
    text: {
      primary: "#333333", 
      secondary: "#666666", 
    },
  },
  typography: {
    fontFamily: "'Roboto', 'Helvetica', 'Arial', sans-serif",
    h1: {
      fontSize: "2.5rem",
      fontWeight: 700,
    },
    h6: {
      fontSize: "1.25rem",
      fontWeight: 500,
    },
    button: {
      textTransform: "none", 
    },
  },
  components: {
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: "none", 
          backgroundColor: "#f4f6f8", 
        },
      },
    },
  },
});

export default theme;

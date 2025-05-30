import React from "react";
import { Box, Typography, Link } from "@mui/material";

const AccountCard = ({ account }) => (
  <Box
    sx={{
      backgroundColor: "background.paper",
      borderRadius: 2,
      padding: 2,
      display: "flex",
      flexDirection: "column",
      alignItems: "flex-start",
      transition: "background-color 0.3s ease",
      "&:hover": {
        backgroundColor: "action.hover",
        cursor: "pointer",
      },
    }}
  >
    <Typography variant="h6" color="text.primary">
      {account.portfolioType}
    </Typography>
    <Typography variant="h4" color="primary.main">
      $
      {parseFloat(account.balance || 0).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}
    </Typography>
    <Typography variant="h6" color="text.primary">
      {account.portfolioId}
    </Typography>
  </Box>
);

export default AccountCard;

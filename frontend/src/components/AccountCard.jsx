// AccountCard.jsx
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
    <Link
      href={'details/'+account.id}
      style={{ textDecoration: "none", color: "inherit", width: "100%" }}
    >
      <Typography variant="h6" color="text.primary">
        {account.type}
      </Typography>
      <Typography variant="h4" color="primary.main">
        {account.value || "-"}
      </Typography>
    </Link>
  </Box>
);

export default AccountCard;

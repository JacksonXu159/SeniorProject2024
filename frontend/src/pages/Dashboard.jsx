// Dashboard.jsx
import React from "react";
import { useState, useEffect } from "react";
import { Box, Typography } from "@mui/material";
import AccountCard from "../components/AccountCard";
import { useUserStore } from "../hooks/useUserStore";

const Dashboard = () => {
  const [total, setTotal] = useState(0);

  const { userId, setUserId, userData, loading, error } = useUserStore();
  const portfolios = userData.portfolios;

  useEffect(() => {
    const computedTotal = portfolios.reduce((sum, account) => {
      const numericValue = parseFloat(account.balance) || 0;
      return sum + numericValue;
    }, 0);
    setTotal(computedTotal);
  }, [userData, userId]);

  return (
    <Box
      sx={{
        margin: "64px",
        padding: "16px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        flex: 1,
      }}
    >
      <Typography variant="h1" color="primary.main">
        ${total.toLocaleString("en-US", { minimumFractionDigits: 2 })}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
        Combined Portfolio Value
      </Typography>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
          gap: 4,
          mt: 4,
          width: "100%",
        }}
      >
        {portfolios.map((account, index) => (
          <AccountCard
            key={index}
            account={account}
          />
        ))}
      </Box>
    </Box>
  );
};

export default Dashboard;

// Dashboard.jsx
import React from "react";
import { useState, useEffect } from "react";
import { Box, Typography } from "@mui/material";
import AccountCard from "../components/AccountCard";

const Dashboard = () => {
  const [total, setTotal] = useState(0);

  const [accounts, setAccounts] = useState([
    {
      type: "Retirement Account (IRA)",
      value: "$587,497.75",
      id: "123"
    },
    {
      type: "Joint Brokerage Account",
      value: "$842,048.84",
      id: "321"
    },
    
  ]);

  useEffect(() => {
    const computedTotal = accounts.reduce((sum, account) => {
      const numericValue = parseFloat(account.value.replace(/[$,]/g, "")) || 0;
      return sum + numericValue;
    }, 0);
    setTotal(computedTotal);
  }, [accounts]);

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
        {accounts.map((account) => (
          <AccountCard key={account.account} account={account}/>
        ))}
      </Box>
    </Box>
  );
};

export default Dashboard;

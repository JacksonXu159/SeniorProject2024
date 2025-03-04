import React from "react";
import { useParams } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { Box, Typography, Paper, List, ListItem, ListItemText, Divider, Container } from "@mui/material";

const useAccountContext = () => {
  return {
    getAccountById: (id) => ({
      id,
      type: "Checking",
      balance: "$5,420.75",
      currency: "USD",
      createdAt: "2023-03-10",
    }),
  };
};

const mockTransactions = [
  { id: "T123", amount: "-$50.00", type: "Purchase", date: "2025-02-20" },
  { id: "T124", amount: "+$1,200.00", type: "Salary", date: "2025-02-18" },
  { id: "T125", amount: "-$15.99", type: "Subscription", date: "2025-02-15" },
];

const mockOrders = [
  { id: "O789", item: "Stocks", price: "$1,299.99", date: "2025-01-28" },
  { id: "O790", item: "Bonds", price: "$199.99", date: "2025-01-15" },
];

const FinancialAccountDetail = () => {
  const { accountId, section } = useParams(); // Get account ID and section
  const { getAccountById } = useAccountContext();
  const account = getAccountById(accountId);
  const [totalTransactions, setTotalTransactions] = useState(0);

  // Create refs for each section
  const bankDetailRef = useRef(null);
  const transactionsRef = useRef(null);
  const ordersRef = useRef(null);

  // Calculate total transaction amount
  useEffect(() => {
    const total = mockTransactions.reduce((sum, transaction) => {
      const value = parseFloat(transaction.amount.replace(/[+$,]/g, "")) || 0;
      return transaction.amount.startsWith("+") ? sum + value : sum - value;
    }, 0);
    setTotalTransactions(total);
  }, []);

  // Scroll to the section when the component loads
  useEffect(() => {
    if (section) {
      const sectionRefs = {
        bankDetail: bankDetailRef,
        transactions: transactionsRef,
        orders: ordersRef,
      };

      const targetRef = sectionRefs[section];
      if (targetRef?.current) {
        targetRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }
  }, [section]);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box
        sx={{
          padding: { xs: 2, md: 3 },
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          width: "100%"
        }}
      >
        {/* Header with account balance - matching dashboard styling */}
        <Typography variant="h2" color="primary.main">
          {account.balance}
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mt: 1, mb: 4 }}>
          {account.type} Balance
        </Typography>

        {/* Bank Details Section */}
        <Box sx={{ width: "100%", mb: 4 }} ref={bankDetailRef}>
          <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
            Account Details
          </Typography>
          <Paper 
            elevation={2} 
            sx={{ 
              padding: 3, 
              borderRadius: 2,
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "repeat(2, 1fr)" },
              gap: 2
            }}
          >
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Account ID</Typography>
              <Typography variant="body1" fontWeight="medium">{account.id}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Type</Typography>
              <Typography variant="body1" fontWeight="medium">{account.type}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Currency</Typography>
              <Typography variant="body1" fontWeight="medium">{account.currency}</Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">Created On</Typography>
              <Typography variant="body1" fontWeight="medium">{account.createdAt}</Typography>
            </Box>
          </Paper>
        </Box>

        {/* Transactions Section */}
        <Box sx={{ width: "100%", mb: 4 }} ref={transactionsRef}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
            <Typography variant="h5" gutterBottom>
              Recent Transactions
            </Typography>
            <Typography variant="h6" color={totalTransactions >= 0 ? "success.main" : "error.main"}>
              {totalTransactions >= 0 ? "+" : ""}{totalTransactions.toLocaleString("en-US", { style: "currency", currency: "USD" })}
            </Typography>
          </Box>
          <Paper elevation={2} sx={{ borderRadius: 2 }}>
            <List sx={{ p: 0 }}>
              {mockTransactions.map((tx, index) => (
                <React.Fragment key={tx.id}>
                  <ListItem sx={{ px: 3, py: 2 }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", width: "100%" }}>
                      <Box>
                        <Typography variant="body1" fontWeight="medium">{tx.type}</Typography>
                        <Typography variant="body2" color="text.secondary">{tx.date}</Typography>
                      </Box>
                      <Typography 
                        variant="body1" 
                        fontWeight="medium" 
                        color={tx.amount.startsWith("+") ? "success.main" : "inherit"}
                      >
                        {tx.amount}
                      </Typography>
                    </Box>
                  </ListItem>
                  {index < mockTransactions.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Box>

        {/* Orders Section */}
        <Box sx={{ width: "100%" }} ref={ordersRef}>
          <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
            Recent Orders
          </Typography>
          <Paper elevation={2} sx={{ borderRadius: 2 }}>
            <List sx={{ p: 0 }}>
              {mockOrders.map((order, index) => (
                <React.Fragment key={order.id}>
                  <ListItem sx={{ px: 3, py: 2 }}>
                    <Box sx={{ display: "flex", justifyContent: "space-between", width: "100%" }}>
                      <Box>
                        <Typography variant="body1" fontWeight="medium">{order.item}</Typography>
                        <Typography variant="body2" color="text.secondary">{order.date}</Typography>
                      </Box>
                      <Typography variant="body1" fontWeight="medium">
                        {order.price}
                      </Typography>
                    </Box>
                  </ListItem>
                  {index < mockOrders.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Box>
      </Box>
    </Container>
  );
};

export default FinancialAccountDetail;
import { useState } from "react";
import {
  User,
  Settings,
  MessageCircle,
  FileText,
  Banknote,
  Mail,
  Shield,
  Bell,
  Key,
  HelpCircle,
  MessageSquare,
  Scale,
  Phone,
  LogOut
} from "lucide-react";
import {
  Box,
  Button,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar
} from "@mui/material";

const Account = () => {
  const userData = {
    firstName: "John",
    lastName: "Johnson",
    email: "john.johnson@example.com",
    accountId: "VG-7849261",
    riskTolerance: "Medium",
    maritalStatus: "Single"
  };

  const menuItems = {
    Account: [
      { title: "Message Center", icon: <MessageCircle size={20} /> },
      { title: "Document Center", icon: <FileText size={20} /> },
      { title: "Banking Preferences", icon: <Banknote size={20} /> },
      { title: "Account Preferences", icon: <User size={20} /> },
      { title: "Paperless Delivery", icon: <Mail size={20} /> },
    ],
    Settings: [
      { title: "Authentication Requests", icon: <Shield size={20} /> },
      { title: "Notifications", icon: <Bell size={20} /> },
      { title: "Login & Security", icon: <Key size={20} /> },
    ],
    Support: [
      { title: "FAQs", icon: <HelpCircle size={20} /> },
      { title: "Feedback", icon: <MessageSquare size={20} /> },
      { title: "Legal", icon: <Scale size={20} /> },
      { title: "Contact Us", icon: <Phone size={20} /> },
    ],
  };

  const handleLogout = () => {
    console.log("Logging out...");
  };

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#f5f5f5", p: 4 }}>
      <Box sx={{ maxWidth: 1200, mx: "auto" }}>
        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            gap: 4,
          }}
        >
          <Box sx={{ flex: "1 1 300px" }}>
            <Paper 
              sx={{ 
                p: 3, 
                mb: 4, 
                display: "flex", 
                alignItems: "center", 
                gap: 2,
                backgroundColor: "#fff",
                borderRadius: 2,
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
              }}
            >
              <Avatar 
                sx={{ 
                  width: 60, 
                  height: 60, 
                  bgcolor: "#1976d2",
                  fontSize: "1.5rem"
                }}
              >
                {userData.firstName[0]}{userData.lastName[0]}
              </Avatar>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {userData.firstName} {userData.lastName}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {userData.accountId}
                </Typography>
              </Box>
            </Paper>

            {Object.entries(menuItems).map(([category, items]) => (
              <Paper 
                key={category} 
                sx={{ 
                  mb: 4, 
                  p: 2,
                  backgroundColor: "#fff",
                  borderRadius: 2,
                  boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
                }}
              >
                <Typography variant="h6" sx={{ mb: 2, pl: 2, fontWeight: 600 }}>
                  {category}
                </Typography>
                <List>
                  {items.map((item, index) => (
                    <ListItem
                      key={`${category}-${item.title}-${index}`}
                      sx={{ 
                        borderRadius: 1,
                        cursor: "pointer",
                        "&:hover": {
                          backgroundColor: "#f5f5f5"
                        }
                      }}
                    >
                      <ListItemIcon sx={{ color: "#1976d2" }}>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.title} />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            ))}

            <Button
              variant="outlined"
              color="error"
              startIcon={<LogOut size={20} />}
              onClick={handleLogout}
              fullWidth
              sx={{ 
                mt: 2,
                p: 1.5,
                borderRadius: 2,
                textTransform: "none",
                fontSize: "1rem"
              }}
            >
              Log Out
            </Button>
          </Box>

          <Box sx={{ flex: "2 1 600px" }}>
            <Paper 
              sx={{ 
                p: 4,
                backgroundColor: "#fff",
                borderRadius: 2,
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
              }}
            >
              <Typography variant="h5" sx={{ mb: 4, fontWeight: 600 }}>
                Profile Information
              </Typography>

              <Box sx={{ display: "grid", gap: 3 }}>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Full Name
                  </Typography>
                  <Typography variant="body1">
                    {userData.firstName} {userData.lastName}
                  </Typography>
                </Box>
                <Divider />
                
                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Email Address
                  </Typography>
                  <Typography variant="body1">{userData.email}</Typography>
                </Box>
                <Divider />

                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Account ID
                  </Typography>
                  <Typography variant="body1">{userData.accountId}</Typography>
                </Box>
                <Divider />

                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Risk Tolerance
                  </Typography>
                  <Typography variant="body1">{userData.riskTolerance}</Typography>
                </Box>
                <Divider />

                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Marital Status
                  </Typography>
                  <Typography variant="body1">{userData.maritalStatus}</Typography>
                </Box>
              </Box>
            </Paper>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default Account;
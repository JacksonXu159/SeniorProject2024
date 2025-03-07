import { useState, useContext, useEffect } from "react";
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
  LogOut,
  Users,
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
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
} from "@mui/material";

import { useAppContext } from "../utils/AppContext";
import { useUserStore } from "../hooks/useUserStore";

const Account = () => {
  const [switchAccountOpen, setSwitchAccountOpen] = useState(false);
  const { userId, setUserId, userData, loading, error } = useUserStore();
  console.log(userData)

  const allUsers = [
    {
      name: "John Johnson",
      id: "b85c001a-4d7e-4f5d-a918-fb35dcd9c47c",
      risk: "Medium",
      status: "Single",
    },
    {
      name: "Michael Williams",
      id: "dc67a009-5d09-443c-a75e-9eac836ac917",
      risk: "Medium",
      status: "Divorced",
    },
    {
      name: "Christina Davis",
      id: "accd1488-2997-4155-b634-6e8ce29ad006",
      risk: "Medium",
      status: "Married",
    },
    {
      name: "Emily Brown",
      id: "67d3701e-7fda-4191-9c95-07e5dedfccd2",
      risk: "Medium",
      status: "Single",
    },
    {
      name: "Katie Rodriguez",
      id: "ceb7ee2f-26fd-4317-abb2-737e4e438f81",
      risk: "Medium",
      status: "Married",
    },
    {
      name: "David Garcia",
      id: "b2d2f6b8-e9fa-49d1-a37f-35c35f9de857",
      risk: "High",
      status: "Divorced",
    },
    {
      name: "Alex Williams",
      id: "dbeda121-4c5a-49d6-bc54-64aca5d69531",
      risk: "Low",
      status: "Single",
    },
    {
      name: "John Smith",
      id: "a58b37e3-f251-4ccd-8c7c-507a3fcf2a71",
      risk: "High",
      status: "Divorced",
    },
    {
      name: "Jane Brown",
      id: "dab0ed72-e100-4337-8d27-166dbad39acf",
      risk: "High",
      status: "Married",
    },
    {
      name: "Laura Davis",
      id: "5e655314-c264-4999-83ad-67c43cc6db5b",
      risk: "Medium",
      status: "Single",
    },
  ];

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

  const handleSwitchAccount = (userName, newUserId) => {
    setSwitchAccountOpen(false);
    setUserId(newUserId);
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
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              }}
            >
              <Avatar
                sx={{
                  width: 60,
                  height: 60,
                  bgcolor: "#1976d2",
                  fontSize: "1.5rem",
                }}
              >
                {userData.accountName
                  .split(" ")
                  .map((n) => n[0])
                  .join("")}
              </Avatar>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {userData.accountName}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {userId}
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
                  boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
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
                          backgroundColor: "#f5f5f5",
                        },
                      }}
                    >
                      <ListItemIcon sx={{ color: "#1976d2" }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText primary={item.title} />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            ))}

            <Button
              variant="outlined"
              color="primary"
              startIcon={<Users size={20} />}
              onClick={() => setSwitchAccountOpen(true)}
              fullWidth
              sx={{
                mt: 2,
                p: 1.5,
                borderRadius: 2,
                textTransform: "none",
                fontSize: "1rem",
              }}
            >
              Switch Account
            </Button>
          </Box>

          <Box sx={{ flex: "2 1 600px" }}>
            <Paper
              sx={{
                p: 4,
                backgroundColor: "#fff",
                borderRadius: 2,
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
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
                    {userData.accountName}
                  </Typography>
                </Box>
                <Divider />

                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Account ID
                  </Typography>
                  <Typography variant="body1">{userId}</Typography>
                </Box>
                <Divider />

                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Risk Tolerance
                  </Typography>
                  <Typography variant="body1">{userData.risktolerance}</Typography>
                </Box>
                <Divider />

                <Box>
                  <Typography variant="subtitle2" color="text.secondary">
                    Marital Status
                  </Typography>
                  <Typography variant="body1">{userData.maritalstatus}</Typography>
                </Box>
              </Box>
            </Paper>
          </Box>
        </Box>
      </Box>

      <Dialog
        open={switchAccountOpen}
        onClose={() => setSwitchAccountOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ fontWeight: 600 }}>Switch Account</DialogTitle>
        <DialogContent>
          <List>
            {allUsers.map((user) => (
              <ListItem
                key={user.id}
                onClick={() => handleSwitchAccount(user.name, user.id)}
                sx={{
                  cursor: "pointer",
                  borderRadius: 1,
                  mb: 1,
                  backgroundColor:
                    user.name === userData.accountName ? "#f0f7ff" : "transparent",
                  "&:hover": {
                    backgroundColor: "#f5f5f5",
                  },
                }}
              >
                <ListItemIcon>
                  <Avatar sx={{ bgcolor: "#1976d2" }}>
                    {user.name
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={user.name}
                  secondary={`ID: ${user.id} • Risk: ${user.risk}`}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default Account;

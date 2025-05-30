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

import { useUserStore } from "../hooks/useUserStore";
import { useUsers } from "../hooks/useUsers";

const Account = () => {
  const [switchAccountOpen, setSwitchAccountOpen] = useState(false);
  const { userId, setUserId, userData} = useUserStore();
  const { users} = useUsers();

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
            {users.map((user) => (
              <ListItem
                key={user.accountid}
                onClick={() => handleSwitchAccount(user.accountname, user.accountid)}
                sx={{
                  cursor: "pointer",
                  borderRadius: 1,
                  mb: 1,
                  backgroundColor:
                  user.accountname === userData.accountName ? "#f0f7ff" : "transparent",
                  "&:hover": {
                    backgroundColor: "#f5f5f5",
                  },
                }}
              >
                <ListItemIcon>
                  <Avatar sx={{ bgcolor: "#1976d2" }}>
                    {user.accountname
                      .split(" ")
                      .map((n) => n[0])
                      .join("")}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={user.accountname}
                  secondary={`• Risk: ${user.risktolerance}`}
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

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
} from "lucide-react";
import {
  Box,
  Button,
  Paper,
  TextField,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from "@mui/material";

const Account = () => {
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    firstName: "John",
    lastName: "Doe",
    email: "john.doe@example.com",
    phone: "+1 (555) 123-4567",
  });

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

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "grey.100", p: 4 }}>
      <Box sx={{ maxWidth: 1200, mx: "auto" }}>
        <Box
          sx={{
            display: "flex",
            flexDirection: { xs: "column", md: "row" },
            gap: 4,
          }}
        >
          {/* Navigation Menu */}
          <Box sx={{ flex: "1 1 300px" }}>
            {Object.entries(menuItems).map(([category, items]) => (
              <Paper key={category} sx={{ mb: 4, p: 2 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  {category}
                </Typography>
                <List>
                  {items.map((item, index) => (
                    <ListItem
                      key={`${category}-${item.title}-${index}`}
                      sx={{ borderRadius: 1 }}
                    >
                      <ListItemIcon>{item.icon}</ListItemIcon>
                      <ListItemText primary={item.title} />
                    </ListItem>
                  ))}
                </List>
              </Paper>
            ))}
          </Box>

          {/* Profile Content */}
          <Box sx={{ flex: "2 1 600px" }}>
            <Paper sx={{ p: 4 }}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 4,
                }}
              >
                <Typography variant="h5">Profile Information</Typography>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => setEditMode(!editMode)}
                >
                  {editMode ? "Save Changes" : "Edit Profile"}
                </Button>
              </Box>

              <Box
                sx={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 3,
                }}
              >
                <Box sx={{ flex: "1 1 45%" }}>
                  <TextField
                    fullWidth
                    label="First Name"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    disabled={!editMode}
                    variant="outlined"
                  />
                </Box>

                <Box sx={{ flex: "1 1 45%" }}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    name="lastName"
                    value={formData.lastName}
                    onChange={handleInputChange}
                    disabled={!editMode}
                    variant="outlined"
                  />
                </Box>

                <Box sx={{ flex: "1 1 45%" }}>
                  <TextField
                    fullWidth
                    label="Email Address"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    disabled={!editMode}
                    variant="outlined"
                  />
                </Box>

                <Box sx={{ flex: "1 1 45%" }}>
                  <TextField
                    fullWidth
                    label="Phone Number"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    disabled={!editMode}
                    variant="outlined"
                  />
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

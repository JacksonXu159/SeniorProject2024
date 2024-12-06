import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';

const Navbar = () => {
  const menuItems = ['Home', 'Account', 'Services', 'Settings'];

  return (
    <AppBar position="static" sx={{
          position: "fixed", 
          right: 0,
          zIndex: 1100, 
        }}>
      <Toolbar>
        <Typography variant="h6" component="div" color="primary" sx={{ flexGrow: 1, textAlign: 'left'}}>
          Vanguard
        </Typography>

        <Box>
          {menuItems.map((item) => (
            <Button key={item} color="primary">
              {item}
            </Button>
          ))}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

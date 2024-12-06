import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import { Container } from '@mui/material';

const Navbar = () => {
  const menuItems = ['Home', 'Account', 'Services', 'Settings'];

  return (
    <AppBar position="sticky" sx={{ width: '100%', backgroundColor: 'background.default'}}>
      <Container>
        <Toolbar
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Typography variant="h6" color="primary.main" sx={{ flexGrow: 1, textAlign: 'left' }}>
            Vanguard
          </Typography>

          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
            {menuItems.map((item) => (
              <Button key={item} color="primary">
                {item}
              </Button>
            ))}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Navbar;
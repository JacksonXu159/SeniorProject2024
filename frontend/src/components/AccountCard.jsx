// AccountCard.jsx
import React from 'react';
import { Box, Typography } from '@mui/material';

const AccountCard = ({ account }) => (
  <Box
    sx={{
      backgroundColor: 'background.paper',
      borderRadius: 2,
      padding: 2,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
    }}
  >
    <Typography variant="h6" color="text.primary">
      {account.type}
    </Typography>
    <Typography variant="h4" color="primary.main">
      {account.value || '-'}
    </Typography>
  </Box>
);

export default AccountCard;
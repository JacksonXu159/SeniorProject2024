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
    <Typography variant="body2" color="text.secondary">
      Account number: {account.account}
    </Typography>
    {account.status && (
      <Typography variant="body2" color="text.secondary">
        {account.status}
      </Typography>
    )}
    {account.description && (
      <Typography variant="body2" color="primary.main" sx={{ mt: 1 }}>
        {account.description}
      </Typography>
    )}
  </Box>
);

export default AccountCard;
// Dashboard.jsx
import React from 'react';
import { Box, Typography } from '@mui/material';
import AccountCard from '../components/AccountCard';

const Dashboard = () => {
  const accounts = [
    {
      type: 'Individual',
      value: '$38,558.92',
      account: '47376967',
      status: '',
    },
    {
      type: 'Individual',
      value: '',
      account: '',
      status: '(closed)',
      description: 'View past statements & transactions',
    },
    { type: 'Super', value: '$125,929.09', account: '233360627', status: '' },
    { type: 'Kids (John)', value: '$0.00', account: '57280059', status: '' },
  ];

  return (
    <Box
      sx={{
        margin: '64px',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        flex: 1,
      }}
    >
      <Typography variant="h1" color="primary.main">
        $164,488.01
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
        Combined Portfolio Value
      </Typography>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: 4,
          mt: 4,
          width: '100%',
        }}
      >
        {accounts.map((account) => (
          <AccountCard key={account.account} account={account} />
        ))}
      </Box>
    </Box>
  );
};

export default Dashboard;
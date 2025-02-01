import React from 'react';
import { Box, Typography } from '@mui/material';

const services = [
    { id: 1, title: "Financial Planning", description: "Description for Service 1" },
    { id: 2, title: "Retirement Planning", description: "Description for Service 2" },
    { id: 3, title: "Investment Management", description: "Description for Service 3" },
    { id: 4, title: "Wealth Management", description: "Description for Service 4" },
    { id: 5, title: "Self-Managed", description: "Description for Service 5" },
];

const Services = () => {
  return (
    <Box
        sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            marginTop: '64px',
            padding: '16px',
            width: '100%',
        }}
    >
      <Typography variant="h4" component="h4" sx={{ marginBottom: '10px', fontWeight: 'bold', fontSize: '40px'}}>Our Financial Services</Typography>
      <Typography variant="h6" component="h6" sx={{ marginBottom: '60px'}}>Comprehensive financial solutions tailored to your unique needs</Typography>
        {services.map((service) => (
            <Box
                key={service.id}
                sx={{
                    border: '1px solid #ccc',
                    borderRadius: '8px',
                    padding: '20px',
                    marginBottom: '20px',
                    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                    transition: 'box-shadow 0.3s ease',
                    width: '800px',
                    height: '250px',
                    '&:hover': {
                        boxShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
                    },
                }}
            >
                <Typography variant="h5" component="h3">
                    {service.title}
                </Typography>
                <Typography variant="body1" sx={{ mt: 2 }}>
                    {service.description}
                </Typography>
            </Box>
        ))}
    </Box>
);
};
export default Services
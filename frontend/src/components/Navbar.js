import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import ReceiptIcon from '@mui/icons-material/Receipt';
import ListAltIcon from '@mui/icons-material/ListAlt';

const Navbar = () => {
  return (
    <AppBar 
      position="static" 
      sx={{ 
        background: 'linear-gradient(45deg, rgba(0,255,255,0.9) 0%, rgba(255,0,255,0.9) 100%)',
        mb: 2 
      }}
    >
      <Toolbar>
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 1,
            background: 'linear-gradient(45deg, #121212 30%, #1E1E1E 90%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 'bold'
          }}
        >
          GruntCode Invoice System
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            component={RouterLink}
            to="/"
            startIcon={<ReceiptIcon />}
            sx={{
              color: '#121212',
              '&:hover': {
                color: '#00ff9f',
              }
            }}
          >
            Create Invoice
          </Button>
          <Button
            component={RouterLink}
            to="/invoices"
            startIcon={<ListAltIcon />}
            sx={{
              color: '#121212',
              '&:hover': {
                color: '#00ff9f',
              }
            }}
          >
            Track Invoices
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

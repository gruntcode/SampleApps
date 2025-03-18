import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  Paper,
  Button,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import PaidIcon from '@mui/icons-material/AttachMoney';
import { Link as RouterLink } from 'react-router-dom';
import axios from 'axios';

const InvoiceList = () => {
  const [invoices, setInvoices] = useState([]);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/invoices');
      setInvoices(response.data);
    } catch (error) {
      console.error('Error fetching invoices:', error);
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await axios.put(`http://localhost:5000/api/invoice/${id}/status`, {
        status: newStatus
      });
      fetchInvoices();
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const markAsPaid = async (id) => {
    try {
      await axios.put(`http://localhost:5000/api/invoice/${id}/paid`, {
        status: 'paid'
      });
      fetchInvoices();
    } catch (error) {
      console.error('Error marking invoice as paid:', error);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: '#FFD700',
      paid: '#00ff9f',
      overdue: '#ff00ff',
      cancelled: '#ff0000'
    };
    return colors[status] || colors.pending;
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h1" sx={{ fontSize: '2.5rem' }}>
          Invoice Tracker
        </Typography>
        <Button
          component={RouterLink}
          to="/"
          startIcon={<HomeIcon />}
          sx={{
            color: 'primary.main',
            '&:hover': {
              color: 'secondary.main',
            }
          }}
        >
          Back to Home
        </Button>
      </Box>
      
      <Card>
        <CardContent>
          <TableContainer component={Paper} sx={{ bgcolor: 'background.paper' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Invoice #</TableCell>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Client</TableCell>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Amount</TableCell>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Date</TableCell>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {invoices.map((invoice) => (
                  <TableRow 
                    key={invoice.id}
                    sx={{
                      '&:hover': {
                        bgcolor: 'rgba(0, 255, 255, 0.05)',
                      }
                    }}
                  >
                    <TableCell>{invoice.invoice_number}</TableCell>
                    <TableCell>{invoice.client_name}</TableCell>
                    <TableCell>${invoice.amount.toFixed(2)}</TableCell>
                    <TableCell>{invoice.date_created}</TableCell>
                    <TableCell>
                      <Select
                        value={invoice.status}
                        onChange={(e) => handleStatusChange(invoice.id, e.target.value)}
                        size="small"
                        sx={{
                          color: getStatusColor(invoice.status),
                          '& .MuiSelect-icon': {
                            color: getStatusColor(invoice.status)
                          }
                        }}
                      >
                        <MenuItem value="pending">Pending</MenuItem>
                        <MenuItem value="paid">Paid</MenuItem>
                        <MenuItem value="overdue">Overdue</MenuItem>
                        <MenuItem value="cancelled">Cancelled</MenuItem>
                      </Select>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<PaidIcon />}
                        onClick={() => markAsPaid(invoice.id)}
                        sx={{
                          bgcolor: '#00ff9f',
                          color: '#121212',
                          '&:hover': {
                            bgcolor: '#00cc7d',
                          }
                        }}
                      >
                        Mark as Paid
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default InvoiceList;

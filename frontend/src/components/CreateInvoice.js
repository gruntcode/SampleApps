import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import HomeIcon from '@mui/icons-material/Home';
import { Link as RouterLink } from 'react-router-dom';
import axios from 'axios';

const CreateInvoice = () => {
  const [formData, setFormData] = useState({
    client_name: '',
    client_email: '',
    items: [],
  });
  const [newItem, setNewItem] = useState({ description: '', amount: '' });
  const [logo, setLogo] = useState(null);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleItemChange = (e) => {
    setNewItem({ ...newItem, [e.target.name]: e.target.value });
  };

  const addItem = () => {
    if (newItem.description && newItem.amount) {
      setFormData({
        ...formData,
        items: [...formData.items, { ...newItem, amount: parseFloat(newItem.amount) }],
      });
      setNewItem({ description: '', amount: '' });
    }
  };

  const removeItem = (index) => {
    const updatedItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: updatedItems });
  };

  const handleLogoChange = (e) => {
    const file = e.target.files[0];
    setLogo(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const totalAmount = formData.items.reduce((sum, item) => sum + item.amount, 0);
      const response = await axios.post('http://localhost:5000/api/invoice', {
        ...formData,
        amount: totalAmount,
      });
      alert('Invoice created and sent successfully!');
      setFormData({ client_name: '', client_email: '', items: [] });
    } catch (error) {
      alert('Error creating invoice: ' + error.message);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h1" sx={{ fontSize: '2.5rem' }}>
          Create Invoice
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
          <Box component="form" onSubmit={handleSubmit}>
            <Box sx={{ mb: 3 }}>
              <input
                accept="image/*"
                style={{ display: 'none' }}
                id="logo-upload"
                type="file"
                onChange={handleLogoChange}
              />
              <label htmlFor="logo-upload">
                <Button
                  variant="outlined"
                  component="span"
                  fullWidth
                  sx={{
                    borderColor: 'secondary.main',
                    color: 'secondary.main',
                    '&:hover': {
                      borderColor: 'primary.main',
                      color: 'primary.main',
                    }
                  }}
                >
                  Upload Logo
                </Button>
              </label>
              {logo && (
                <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
                  Logo uploaded: {logo.name}
                </Typography>
              )}
            </Box>

            <TextField
              fullWidth
              label="Client Name"
              name="client_name"
              value={formData.client_name}
              onChange={handleInputChange}
              sx={{ mb: 2 }}
              required
            />

            <TextField
              fullWidth
              label="Client Email"
              name="client_email"
              type="email"
              value={formData.client_email}
              onChange={handleInputChange}
              sx={{ mb: 3 }}
              required
            />

            <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>
              Invoice Items
            </Typography>

            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <TextField
                label="Description"
                name="description"
                value={newItem.description}
                onChange={handleItemChange}
                sx={{ flex: 2 }}
              />
              <TextField
                label="Amount"
                name="amount"
                type="number"
                value={newItem.amount}
                onChange={handleItemChange}
                sx={{ flex: 1 }}
              />
              <IconButton
                onClick={addItem}
                sx={{
                  color: 'success.main',
                  '&:hover': { color: 'primary.main' }
                }}
              >
                <AddIcon />
              </IconButton>
            </Box>

            <List>
              {formData.items.map((item, index) => (
                <ListItem
                  key={index}
                  sx={{
                    bgcolor: 'background.paper',
                    borderRadius: 1,
                    mb: 1,
                  }}
                >
                  <ListItemText
                    primary={item.description}
                    secondary={`$${item.amount.toFixed(2)}`}
                  />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      onClick={() => removeItem(index)}
                      sx={{ color: 'secondary.main' }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>

            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Total: ${formData.items.reduce((sum, item) => sum + item.amount, 0).toFixed(2)}
              </Typography>
              <Button
                type="submit"
                variant="contained"
                fullWidth
                sx={{
                  background: 'linear-gradient(45deg, #00ffff 30%, #ff00ff 90%)',
                  color: 'background.paper',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #ff00ff 30%, #00ffff 90%)',
                  }
                }}
              >
                Generate & Send Invoice
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CreateInvoice;

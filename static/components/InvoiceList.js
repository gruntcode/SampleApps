// Get Material-UI components
const {
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
} = window.MaterialUI;

function InvoiceList() {
  const [invoices, setInvoices] = React.useState([]);

  React.useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      const response = await axios.get('/api/invoices');
      setInvoices(response.data);
    } catch (error) {
      console.error('Error fetching invoices:', error);
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      await axios.put(`/api/invoice/${id}/status`, {
        status: newStatus
      });
      fetchInvoices();
    } catch (error) {
      console.error('Error updating status:', error);
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
      <Typography variant="h4" sx={{ 
        mb: 4, 
        textAlign: 'center',
        background: 'linear-gradient(45deg, #00ffff 30%, #ff00ff 90%)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
      }}>
        Invoice Tracker
      </Typography>
      
      <Card sx={{ bgcolor: 'background.paper' }}>
        <CardContent>
          <TableContainer component={Paper} sx={{ bgcolor: 'background.default' }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Invoice #</TableCell>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Client</TableCell>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Amount</TableCell>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Date</TableCell>
                  <TableCell sx={{ color: 'primary.main', fontWeight: 'bold' }}>Status</TableCell>
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
                    <TableCell sx={{ color: 'text.primary' }}>{invoice.invoice_number}</TableCell>
                    <TableCell sx={{ color: 'text.primary' }}>{invoice.client_name}</TableCell>
                    <TableCell sx={{ color: 'text.primary' }}>${invoice.amount.toFixed(2)}</TableCell>
                    <TableCell sx={{ color: 'text.primary' }}>{invoice.date_created}</TableCell>
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
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}

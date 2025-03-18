// Get Material-UI components
const { AppBar, Toolbar, Typography, Button, Box } = MaterialUI;
const { Link } = ReactRouterDOM;

function Navbar() {
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
            component={Link}
            to="/"
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
            component={Link}
            to="/invoices"
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
}

const { Box } = window.MaterialUI;
const { BrowserRouter, Routes, Route } = window.ReactRouterDOM;

const theme = window.MaterialUI.createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00ffff', // Cyan
    },
    secondary: {
      main: '#ff00ff', // Pink
    },
    success: {
      main: '#00ff9f', // Neon Green
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
    text: {
      primary: '#ffffff',
      secondary: '#00ff9f',
    }
  }
});

function App() {
  return (
    <window.MaterialUI.ThemeProvider theme={theme}>
      <window.MaterialUI.CssBaseline />
      <BrowserRouter>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', bgcolor: '#121212' }}>
          <Navbar />
          <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
            <Routes>
              <Route path="/" element={<CreateInvoice />} />
              <Route path="/invoices" element={<InvoiceList />} />
            </Routes>
          </Box>
        </Box>
      </BrowserRouter>
    </window.MaterialUI.ThemeProvider>
  );
}

const root = window.ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <window.React.StrictMode>
    <App />
  </window.React.StrictMode>
);

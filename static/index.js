// Get Material-UI components
const { createRoot } = ReactDOM;
const { createTheme, ThemeProvider, CssBaseline } = MaterialUI;

// Define the theme
const theme = createTheme({
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
  },
});

// Create root and render app
const container = document.getElementById('root');
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);

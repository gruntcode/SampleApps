import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00ffff', // Cyan from logo
    },
    secondary: {
      main: '#ff00ff', // Pink from logo
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
    success: {
      main: '#00ff9f', // Neon green
    },
    text: {
      primary: '#ffffff',
      secondary: '#00ff9f', // Neon green for accents
    },
    accent: {
      purple: '#9c27b0', // Purple from logo
    }
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      background: 'linear-gradient(45deg, #00ffff 30%, #ff00ff 90%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          backgroundImage: 'linear-gradient(45deg, rgba(0,255,255,0.05) 0%, rgba(255,0,255,0.05) 100%)',
        },
      },
    },
  },
});

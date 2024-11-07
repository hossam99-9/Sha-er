// theme.ts
import { createTheme, ThemeOptions } from '@mui/material/styles';
import { red } from '@mui/material/colors';

// Define theme options for both light and dark modes
const getThemeOptions = (mode: 'light' | 'dark'): ThemeOptions => ({
  direction: 'rtl',
  palette: {
    mode,
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#B4B4B4',
    },
    error: {
      main: red.A400,
    },
    background: {
      default: mode === 'light' ? '#f4f6f8' : '#212121',
      paper: mode === 'light' ? '#ffffff' : '#1e1e1e',
    },
    text: {
      primary: mode === 'light' ? '#000000' : '#ffffff',
      secondary: mode === 'light' ? '#666666' : '#b3b3b3',
    },
  },
  typography: {
    fontFamily: "'Inter', 'Amiri', sans-serif",
    h1: {
      fontSize: '2.5rem',
      fontStyle: 'italic',
    },
    h2: {
      fontSize: '2rem',
      fontStyle: 'italic',
    },
    h3: {
      fontSize: '1.25rem',
      fontStyle: 'italic',
    },
    body1: {
      fontStyle: 'italic',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '0',
          textTransform: 'none',
          fontStyle: 'italic',
        },
        endIcon: {
          marginRight: '8px',
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          '&:hover': {
            backgroundColor: 'transparent',
          },
        },
      },
    },
    MuiList: {
      styleOverrides: {
        root: {
          padding: 0,
          display: 'flex',
          flexDirection: 'column',
        },
        padding: {
          gap: '16px',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          marginBottom: '16px',
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          paddingRight: 0,
          minWidth: '35px',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          '&.Mui-selected': {
            backgroundColor: mode === 'light' ? '#ffffff3b' : '#ffffff1f',
            fontWeight: 'bold',
            '& .MuiListItemText-root': {
              '& span': {
                fontWeight: 'bold',
              },
            },
            '&:hover': {
              backgroundColor: mode === 'light' ? '#ffffff3b' : '#ffffff1f',
            },
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: mode === 'light' ? '#333' : '#1e1e1e',
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: '0 20px 20px 0',
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: mode === 'light' ? '#656565' : '#888888',
          },
          // '&:focus .MuiOutlinedInput-notchedOutline': {
          //   borderColor: mode === 'light' ? '#656565' : '#888888',
          // },
        },
        notchedOutline: {
          borderColor: mode === 'light' ? '#ECECEC' : '#404040',
        },
      },
    },
  },
});

// Create and export the theme creator function
export const createAppTheme = (mode: 'light' | 'dark') => {
  return createTheme(getThemeOptions(mode));
};

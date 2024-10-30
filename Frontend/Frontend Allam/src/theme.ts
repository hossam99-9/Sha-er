// theme.ts
import { createTheme } from '@mui/material/styles';
import { red } from '@mui/material/colors';

const theme = createTheme({
  direction: 'rtl',
  palette: {
    primary: {
      main: '#1976d2', // Customize the primary color
    },
    secondary: {
      main: '#B4B4B4', // Customize the secondary color
    },
    error: {
      main: red.A400, // Customize error color
    },
    background: {
      default: '#f4f6f8', // Default background color
    },
  },
  typography: {
    fontFamily: "'Inter', 'Amiri', sans-serif",
    h1: {
      fontSize: '2.5rem',
      fontStyle: 'italic', // Apply italic to h1
    },
    h2: {
      fontSize: '2rem',
      fontStyle: 'italic', // Apply italic to h2
    },
    h3: {
      fontSize: '1.25rem',
      fontStyle: 'italic', // Apply italic to h3
    },
    body1: {
      fontStyle: 'italic', // Apply italic to body text
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '0', // Customize button border radius
          textTransform: 'none', // Disable uppercase text for buttons
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
            backgroundColor: 'transparent', // Disable hover effect by making background transparent
          },
        },
      },
    },
    MuiList: {
      styleOverrides: {
        root: {
          padding: 0, // Removes default padding
          display: 'flex',
          flexDirection: 'column',
        },
        padding: {
          gap: '16px', // Add gap between the list items
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          marginBottom: '16px', // Apply margin between the list items
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          paddingRight: 0, // Remove right padding
          minWidth: '35px', // Adjust the width
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          '&.Mui-selected': {
            backgroundColor: '#ffffff3b', // Change the background color when selected
            fontWeight: 'bold', // Change the font weight when selected
            '& .MuiListItemText-root': {
              '& span': {
                fontWeight: 'bold', // Apply bold to the ListItemText when selected
              },
            },
            '&:hover': {
              backgroundColor: '#ffffff3b', // Keep the same background on hover when selected
            },
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#333', // Customize AppBar background color
        },
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: '0 20px 20px 0', // Custom border radius for the TextField component
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#656565', // Hover effect for the outlined variant
          },
        },
        notchedOutline: {
          borderColor: '#ECECEC', // Default border color for outlined variant
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {},
      },
    },
  },
});

export default theme;

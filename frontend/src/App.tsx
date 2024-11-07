import React from 'react';
import './App.css';

import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';
import ChatLayout from './components/ChatLayout';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './ThemeContext';
import 'react-toastify/dist/ReactToastify.css';

// Initializes a new instance of QueryClient for managing server state
const queryClient = new QueryClient();

/**
 * App component
 * The root component for the application, providing global contexts for theme, server state, and notifications.
 */
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      {/* Provides server state management for API calls */}
      <ThemeProvider>
        {/* Applies theme and resets CSS to match Material-UI styling */}
        <CssBaseline />
        <Box dir="rtl" lang="ar">
          {/* Chat layout with RTL direction for Arabic support */}
          <ChatLayout />
        </Box>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;

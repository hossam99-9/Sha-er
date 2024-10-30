import React from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box } from '@mui/material';
import ChatLayout from './components/ChatLayout';
import theme from './theme';
import { Provider } from 'react-redux'; // Import Redux Provider
import { store } from './store'; // Import the configured store
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Provider store={store}>
        {/* Wrap with Provider */}
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Box dir="rtl" lang="ar">
            <Router>
              <Routes>
                <Route path="/" element={<ChatLayout />} />
                <Route path="/category1" element={<ChatLayout />} />
                <Route path="/category2" element={<ChatLayout />} />
                <Route path="/category3" element={<ChatLayout />} />
              </Routes>
            </Router>
          </Box>
        </ThemeProvider>
      </Provider>
    </QueryClientProvider>
  );
}

export default App;

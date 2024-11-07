// ThemeContext.tsx
import React, { createContext, useContext, useState, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { createAppTheme } from './theme';

/**
 * Gets the initial theme mode based on the user's system preference.
 *
 * @returns 'light' if the system preference is light or no matchMedia support; 'dark' otherwise.
 */
const getInitialMode = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }
  return 'light';
};

/**
 * Type definition for the ThemeContext
 */
interface ThemeContextType {
  mode: 'light' | 'dark'; // Current theme mode, either 'light' or 'dark'
  toggleColorMode: () => void; // Function to toggle between light and dark modes
}

// Creates a context with a default mode of 'light' and an empty toggle function
const ThemeContext = createContext<ThemeContextType>({
  mode: 'light',
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  toggleColorMode: () => {},
});

/**
 * Custom hook to access the theme context.
 *
 * @returns The current theme mode and a function to toggle between light and dark modes.
 */
export const useThemeContext = () => useContext(ThemeContext);

/**
 * ThemeProvider component
 * Wraps the application in a theme context, providing a color mode toggle.
 *
 * @param children - The child components to be wrapped by the ThemeProvider.
 */
export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  // State to store the current theme mode, initialized to the user's preference
  const [mode, setMode] = useState<'light' | 'dark'>(getInitialMode());

  /**
   * Memoized color mode object with the current mode and a toggle function.
   */
  const colorMode = useMemo(
    () => ({
      mode,
      toggleColorMode: () => {
        setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
      },
    }),
    [mode]
  );

  // Memoized theme created based on the current mode
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  return (
    <ThemeContext.Provider value={colorMode}>
      {/* Provides the theme to Material-UI components */}
      <MuiThemeProvider theme={theme}>{children}</MuiThemeProvider>
    </ThemeContext.Provider>
  );
};

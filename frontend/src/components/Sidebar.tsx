import React, { useState } from 'react';
import {
  Box,
  List,
  ListItemButton,
  ListItemText,
  ListItemIcon,
  IconButton,
  Button,
  Drawer as MuiDrawer,
  styled,
  useTheme,
  Divider,
} from '@mui/material';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import AddIcon from '@mui/icons-material/Add';

import Logo from '../assets/logos/logo.svg';
import WhiteLogo from '../assets/logos/logo-white.svg';
import BsLogo from '../assets/logos/brightskies-logo.svg';
import WhiteAllamLogo from '../assets/logos/white-allam-logo.svg';
import SdaiaLogo from '../assets/logos/sdaia-logo.svg';
import WhiteBsLogo from '../assets/logos/white-brightskies-logo.svg';
import AllamLogo from '../assets/logos/allam-logo.png';
import WhiteSdaiaLogo from '../assets/logos/white-sdaia-logo.svg';

import { useThemeContext } from '../ThemeContext';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import SimulationIcon from '../assets/icons/simulationIcon';
import FeatherIcon from '../assets/icons/featherIcon';
import BattleIcon from '../assets/icons/battleIcon';
import AnalysisIcon from '../assets/icons/analysisIcon';
import { ChatCategory } from '../types/chat';

interface SidebarProps {
  selectedCategory: number; // The index of the currently selected chat category
  onCategorySelect: (category: ChatCategory) => void; // Function to handle category selection changes
  clearMessages: () => void; // Function to clear messages
}

const drawerWidth = 300; // Width of the sidebar when expanded

/**
 * Custom-styled Material-UI Drawer component for the sidebar.
 */
const Drawer = styled(MuiDrawer)(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  whiteSpace: 'nowrap',
  boxSizing: 'border-box',
  '& .MuiDrawer-paper': {
    width: drawerWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
    overflowX: 'hidden',
  },
}));

/**
 * Sidebar component used for navigating between chat categories,
 * clearing messages, and toggling between light and dark mode.
 *
 * @param selectedCategory - Currently selected chat category index.
 * @param onCategorySelect - Callback function to select a different chat category.
 * @param clearMessages - Callback function to clear messages in the selected chat category.
 */
const Sidebar: React.FC<SidebarProps> = ({
  selectedCategory,
  onCategorySelect,
  clearMessages,
}) => {
  const theme = useTheme();
  const [open, setOpen] = useState(false); // State to control drawer open/close
  const { mode, toggleColorMode } = useThemeContext(); // Theme mode and toggle function from ThemeContext

  /**
   * Opens the sidebar drawer.
   */
  const handleDrawerOpen = () => {
    setOpen(true);
  };

  /**
   * Closes the sidebar drawer.
   */
  const handleDrawerClose = () => {
    setOpen(false);
  };

  /**
   * Custom-styled header for the drawer, includes background gradient based on theme.
   */
  const DrawerHeader = styled('div')(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: theme.spacing(0, 1),
    backgroundColor: theme.palette.background.default,
    backgroundImage:
      mode === 'light'
        ? 'linear-gradient(to right, #f3ecde54, #98a7ad)'
        : 'linear-gradient(to right, #5e5e5e, #383838)',
    ...theme.mixins.toolbar,
  }));

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Main content container */}
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <DrawerHeader />
        {/* Main content goes here */}
      </Box>

      <Drawer
        anchor="right" // Positions the drawer on the right
        variant="permanent"
        sx={{
          width: open ? '235px' : `fit-content`,
          '& .MuiDrawer-paper': {
            width: open ? drawerWidth : `75px`,
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          },
        }}
      >
        {/* Drawer Header with Logo and Expand/Collapse Icon */}
        <DrawerHeader>
          {open && (
            <img
              src={mode === 'light' ? Logo : WhiteLogo}
              alt="Logo"
              style={{ width: '120px', height: 'auto' }}
            />
          )}
          <IconButton onClick={open ? handleDrawerClose : handleDrawerOpen}>
            {!open && <FeatherIcon />}
            {open ? <ChevronRightIcon /> : <ChevronLeftIcon />}
          </IconButton>
        </DrawerHeader>

        {/* Sidebar content */}
        <Box
          p={2}
          sx={{
            backgroundColor: theme.palette.background.default,
            backgroundImage:
              mode === 'light'
                ? 'linear-gradient(to right, #f3ecde54, #98a7ad)'
                : 'linear-gradient(to right, #5e5e5e, #383838)',
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          }}
        >
          <Box display="flex" flexDirection="column" gap={theme.spacing(5)}>
            {/* Clear messages button */}
            <Button
              variant="contained"
              color="primary"
              endIcon={<AddIcon />}
              onClick={clearMessages}
              sx={{
                marginY: theme.spacing(3),
                borderRadius: '12px',
                backgroundColor: '#242220',
                padding: theme.spacing(2),
                width: open ? 'fit-content' : '80%',
                alignSelf: 'center',
              }}
            >
              {open ? 'ابدأ محادثة جديدة' : ''}
            </Button>

            {/* Category List with icons and labels */}
            <List>
              <ListItemButton
                selected={selectedCategory === 0}
                onClick={() => onCategorySelect(0)}
                sx={{
                  justifyContent: open ? 'initial' : 'center',
                  px: open ? 2.5 : 0,
                  width: open ? '85%' : '100%',
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    justifyContent: 'center',
                    mr: '0',
                    ml: open ? theme.spacing(3) : '0',
                  }}
                >
                  <Box sx={{ margin: '0 8px 0 8px' }}>
                    <AnalysisIcon />
                  </Box>
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary="نقد وتحليل" // Analysis category label
                    primaryTypographyProps={{
                      style: {
                        textAlign: 'right',
                        fontSize: theme.typography.h3.fontSize,
                      },
                    }}
                  />
                )}
              </ListItemButton>

              <ListItemButton
                selected={selectedCategory === 1}
                onClick={() => onCategorySelect(1)}
                sx={{
                  justifyContent: open ? 'initial' : 'center',
                  px: open ? 2.5 : 0,
                  width: open ? '85%' : '100%',
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: '48px',
                    justifyContent: 'flex-start',
                    mr: '0',
                    ml: open ? theme.spacing(3) : '0',
                  }}
                >
                  <SimulationIcon />
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary="محاكاة الشاعر" // Simulation category label
                    primaryTypographyProps={{
                      style: {
                        textAlign: 'right',
                        fontSize: theme.typography.h3.fontSize,
                      },
                    }}
                  />
                )}
              </ListItemButton>

              <ListItemButton
                selected={selectedCategory === 2}
                onClick={() => onCategorySelect(2)}
                sx={{
                  justifyContent: open ? 'initial' : 'center',
                  px: open ? 2.5 : 0,
                  width: open ? '85%' : '100%',
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: '24px',
                    justifyContent: 'flex-start',
                    mr: '0',
                    ml: open ? theme.spacing(3) : '0',
                  }}
                >
                  <Box sx={{ margin: '0 8px 0 8px' }}>
                    <BattleIcon />
                  </Box>
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary="مبارزة شعرية" // Battle category label
                    primaryTypographyProps={{
                      style: {
                        textAlign: 'right',
                        fontSize: theme.typography.h3.fontSize,
                      },
                    }}
                  />
                )}
              </ListItemButton>
            </List>
          </Box>

          {/* Bottom section with logos and theme toggle button */}
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            mt={theme.spacing(2)}
          >
            <img
              src={mode === 'light' ? BsLogo : WhiteBsLogo}
              alt="brightskies logo"
              style={{
                display: open ? 'block' : 'none',
                width: '45%',
                height: 'auto',
                marginBottom: mode === 'light' ? 0 : theme.spacing(2),
              }}
            />
            <img
              src={mode === 'light' ? AllamLogo : WhiteAllamLogo}
              alt="allam logo"
              style={{
                display: open ? 'block' : 'none',
                width: mode === 'light' ? '80%' : '45%',
                height: 'auto',
                marginBottom: mode === 'light' ? 0 : theme.spacing(2),
              }}
            />
            <img
              src={mode === 'light' ? SdaiaLogo : WhiteSdaiaLogo}
              alt="sdaia logo"
              style={{
                display: open ? 'block' : 'none',
                width: '45%',
                height: 'auto',
                marginBottom: theme.spacing(2),
              }}
            />
            <Divider
              sx={{
                border: 'solid 1px #aeb1b312',
                width: '100%',
                marginY: '10px',
              }}
            />
            <IconButton onClick={toggleColorMode} color="inherit">
              {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Box>
        </Box>
      </Drawer>
    </Box>
  );
};

export default Sidebar;

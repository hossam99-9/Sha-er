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
} from '@mui/material';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import AddIcon from '@mui/icons-material/Add';

// Import your logos and icons
import Logo from '../assets/logos/logo.svg';
import BsLogo from '../assets/logos/brightskies-logo.svg';
import AllamLogo from '../assets/logos/allam-logo.svg';
import SdaiaLogo from '../assets/logos/sdaia-logo.svg';
import AnalysisIcon from '../assets/icons/analysis-icon.svg';
import BattleIcon from '../assets/icons/battle-icon.svg';
import SimulationIcon from '../assets/icons/simulation-icon.svg';
import FeatherIcon from '../assets/icons/feather-icon.svg';
// Define SidebarProps interface
interface SidebarProps {
  selectedCategory: number;
  onCategorySelect: (category: number) => void; // Ensure this is the correct type
  clearMessages: () => void;
}
const drawerWidth = 300;

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

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',

  padding: theme.spacing(0, 1),
  backgroundColor: theme.palette.background.default, // Same background as sidebar
  backgroundImage: 'linear-gradient(to right, #f3ecde54, #98a7ad)', // Gradient same as sidebar
  ...theme.mixins.toolbar,
}));

const Sidebar: React.FC<SidebarProps> = ({
  selectedCategory,
  onCategorySelect,
  clearMessages,
}) => {
  const theme = useTheme();
  const [open, setOpen] = useState(false);

  const handleDrawerOpen = () => {
    setOpen(true);
  };

  const handleDrawerClose = () => {
    setOpen(false);
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <DrawerHeader />
        {/* Main content goes here */}
      </Box>

      <Drawer
        anchor="right" // Move drawer to the right
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
        {/* Drawer Header with Logo and Collapse/Expand Icon */}
        <DrawerHeader>
          {open && (
            <img
              src={Logo}
              alt="Logo"
              style={{ width: '120px', height: 'auto' }}
            />
          )}
          <IconButton onClick={open ? handleDrawerClose : handleDrawerOpen}>
            {!open && (
              <>
                <img
                  src={FeatherIcon}
                  alt="Feather Icon"
                  style={{ width: '32px', height: '32px' }}
                />{' '}
              </>
            )}
            {open ? <ChevronRightIcon /> : <ChevronLeftIcon />}
          </IconButton>
        </DrawerHeader>

        {/* Sidebar content */}
        <Box
          p={2}
          sx={{
            backgroundColor: theme.palette.background.default,
            backgroundImage: 'linear-gradient(to right, #f3ecde54, #98a7ad)',
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            borderRadius: '0', // Rounded on the left for right-side drawer
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

            {/* Category List */}
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
                  <img
                    src={AnalysisIcon}
                    alt="Analysis Icon"
                    style={{
                      width: '32px',
                      height: '32px',
                      margin: '0 8px 0 8px',
                    }}
                  />
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary="نقد وتحليل"
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
                  <img
                    src={SimulationIcon}
                    alt="Simulation Icon"
                    style={{ width: '48px', height: '48px' }}
                  />
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary="محاكاة الشاعر"
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
                  <img
                    src={BattleIcon}
                    alt="Battle Icon"
                    style={{
                      width: '32px',
                      height: '32px',
                      margin: '0 8px 0 8px',
                    }}
                  />
                </ListItemIcon>
                {open && (
                  <ListItemText
                    primary="مبارزة شعرية"
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

          {/* Bottom Logos */}
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            mt={theme.spacing(2)}
          >
            <img
              src={BsLogo}
              alt="brightskies logo"
              style={{
                display: open ? 'block' : 'none',
                width: '45%',
                height: 'auto',
                marginBottom: theme.spacing(2),
              }}
            />
            <img
              src={AllamLogo}
              alt="allam logo"
              style={{
                display: open ? 'block' : 'none',
                width: '45%',
                height: 'auto',
                marginBottom: theme.spacing(2),
              }}
            />
            <img
              src={SdaiaLogo}
              alt="sdaia logo"
              style={{
                display: open ? 'block' : 'none',
                width: '45%',
                height: 'auto',
                marginBottom: theme.spacing(2),
              }}
            />
          </Box>
        </Box>
      </Drawer>
    </Box>
  );
};

export default Sidebar;

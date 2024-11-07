import React, { useState, useEffect, useMemo } from 'react';
import { Box, TextField, Button, Select, MenuItem } from '@mui/material';
import { POETS, TOPICS } from '../constants/constants';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';

/**
 * Props for the InputArea component.
 */
interface InputAreaProps {
  selectedCategory: number; // Index of the currently selected category (0, 1, or 2)
  onSendMessage: (
    message:
      | { text: string; sender: 'user' }
      | { text: string; prompt: string; poet1: string; sender: 'user' }
      | {
          text: string;
          poet1: string;
          poet2: string;
          topics: string[];
          sender: 'user';
        }
  ) => void; // Function to handle sending messages
  isLoading: boolean; // Indicates if a message is currently being sent
}

const poets = POETS; // List of poets from constants
const topics = TOPICS; // List of topics from constants

/**
 * InputArea component
 * Provides a user interface for inputting messages, selecting poets and topics based on the selected chat category.
 *
 * @param selectedCategory - Currently selected category for chat.
 * @param onSendMessage - Callback function to send the constructed message.
 * @param isLoading - Indicates if a message is in progress.
 */
const InputArea: React.FC<InputAreaProps> = ({
  selectedCategory,
  onSendMessage,
}) => {
  // Initial state for input fields based on category
  const initialInputState = useMemo(
    () => ({
      input: '', // Main text input
      dropdown1: '', // First dropdown selection (e.g., poet1)
      dropdown2: '', // Second dropdown selection (e.g., poet2)
      dropdown3: [] as string[], // Array to support multiple selections in category 2
    }),
    []
  );
  const [inputState, setInputState] = useState<
    Record<number, typeof initialInputState>
  >({
    0: initialInputState,
    1: initialInputState,
    2: initialInputState,
  });

  useEffect(() => {
    // Resets input state when category changes
    setInputState((prev) => ({
      ...prev,
      [selectedCategory]: initialInputState,
    }));
  }, [initialInputState, selectedCategory]);

  /**
   * Updates the main input field value.
   */
  const handleInputChange = (value: string) => {
    setInputState((prev) => ({
      ...prev,
      [selectedCategory]: { ...prev[selectedCategory], input: value },
    }));
  };

  /**
   * Updates the dropdown selections based on the dropdown index.
   */
  const handleDropdownChange = (
    dropdownIndex: number,
    value: string | string[]
  ) => {
    const dropdownKey =
      `dropdown${dropdownIndex}` as keyof typeof initialInputState;
    setInputState((prev) => ({
      ...prev,
      [selectedCategory]: { ...prev[selectedCategory], [dropdownKey]: value },
    }));
  };

  /**
   * Constructs and sends the message based on the selected category.
   */
  const handleSendMessage = () => {
    const { input, dropdown1, dropdown2, dropdown3 } =
      inputState[selectedCategory];

    if (selectedCategory === 0) {
      onSendMessage({
        text: input,
        sender: 'user',
      });
    } else if (selectedCategory === 1) {
      onSendMessage({
        text: `الموضوع:  ${input}
الشاعر:  ${dropdown1}`,
        prompt: input,
        poet1: dropdown1,
        sender: 'user',
      });
    } else if (selectedCategory === 2) {
      onSendMessage({
        text: `الشاعر الأول:  ${dropdown1}
الشاعر الثاني:  ${dropdown2}
الموضوع:  ${dropdown3.join(', ')}`,
        poet1: dropdown1,
        poet2: dropdown2,
        topics: dropdown3,
        sender: 'user',
      });
    }

    setInputState((prev) => ({
      ...prev,
      [selectedCategory]: {
        ...prev[selectedCategory],
        input: '',
        dropdown1: '',
        dropdown2: '',
        dropdown3: [],
      },
    }));
  };

  /**
   * Handles the 'Enter' key press to send the message.
   */
  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isSendDisabled()) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  /**
   * Determines if the send button should be disabled.
   * Checks if required fields are filled based on the selected category.
   */
  const isSendDisabled = () => {
    if (selectedCategory === 2) {
      const { dropdown1, dropdown2, dropdown3 } = inputState[selectedCategory];
      return !(dropdown1 && dropdown2 && dropdown3.length > 0);
    }
    if (selectedCategory === 1) {
      const { dropdown1, input } = inputState[selectedCategory];
      return !(dropdown1 && input.trim());
    }
    return !inputState[selectedCategory].input?.trim();
  };

  return (
    <Box mt={2} display="flex" flexDirection="column" sx={{ width: '100%' }}>
      {/* Category 0 - Analysis */}
      {selectedCategory === 0 && (
        <Box display="flex" alignItems="center">
          <TextField
            value={inputState[selectedCategory].input}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyDown={handleKeyPress}
            label="أدخل بيت الشعر الذي تريد نقده وتحليله"
            variant="outlined"
            fullWidth
            multiline
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSendMessage}
            disabled={isSendDisabled()}
            sx={{
              borderRadius: '20px 0 0 20px',
              height: '100%',
              padding: '16px',
            }}
          >
            <ArrowUpwardIcon />
          </Button>
        </Box>
      )}

      {/* Category 1 - Simulation */}
      {selectedCategory === 1 && (
        <Box display="flex" alignItems="center">
          <Select
            value={inputState[selectedCategory].dropdown1}
            onChange={(e) => handleDropdownChange(1, e.target.value as string)}
            displayEmpty
            sx={{ width: '25%' }}
          >
            <MenuItem value="">
              <em>اختر الشاعر</em>
            </MenuItem>
            {poets.map((poet) => (
              <MenuItem key={poet} value={poet}>
                {poet}
              </MenuItem>
            ))}
          </Select>
          <TextField
            value={inputState[selectedCategory].input}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyDown={handleKeyPress}
            label="أدخل الموضوع"
            placeholder="بيت شعر ينتهي بقافية الميم"
            variant="outlined"
            fullWidth
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '0',
              },
            }}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSendMessage}
            disabled={isSendDisabled()}
            sx={{
              borderRadius: '20px 0 0 20px',
              height: '100%',
              padding: '16px',
            }}
          >
            <ArrowUpwardIcon />
          </Button>
        </Box>
      )}

      {/* Category 2 - Battle */}
      {selectedCategory === 2 && (
        <Box display="flex" alignItems="center" gap="0">
          <Select
            value={inputState[selectedCategory].dropdown1}
            onChange={(e) => handleDropdownChange(1, e.target.value as string)}
            displayEmpty
            sx={{ width: '33%' }}
          >
            <MenuItem value="">
              <em>اختر الشاعر الأول</em>
            </MenuItem>
            {poets.map((poet) => (
              <MenuItem key={poet} value={poet}>
                {poet}
              </MenuItem>
            ))}
          </Select>
          <Select
            value={inputState[selectedCategory].dropdown2}
            onChange={(e) => handleDropdownChange(2, e.target.value as string)}
            displayEmpty
            sx={{ width: '33%', borderRadius: '0' }}
          >
            <MenuItem value="">
              <em>اختر الشاعر الثاني</em>
            </MenuItem>
            {poets.map((poet) => (
              <MenuItem key={poet} value={poet}>
                {poet}
              </MenuItem>
            ))}
          </Select>
          <Select
            multiple
            value={inputState[selectedCategory].dropdown3}
            onChange={(e) =>
              handleDropdownChange(3, e.target.value as string[])
            }
            displayEmpty
            renderValue={(selected) =>
              selected.length ? selected.join(', ') : 'اختر الموضوع'
            }
            sx={{ width: '33%', borderRadius: '0' }}
          >
            <MenuItem disabled value="">
              <em>اختر الموضوع</em>
            </MenuItem>
            {topics.map((topic) => (
              <MenuItem key={topic} value={topic}>
                {topic}
              </MenuItem>
            ))}
          </Select>

          <Button
            variant="contained"
            color="primary"
            onClick={handleSendMessage}
            disabled={isSendDisabled()}
            sx={{
              borderRadius: '20px 0 0 20px',
              height: '100%',
              padding: '16px',
            }}
          >
            <ArrowUpwardIcon />
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default InputArea;

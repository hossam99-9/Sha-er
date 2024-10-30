import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Select, MenuItem } from '@mui/material';

interface InputAreaProps {
  selectedCategory: number;
  onSendMessage: (
    message:
      | { text: string; sender: 'user' }
      | { text: string; prompt: string; poet1: string; sender: 'user' }
      | {
          text: string;
          poet1: string;
          poet2: string;
          topics: string;
          sender: 'user';
        }
  ) => void;
  isLoading: boolean;
}

const poets = ['المتنبي', 'أحمد شوقي', 'امرؤ القيس'];
const topics = ['الحب', 'الفخر', 'الحكمة', 'الهجاء', 'الرثاء'];
const InputArea: React.FC<InputAreaProps> = ({
  selectedCategory,
  onSendMessage,
}) => {
  const initialInputState = {
    input: '',
    dropdown1: '',
    dropdown2: '',
    dropdown3: '',
  };

  const [inputState, setInputState] = useState<
    Record<number, typeof initialInputState>
  >({
    0: initialInputState,
    1: initialInputState,
    2: initialInputState,
  });

  useEffect(() => {
    setInputState((prev) => ({
      ...prev,
      [selectedCategory]: initialInputState,
    }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCategory]);

  const handleInputChange = (value: string) => {
    setInputState((prev) => ({
      ...prev,
      [selectedCategory]: { ...prev[selectedCategory], input: value },
    }));
  };

  const handleDropdownChange = (dropdownIndex: number, value: string) => {
    const dropdownKey =
      `dropdown${dropdownIndex}` as keyof typeof initialInputState;
    setInputState((prev) => ({
      ...prev,
      [selectedCategory]: { ...prev[selectedCategory], [dropdownKey]: value },
    }));
  };

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
        text: `الموضوع: ${input}, الشاعر: ${dropdown1}`,
        prompt: input,
        poet1: dropdown1,
        sender: 'user',
      });
    } else if (selectedCategory === 2) {
      onSendMessage({
        text: `الشاعر الأول: ${dropdown1}, الشاعر الثاني: ${dropdown2}, الموضوع: ${dropdown3}`,
        poet1: dropdown1,
        poet2: dropdown2,
        topics: dropdown3,
        sender: 'user',
      });
    }

    setInputState((prev) => ({
      ...prev,
      [selectedCategory]: { ...prev[selectedCategory], input: '' },
    }));
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isSendDisabled()) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const isSendDisabled = () => {
    if (selectedCategory === 2) {
      const { dropdown1, dropdown2, dropdown3 } = inputState[selectedCategory];
      return !(dropdown1 && dropdown2 && dropdown3);
    }
    if (selectedCategory === 1) {
      const { dropdown1, input } = inputState[selectedCategory];
      return !(dropdown1 && input.trim());
    }
    return !inputState[selectedCategory].input?.trim();
  };

  return (
    <Box mt={2} display="flex" flexDirection="column" sx={{ width: '100%' }}>
      {/* Category 1 */}
      {selectedCategory === 0 && (
        <Box display="flex" alignItems="center">
          <TextField
            value={inputState[selectedCategory].input}
            onChange={(e) => handleInputChange(e.target.value)}
            onKeyDown={handleKeyPress}
            label="أدخل بيت الشعر الذي تريد نقده وتحليله"
            variant="outlined"
            fullWidth
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
            إرسال
          </Button>
        </Box>
      )}

      {/* Category 2 */}
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
            إرسال
          </Button>
        </Box>
      )}

      {/* Category 3 */}
      {selectedCategory === 2 && (
        <Box display="flex" alignItems="center" gap="0">
          <Select
            value={inputState[selectedCategory].dropdown1}
            onChange={(e) => handleDropdownChange(1, e.target.value as string)}
            displayEmpty
            sx={{ width: '30%' }}
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
            sx={{ width: '30%', borderRadius: '0' }}
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
            value={inputState[selectedCategory].dropdown3}
            onChange={(e) => handleDropdownChange(3, e.target.value as string)}
            displayEmpty
            sx={{ width: '30%', borderRadius: '0' }}
          >
            <MenuItem value="">
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
            إرسال
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default InputArea;

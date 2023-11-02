import React, { ButtonHTMLAttributes } from 'react';
import { Button, styled, useTheme } from '@mui/material';

export type ButtonColor = 'green' | 'orange' | 'purple';

const StyledButton = styled(Button)<{ bgcolor: string}>(({ bgcolor}) => ({
  background: bgcolor,
  color: 'black !important',
  borderColor: bgcolor,
  '&:hover': {
    background: bgcolor,
  },
}));


interface CustomButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  color: ButtonColor,
  buttonText?:string,
  sx?:any
}

const CustomButton: React.FC<CustomButtonProps> = (props) => {
  const { color, ...other } = props;
  const theme = useTheme();
  const getColor = (color: ButtonColor): string => {
    switch (color) {
      case 'green':
        return theme.palette.customColors.green;
      case 'orange':
        return theme.palette.customColors.orange;
      case 'purple':
        return theme.palette.customColors.purple;
      default:
        return '#3F51B5';
    }
  };
  return (
    <StyledButton bgcolor={getColor(color)} {...other}>{props.buttonText}</StyledButton>
  );
};


export default CustomButton;

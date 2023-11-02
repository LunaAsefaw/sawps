import React from "react";
import {Box, Typography} from "@mui/material";
import './style.scss';


interface ChartContainerInterface {
    title: string;
    chart: any;
    icon?: string;
}

export default function ChartContainer(props: ChartContainerInterface) {
    return (
        <Box className={'ChartContainerBox'}>
            <Typography className={'TextBox'}>{props.title}</Typography>
            {props.chart}
        </Box>
    )
}

import React, {useEffect, useRef} from "react";
import {Bar} from "react-chartjs-2";
import './style.scss';
import ChartContainer from "../ChartContainer";


interface BarChartInterface {
    chartData: any,
    chartId: string,
    chartTitle: string,
    indexAxis?: string,
    xLabel?: string,
    yLabel?: string,
    xStacked?: boolean,
    yStacked?: boolean
}


export default function BarChart({chartData,
                                 chartId,
                                 chartTitle,
                                 indexAxis = 'y',
                                 xLabel = 'Default X Label',
                                 yLabel = 'Default Y Label',
                                 xStacked = true,
                                 yStacked = true}: BarChartInterface) {

    const options = {
        indexAxis: indexAxis as any,
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                beginAtZero: true,
                display: true,
                stacked: xStacked,
                title: {
                    display: true,
                    text: xLabel,
                    font: {
                        size: 14,
                    },
                },
            },
            y: {
                display: true,
                stacked: yStacked,
                title: {
                    display: true,
                    text: yLabel,
                    font: {
                        size: 14,
                    },
                },
                grid: {
                    display: false,
                },
                ticks: {
                    color: "black",
                },
            },
        },
        plugins: {
            tooltip: {
                enabled: true
            },
            datalabels: {
                display: false,
            },
            legend: {
                display: true,
                position: 'right' as 'right',
                labels: {
                    boxWidth: 20,
                    boxHeight: 13,
                    padding: 12,
                    font: {
                        size: 10,
                    }
                },
            },
        },
    } as const;


    return (
        <ChartContainer title={chartTitle}>
            <div className={'BarChartContainer'}>
                <Bar
                    key={chartId}
                    data={chartData}
                    options={options}
                    className={'bar-chart'}
                />
            </div>
        </ChartContainer>
    )
}

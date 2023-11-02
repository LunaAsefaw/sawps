import React, {useEffect, useRef} from "react";
import {Doughnut} from "react-chartjs-2";


interface DoughnutChartInterface {
    chartData: any,
    chartId: string,
    icon?: string
}

const ChartContainerStyle: React.CSSProperties = {
    position: "relative",
    whiteSpace: "pre-wrap",
};


export default function DoughnutChart(props: DoughnutChartInterface) {
    const chartRef = useRef(null);

    const doughnutIconPlugin = {
        id: props.chartId,
        beforeInit: (chart: any) => {
            if (!chart.options.icon) return;
            const icon = new Image();
            icon.src = chart.options.icon;
            chart.iconImage = icon;
        },
        afterDraw: (chart: any) => {
            if (!chart.iconImage) return;
            const ctx = chart.ctx;
            ctx.save();
            const icon = chart.iconImage;
            const { top, left, width, height } = chart.chartArea;
            const size = Math.min(width, height) / 4;
            const centerX = left + width / 2;
            const centerY = top + height / 2;

            if (icon.complete) {
                ctx.drawImage(icon, centerX - size / 2, centerY - size / 2, size, size);
                ctx.restore();
            } else {
                icon.onload = () => {
                    ctx.drawImage(icon, centerX - size / 2, centerY - size / 2, size, size);
                    ctx.restore();
                };
            }
        }
    };

    const options = {
        cutout: '54%',
        icon: props.icon,
        plugins: {
            legend: {
                position: 'right' as 'right',
                display: true,
                labels: {
                    boxWidth: 20,
                    boxHeight: 13,
                    padding: 12,
                    font: {
                        size: 12,
                    },
                },
            },
            datalabels: {
                color: '#fff',
                font: {
                    size: 12,
                },
            },
            title: {
                display: false,
            },
        },
    };

    useEffect(() => {
        if (chartRef.current) {
            const chart = chartRef.current;
            const icon = new Image();
            icon.src = props.icon;

            icon.onload = () => {
                chart.iconImage = icon;
                chart.update();
            };
        }
    }, [props.icon]);

    return (
        <Doughnut
            ref={chartRef}
            data={props.chartData}
            options={options}
            plugins={[doughnutIconPlugin]}
            style={ChartContainerStyle}
        />
    )
}

import React, {FC, useState, useEffect} from 'react';
import axios from 'axios';
import Skeleton from '@mui/material/Skeleton';
import './styles.scss'
import {
    Chart as ChartJS,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Legend,
    Tooltip,
    Filler,
    LegendItem,
} from 'chart.js';

import {Line} from 'react-chartjs-2'

ChartJS.register(
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Legend,
    Tooltip,
    Filler,
);

interface ISpeciesChartProps{
    species_id: number,
    species_name?:string,
    areaFillColor?:string,
    areaLineColor?:string,
    lineColor?:string,
    index?:number
}

// National trend structure
interface NationalTrendInterface {
    year: number;
    fit: number;
    'se.fit': number;
    lower_ci: number;
    upper_ci: number;
}

const SPECIES_NATIONAL_TREND_URL = '/api/species/{species_id}/trend/national/'

const SpeciesChart:FC<ISpeciesChartProps> = (props)=>{
    const [chartData, setChartData] = useState(null)

    const fetchChartData = () => {
        axios.get(SPECIES_NATIONAL_TREND_URL.replace('{species_id}', props.species_id.toString())).then((response) => {
            if (response) {
                let _data = response.data as NationalTrendInterface[]
                setChartData({
                    labels: _data.map((a) => {
                        if (a.year % 2 === 0) return a.year
                        return ""
                    }),
                    datasets:[
                        {
                            label: props.species_name,
                            data: _data,
                            borderColor: props.lineColor,
                            fill: false,
                            parsing: {
                                xAxisKey: 'year',
                                yAxisKey: 'fit'
                            },
                            pointRadius: 0
                        },
                        {
                            label: 'upper_ci',
                            data: _data,
                            fill: 1,
                            parsing: {
                                xAxisKey: 'year',
                                yAxisKey: 'upper_ci'
                            },
                            backgroundColor: props.areaFillColor,
                            showLine: false,
                            pointRadius: 0,
                        },
                        {
                            label: 'lower_ci',
                            data: _data,
                            fill: 1,
                            parsing: {
                                xAxisKey: 'year',
                                yAxisKey: 'lower_ci'
                            },
                            backgroundColor: props.areaFillColor,
                            showLine: false,
                            pointRadius: 0,
                        },
                    ]
                })
            }
        }).catch((error) => {
            console.log(error)
        })
    }

    useEffect(() => {
        fetchChartData()
    }, [])

    const options:object={
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 1.5,
        scales: {
            y: {grace:50},
        },
        plugins: {
            legend: {
                labels: {
                    filter: function(item: LegendItem, chart: ChartJS) {
                        if (item.text && typeof item.text === 'string') {
                            return !item.text.includes('_ci');
                        }
                        return true; // Return true to keep all other items
                    }
                }
            },
            tooltips: {
                enabled: false
           }
        }
    }

    return(
        <>
            <div className="species-chart-container" data-testid="species-chart">
                {chartData ?
                    <Line
                        data={chartData}
                        options={options}
                        plugins={[]}
                    ></Line> :
                    <Skeleton variant='rectangular' className='species-chart-skeleton' />
                }
            </div>
        </>
    )
}

export default SpeciesChart
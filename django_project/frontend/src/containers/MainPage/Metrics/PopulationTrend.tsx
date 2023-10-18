import React, {FC, useState, useEffect} from 'react';
import axios from 'axios';
import Skeleton from '@mui/material/Skeleton';
// import './styles.scss'
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
import Grid from '@mui/material/Grid';
import Loading from '../../../components/Loading';
import { Typography } from '@mui/material';

/*
a new dataset labeled "Counts" is added to the chartData object. 
This dataset uses the same years as the x-axis and the fit values as the y-axis. 
It's configured to display as points (dots) with a specified size and color.
With this the chart has dots representing the actual counts per year on the chart,
in addition to the existing trend line and confidence intervals.
*/

ChartJS.register(
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement,
    Legend,
    Tooltip,
    Filler,
);

// National trend structure
interface NationalTrendInterface {
    year: number;
    fit: number;
    'se.fit': number;
    lower_ci: number;
    upper_ci: number;
}

const SPECIES_POPULATION_TREND_URL = '/api/species/population_trend/'

const PopulationTrend= (props: any) => {
    const { selectedSpecies, propertyId, startYear, endYear, loading, setLoading, onEmptyDatasets } = props;
    const [chartData, setChartData] = useState(null)

    const fetchChartData = () => {
        axios
      .get(
        `${SPECIES_POPULATION_TREND_URL}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`
      )
      .then((response) => {
            if (response) {
                setLoading(false)
                let _data = response.data as NationalTrendInterface[]
                setChartData({
                    labels: _data.map((a) => {
                      if (a.year % 2 === 0) return a.year;
                      return "";
                    }),
                    datasets: [
                      {
                        label: props.species_name,
                        data: _data,
                        borderColor: props.lineColor,
                        fill: false,
                        parsing: {
                          xAxisKey: "year",
                          yAxisKey: "fit",
                        },
                        pointRadius: 0, // Disable points for the trend line
                      },
                      // Add a new dataset for the counts with points
                      {
                        label: "Counts",
                        data: _data.map((item) => ({ x: item.year, y: item.fit })),
                        borderColor: "rgba(0, 0, 0, 0)", // Transparent line
                        pointBackgroundColor: "rgba(0, 0, 0, 0.8)", // Point color
                        pointRadius: 4, // Point size
                      },
                      {
                        label: "upper_ci",
                        data: _data,
                        fill: 1,
                        parsing: {
                          xAxisKey: "year",
                          yAxisKey: "upper_ci",
                        },
                        backgroundColor: props.areaFillColor,
                        showLine: false,
                        pointRadius: 0,
                      },
                      {
                        label: "lower_ci",
                        data: _data,
                        fill: 1,
                        parsing: {
                          xAxisKey: "year",
                          yAxisKey: "lower_ci",
                        },
                        backgroundColor: props.areaFillColor,
                        showLine: false,
                        pointRadius: 0,
                      },
                    ],
                  });
            }
        }).catch((error) => {
            console.log(error)
            setLoading(false)
        })
    }

    useEffect(() => {
        fetchChartData()
    }, [propertyId, startYear, endYear, selectedSpecies])


    if(chartData === null){
        onEmptyDatasets(false);
    }else onEmptyDatasets(true);
    

    const options:object={
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 1.5,
        scales: {
            y: {grace:50},
        },
        plugins: {
            legend: {
                position: 'right' as 'right',
                labels: {
                    boxWidth: 20,
                    boxHeight: 13,
                    padding: 12,
                    font: {
                        size: 10,
                    },
                    filter: function(item: LegendItem, chart: ChartJS) {
                        if (item.text && typeof item.text === 'string') {
                            return !item.text.includes('_ci');
                        }
                        return true; // Return true to keep all other items
                    }
                }
            },
            tooltips: {
                enabled: true
           }
        }
    }
    
    return (
        <Grid>
          {!loading ? (
            chartData ? (
              <Line
                data={chartData}
                options={options}
                plugins={[]}
              />
            ) : (
                <Typography >
                    No trend data available for selected species
                </Typography>
            )
          ) : (
            <Loading containerStyle={{ minHeight: 160 }} />
          )}
        </Grid>
      );      
}

export default PopulationTrend

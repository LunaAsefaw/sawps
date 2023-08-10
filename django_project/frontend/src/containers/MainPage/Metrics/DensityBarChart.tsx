import React, { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";
import { Bar } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import axios from "axios";
import Loading from "../../../components/Loading";
import { useAppSelector } from "../../../app/hooks";
import { RootState } from "../../../app/store";
import "./index.scss";


Chart.register(CategoryScale);
Chart.register(ChartDataLabels);

const FETCH_SPECIES_DENSITY = '/api/species-population-total-density/'

const DensityBarChart = () => {
    const selectedSpecies = useAppSelector((state: RootState) => state.SpeciesFilter.selectedSpecies)
    const propertyId = useAppSelector((state: RootState) => state.SpeciesFilter.propertyId)
    const startYear = useAppSelector((state: RootState) => state.SpeciesFilter.startYear)
    const endYear = useAppSelector((state: RootState) => state.SpeciesFilter.endYear)
    const [loading, setLoading] = useState(false)
    const [densityData, setDesityData] = useState([])
    const labels = [];
    const totalCounts = [];
    const density = [];

    const fetchActivityPercentageData = () => {
        setLoading(true)
        axios.get(`${FETCH_SPECIES_DENSITY}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`).then((response) => {
            setLoading(false)
            if (response.data) {
                setDesityData(response.data)
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }


    useEffect(() => {
        fetchActivityPercentageData();
    }, [propertyId, startYear, endYear, selectedSpecies])

    for (const each of densityData) {
        labels.push(each.density.species_name);
        totalCounts.push(each.density.total);
        density.push(each.density.density);
    }

    const data = {
        labels: labels,
        datasets: [
            {
                label: 'Total Population',
                backgroundColor: '#75B37A',
                borderColor: '#75B37A',
                borderWidth: 1,
                data: totalCounts,
            },
            {
                label: 'Population density (individuals/Ha)',
                backgroundColor: '#FAA755',
                borderColor: '#FAA755',
                borderWidth: 1,
                data: density,
            },
        ],
    };

    const options = {
        plugins: {
            datalabels: {
                display: false,
            },
            legend: {
                position: 'bottom' as 'bottom',
                labels: {
                    position: 'bottom' as 'bottom',
                    usePointStyle: true,
                    font: {
                        size: 15,
                    },
                    generateLabels: (chart: any) => {
                        const { datasets } = chart.data;
                        return datasets.map((dataset: any, index: any) => ({
                            text: dataset.label,
                            fillStyle: dataset.borderColor,
                            hidden: !chart.isDatasetVisible(index),
                            lineCap: 'round',
                            lineDash: [] as number[],
                            lineDashOffset: 0,
                            lineJoin: 'round',
                            lineWidth: 10,
                            strokeStyle: dataset.borderColor,
                            pointStyle: 'rect',
                            rotation: 0,
                        }))
                    },
                },
            }
        },
        scales: {
            x: {
                beginAtZero: true,
            },
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 50,
                    max: 200,
                },
            },
        },
    };

    return (
        <Box>
            {loading ? <Loading /> :
                <Box className="white-chart" >
                    <Typography>Species Population Totals and Density</Typography>
                    <Bar data={data} options={options} height={450} width={1000}/>
                </Box >}
        </Box>
    );
};

export default DensityBarChart;
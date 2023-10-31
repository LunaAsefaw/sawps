import React, { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";
import { Bar } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import axios from "axios";
import Loading from "../Loading";

Chart.register(CategoryScale);
Chart.register(ChartDataLabels);

const FETCH_SPECIES_LIST = '/api/species-list/';
const FETCH_SPECIES_DENSITY = '/api/properties_population_category/';

interface PopulationCategoryData {
    [key: string]: number;
}

interface Species {
    species_name: string;
    species_colour: string;
    icon: string; // Add the icon property
}

const PopulationCategoryChart = () => {
    const [loading, setLoading] = useState(false);
    const [populationDataArray, setPopulationDataArray] = useState<Array<PopulationCategoryData>>([]);
    const [species, setSpecies] = useState<Species[]>([]);

    const fetchSpeciesList = () => {
        axios.get(FETCH_SPECIES_LIST)
            .then((response) => {
                if (response.data) {
                    setSpecies(response.data as Species[]);
                    setLoading(false);
                }
            })
            .catch((error) => {
                console.log(error);
            });
    }

    useEffect(() => {
        fetchSpeciesList();
    }, []);

    const fetchPopulationCategoryData = (selectedSpecies: string[]) => {
        const startYear = 1960;
        const endYear = new Date().getFullYear();
        const fetchDataPromises = selectedSpecies.map((speciesName) => {
            return axios.get(`${FETCH_SPECIES_DENSITY}?start_year=${startYear}&end_year=${endYear}&species=${speciesName}`)
                .then((response) => {
                    if (response.data) {
                        return {
                            species_name: speciesName,
                            data: response.data
                        };
                    }
                })
                .catch((error) => {
                    console.log(error);
                });
        });

        Promise.all(fetchDataPromises)
            .then((dataResponses) => {
                const newDataArray = dataResponses.reduce((acc, dataResponse) => {
                    if (dataResponse) {
                        acc.push({
                            [dataResponse.species_name]: dataResponse.data
                        });
                    }
                    return acc;
                }, []);
                setPopulationDataArray(newDataArray);
                setLoading(false);
            });
    }

    useEffect(() => {
        const selectedSpecies = species.map(specie => specie.species_name);
        fetchPopulationCategoryData(selectedSpecies);
    }, [species]);

    const generatedCharts = populationDataArray.map((speciesData, index) => {
        const specieName = Object.keys(speciesData)[0];
        const specieData = speciesData[specieName];
        const specie = species.find(specie => specie.species_name === specieName);

        if (index % 2 === 0 && index + 1 < populationDataArray.length) {
            const nextSpeciesData = populationDataArray[index + 1];
            const nextSpecieName = Object.keys(nextSpeciesData)[0];
            const nextSpecieData = nextSpeciesData[nextSpecieName];
            const nextSpecie = species.find(specie => specie.species_name === nextSpecieName);

            const hasNonZeroValues = Object.values(specieData).some(value => value !== 0);
            const nextHasNonZeroValues = Object.values(nextSpecieData).some(value => value !== 0);

            if (hasNonZeroValues || nextHasNonZeroValues) {
                return (
                    <Box key={index} style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between' }}>
                        <Box style={{ width: '98%', marginRight: '2%' }}>
                            <Box style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                                <Typography style={{ fontSize: 20 }}>{specieName}</Typography>
                                {specie && (
                                    <img
                                        src={specie.icon}
                                        alt={`${specieName} Icon`}
                                        style={{ maxWidth: '60px', maxHeight: '60px', marginLeft: '400px' }}
                                    />
                                )}
                            </Box>
                            <Bar
                                data={{
                                    labels: Object.keys(specieData || {}),
                                    datasets: [
                                        {
                                            backgroundColor: specie?.species_colour || '',
                                            borderColor: specie?.species_colour || '',
                                            borderWidth: 1,
                                            data: Object.values(specieData || {}),
                                        },
                                    ],
                                }}
                                options={{
                                    plugins: {
                                        datalabels: {
                                            display: false,
                                        },
                                        legend: {
                                            display: false,
                                        },
                                    },
                                    scales: {
                                        x: {
                                            beginAtZero: true,
                                            ticks: {font: {
                                                size: 20,
                                                weight: "bold" as "bold",
                                              },
                                            }
                                        },
                                        y: {
                                            beginAtZero: true,
                                            ticks: {
                                                font: {
                                                    size: 20,
                                                    weight: "bold" as "bold",
                                                  },
                                                stepSize: 50,
                                            },
                                        },
                                    },
                                }}
                            />
                        </Box>
                        <Box style={{ width: '98%', marginLeft: '2%' }}>
                            <Box style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                                <Typography style={{ fontSize: 20 }}>{nextSpecieName}</Typography>
                                {nextSpecie && (
                                    <img
                                        src={nextSpecie.icon}
                                        alt={`${nextSpecieName} Icon`}
                                        style={{ maxWidth: '60px', maxHeight: '60px', marginLeft: '400px'}}
                                    />
                                )}
                            </Box>
                            <Bar
                                data={{
                                    labels: Object.keys(nextSpecieData || {}),
                                    datasets: [
                                        {
                                            backgroundColor: nextSpecie?.species_colour || '',
                                            borderColor: nextSpecie?.species_colour || '',
                                            borderWidth: 1,
                                            data: Object.values(nextSpecieData || {}),
                                        },
                                    ],
                                }}
                                options={{
                                    plugins: {
                                        datalabels: {
                                            display: false,
                                            font : {
                                                size: 20
                                              }
                                        },
                                        legend: {
                                            display: false,
                                        },
                                    },
                                    scales: {
                                        x: {
                                            beginAtZero: true,
                                            ticks: {font: {
                                                size: 20,
                                                weight: "bold" as "bold",
                                              },
                                            }
                                        },
                                        y: {
                                            beginAtZero: true,
                                            ticks: {
                                                font: {
                                                    size: 20,
                                                    weight: "bold" as "bold",
                                                  },
                                                stepSize: 50,
                                            },
                                        },
                                    },
                                }}
                            />
                        </Box>
                    </Box>
                );
            } else {
                return null; // Don't generate the chart if all values are 0
            }
        } else {
            return null;
        }
    });


    const hasNonZeroCharts = generatedCharts.some(chart => chart !== null);

    return (
        <Box>
            {loading ? (
                <Loading />
            ) : generatedCharts.length > 0 ? (
                <Box className="">
                    {hasNonZeroCharts && (
                        <Typography variant="h6" gutterBottom style={{ textAlign: "left" }}>
                            Number of properties per population category
                        </Typography>
                    )}
                    {generatedCharts}
                </Box>
            ) : null}
        </Box>
    );
};

export default PopulationCategoryChart;

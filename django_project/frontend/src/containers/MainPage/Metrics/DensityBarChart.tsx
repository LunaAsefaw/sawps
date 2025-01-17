import React, { useEffect, useState } from 'react';
import { Grid } from "@mui/material";
import { Bar } from 'react-chartjs-2';
import "./index.scss";
import Loading from '../../../components/Loading';
import axios from 'axios';
import ChartContainer from "../../../components/ChartContainer";
import BarChart from "../../../components/BarChart";

const FETCH_SPECIES_DENSITY = "/api/species-population-total-density/";

const DensityBarChart = (props: any) => {
    const {
        selectedSpecies,
        propertyId,
        startYear,
        endYear,
        loading,
        setLoading,
        densityData,
        setDensityData
    } = props;


    useEffect(() => {
        const fetchActivityPercentageData = () => {
            setLoading(true);
            axios
                .get(
                    `${FETCH_SPECIES_DENSITY}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`
                )
                .then((response) => {
                    setLoading(false);
                    if (response.data) {
                        // Filter out objects with non-null density
                        const filteredData = response.data.filter((item: { density: any[]; }) => {
                            const hasNonNullDensity = item.density.some((densityItem) => densityItem.density !== null);
                            return hasNonNullDensity;
                        });
                        setDensityData(filteredData);
                    } else {
                        setDensityData([]);
                    }
                })
                .catch((error) => {
                    setLoading(false);
                    console.log(error);
                    setDensityData([])
                });
        };

        fetchActivityPercentageData();
    }, [propertyId, startYear, endYear, selectedSpecies, setLoading, setDensityData]);


    const filteredArray = densityData.filter((item: { density: any[]; }) => {
        if (item.density === null) {
            return false; // Filter out items with null density
        }

        if (Array.isArray(item.density)) {
            // Check if all elements in the density array are null or 0
            const isAllNullOrZero = item.density.every((value) => value.density === null || value === 0);
            return !isAllNullOrZero; // Filter out items where all elements are null or 0
        }

        return true; // Keep other items
    });


    // Extract labels and data from the fetched API response
    const labels = filteredArray.map((each: any, index: number) => {
        const provinceName = each.province_name;
        const organizationName = each.organisation_name;

        // Check if the density array exists and has at least one item
        if (each.density && Array.isArray(each.density) && each.density.length > 0) {
            // Access the property_name field from the first item in the density array
            const propertyName = each.density[0].property_name;

            // Helper function to format a name based on the specified rules
            const formatName = (name: string) => {
                const words = name.split(' ');
                if (words.length === 1) {
                    return words[0].substring(0, 2).toUpperCase();
                } else {
                    return words.map(word => word.substring(0, 1).toUpperCase()).join('');
                }
            };

            const provinceCode = formatName(provinceName);
            const organizationCode = formatName(organizationName);
            const propertyCode = formatName(propertyName);
            const uniqueNumericValue = 1000 + index + 1; // Generate unique numeric value starting from 1001

            // Create the label by combining province, organization, property, and the unique numeric value
            const label = `${provinceCode}${organizationCode}${propertyCode}${uniqueNumericValue}`;

            return label;
        }

        return ''; // Return an empty string if density data is missing or invalid
    });

   // Extract years from the fetched API response
    const yearsInData = filteredArray.reduce((years: any[], each: any) => {
        // Check if the density array exists and has at least one item
        if (each.density && Array.isArray(each.density) && each.density.length > 0) {
            // Iterate through the density array and extract all unique years
            each.density.forEach((densityItem: any) => {
                if (densityItem.year) {
                    years.push(densityItem.year);
                }
            });
        }

        return years;
    }, []);

    // Remove duplicate years
    const uniqueYears = Array.from(new Set(yearsInData));

    // Sort the years from highest to lowest
    uniqueYears.sort((a: number, b: number) => b - a);

    // Create datasets for each year using available colors
    const datasets = uniqueYears.map((year: any, index: number) => {
        const backgroundColor = colors[index % colors.length];
        const data = filteredArray.map((each: any) => {
        // Check if the density array exists, is an array, and has at least one item
        if (each.density && Array.isArray(each.density) && each.density.length > 0) {
            // Find the density data object with the matching year, if it exists
            const densityItem = each.density.find((densityDataItem: any) => densityDataItem.year === year);
            if (densityItem) {
            // Access the density value from the found density data object
            return densityItem.density;
            }
        }
        return null; // Return null if density data is missing or invalid for the given year
        });

        if (data.some((value: any) => value !== null)) {
        // Create the dataset
        return {
            label: `${year}`,
            data: data,
            backgroundColor: backgroundColor,
        };
        }
    }).filter(dataset => dataset); // Remove any null datasets

    // Reverse the order of datasets
    datasets.reverse();

    return (
        <Grid>
            {!loading ? (
                <BarChart
                    chartData={{ labels: labels, datasets: datasets }}
                    chartId={'density-bar-chart'}
                    xLabel={'Population density'}
                    yLabel={'Property'}
                    chartTitle={`${selectedSpecies} population density per property`}/>
            ) : (
                <Loading containerStyle={{ minHeight: 160 }} />
            )}
        </Grid>
    );

};

// Define colors for each year
const colors = [
  'rgba(112, 178, 118, 1)',
  'rgba(250, 167, 85, 1)',
  'rgba(157, 133, 190, 1)',
  '#FF5252',
  '#616161',
  'rgba(112, 178, 118, 0.5)',
  'rgba(250, 167, 85, 0.5)',
  'rgba(157, 133, 190, 0.5)',
  'rgba(255, 82, 82, 0.5)',
  'rgba(97, 97, 97, 0.5)'
];

export default DensityBarChart;

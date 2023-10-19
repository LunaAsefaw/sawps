import React from 'react';
import { Bar } from 'react-chartjs-2';
import "./index.scss";
import Loading from '../../../components/Loading';

type AvailableColors = {
    [key: string]: string;
};

const availableColors: AvailableColors = {
    'Adult male': 'rgba(112, 178, 118, 1)', // Solid color for male
    'Adult female': 'rgba(112, 178, 118, 0.5)', // 50% transparency for female
    'Sub-adult male': 'rgba(250, 167, 85, 1)', // Solid color for male
    'Sub-adult female': 'rgba(250, 167, 85, 0.5)', // 50% transparency for female
    'Juvenile male': 'rgba(157, 133, 190, 1)', // Solid color for male
    'Juvenile female': 'rgba(157, 133, 190, 0.5)', // 50% transparency for female
};
const AgeGroupBarChart = (props: any) => {
    const { loading, ageGroupData } = props;


    const filteredData = ageGroupData.filter((item: { total_adult_female: number; total_adult_male: number; total_juvenile_female: number; total_juvenile_male: number; total_sub_adult_female: number; total_sub_adult_male: number; }) => {
        // Check if any of the specified numeric properties are empty or equal to 0
        return (
          item.total_adult_female !== 0 &&
          item.total_adult_male !== 0 &&
          item.total_juvenile_female !== 0 &&
          item.total_juvenile_male !== 0 &&
          item.total_sub_adult_female !== 0 &&
          item.total_sub_adult_male !== 0
        );
      });

    // Extract the species name
    const species = ageGroupData.length > 0 ? ageGroupData[0].owned_species__taxon__common_name_varbatim : '';


    // Define the labels (years) dynamically from ageGroupData and sort them from highest to lowest
    const labels = filteredData.map((data: any) => data.total_year).sort((a: number, b: number) => b - a);

    // Define age groups and their corresponding data properties
    const ageGroups = [
        { label: 'Adult male', dataProperty: 'total_adult_male' },
        { label: 'Adult female', dataProperty: 'total_adult_female' },
        { label: 'Sub-adult male', dataProperty: 'total_sub_adult_male' },
        { label: 'Sub-adult female', dataProperty: 'total_sub_adult_female' },
        { label: 'Juvenile male', dataProperty: 'total_juvenile_male' },
        { label: 'Juvenile female', dataProperty: 'total_juvenile_female' },
    ];

    // Create an array to hold datasets
    const datasets = [];

    // Loop through age groups
    for (const ageGroup of ageGroups) {
        // Map the data for the current age group
        const data = filteredData.map((dataItem: any) => dataItem[ageGroup.dataProperty] || 0);

        // Rearrange the data to match the sorted labels
        const sortedData = labels.map((year: any) => {
            const index = filteredData.findIndex((item: { total_year: any }) => item.total_year === year);
            return data[index];
        });

    // Create the dataset object
    const dataset = {
        label: ageGroup.label,
        data: sortedData,
        backgroundColor: availableColors[ageGroup.label],
    };

    datasets.push(dataset);
}


let data = null;
    
if (labels.length > 0 && datasets.length > 0) {
    data = {
      labels: labels,
      datasets: datasets,
    };
} else return null;

const options = {
    indexAxis: 'y' as const,
    scales: {
        x: {
            beginAtZero: true,
            display: true,
            stacked: true,
            title: {
                display: true,
                text: 'Count', // X-axis label
                font: {
                    size: 14,
                },
            },
        },
        y: {
            display: true,
            stacked: true,
            title: {
                display: true,
                text: 'Year', // Y-axis label
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
        responsive: true,
        maintainAspectRatio: false,
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
                font : {
                  size: 10,
                }
            },
        },
        title: {
            display: true,
            text: `Population per age group for ${species}`,
            font: {
                size: 16,
                weight: 'bold' as 'bold',
            },
        },
    },
} as const;
  


return (
    <>
        {!loading ? (
            <Bar 
                data={data} 
                options={options} 
            />
        ) : (
            <Loading containerStyle={{ minHeight: 160 }} />
        )}
    </>
);
};

export default AgeGroupBarChart;

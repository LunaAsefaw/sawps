import React, { useEffect, useState } from "react";
import { Grid } from "@mui/material";
import { Bar } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import axios from "axios";
import Loading from "../../../components/Loading";
import "./index.scss";

Chart.register(CategoryScale);
Chart.register(ChartDataLabels);

const FETCH_SPECIES_AREA_AVAILABLE = '/api/total-area-available-to-species/';

interface PropertyAreaAvailableData {
    province_name: string;
    organisation_name: any;
    property_name: string;
    area: number;
    year: number;
}

interface PropertyAvailableBarChartProps {
    selectedSpecies: string;
    propertyId: string;
    startYear: number;
    endYear: number;
    loading: boolean;
    setLoading: React.Dispatch<React.SetStateAction<boolean>>;
    onEmptyDatasets: any;
}

const PropertyAvailableBarChart: React.FC<PropertyAvailableBarChartProps> = (props) => {
    const { selectedSpecies, propertyId, startYear, endYear, loading, setLoading, onEmptyDatasets } = props;
    const [propertyAreaAvailableData, setPropertyAreaAvailableData] = useState<PropertyAreaAvailableData[]>([]);
    const [ renderChart, setRenderChart] = useState(false);

    // Define colors for each year
    const availableColors = [
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

    const fetchAreaAvailable = () => {
        setLoading(true);
        axios.get(`${FETCH_SPECIES_AREA_AVAILABLE}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`)
            .then((response) => {
                setLoading(false);
                if (response.data) {
                     if(response.data.length > 0){
                    onEmptyDatasets(true)
                  }else onEmptyDatasets(false)
                    setPropertyAreaAvailableData(response.data);
                }
            })
            .catch((error) => {
                setLoading(false);
                console.log(error);
            });
    };

    useEffect(() => {
        if(selectedSpecies !== ''){
            fetchAreaAvailable();
            setRenderChart(true)
        }
            
        else {
            setRenderChart(false);
            setPropertyAreaAvailableData([])
        }
    }, [propertyId, startYear, endYear, selectedSpecies]);

    const dataByPropertyAndOrganization: Record<string, {
        years: number[];
        areas: number[];
        province: string;
    }> = {};

    for (const each of propertyAreaAvailableData) {
        const key = `${each.property_name}-${each.organisation_name}`;
        if (!dataByPropertyAndOrganization[key]) {
            dataByPropertyAndOrganization[key] = {
                years: [],
                areas: [],
                province: each.province_name
            };
        }
        dataByPropertyAndOrganization[key].years.push(each.year);
        dataByPropertyAndOrganization[key].areas.push(each.area);
    }

    const groupedData = Object.entries(dataByPropertyAndOrganization).map(([key, value]) => {
        const [property_name, organisation_name] = key.split('-');
        return {
            property_name,
            organisation_name,
            years: value.years,
            areas: value.areas,
            province_name: value.province,
        };
    });


    // Extract labels and data from the fetched API response
    const labelsB = groupedData.map((group, index) => {
        const property_name = group.property_name;
        const organisation_name = group.organisation_name;
        const province_name = group.province_name;

        // Helper function to format a name based on the specified rules
        const formatName = (name: string) => {
            const words = name.split(' ');
            if (words.length === 1) {
                return words[0].substring(0, 2).toUpperCase();
            } else {
                return words.map(word => word.substring(0, 1).toUpperCase()).join('');
            }
        };


        const provinceCode = formatName(province_name);
        const organizationCode = formatName(organisation_name);
        const propertyCode = formatName(property_name);
        const uniqueNumericValue = 1000 + index + 1; // Generate unique numeric value starting from 1001

        // Create the label by combining province, organization, property, and the unique numeric value
        const label = `${provinceCode}${organizationCode}${propertyCode}${uniqueNumericValue}`;

        return label;
    });

    /// Extract unique years from groupedData and sort them in descending order
    const uniqueYears: number[] = Array.from(
        new Set(
        groupedData.reduce((years, group) => {
            return years.concat(group.years);
        }, [])
        )
    ).sort((a, b) => b - a); // Sort in descending order
    
    // Generate legend labels based on uniqueYears in descending order
    const year_labels = uniqueYears.map((year) => year.toString());
    
    const backgroundColors: string[] = uniqueYears.map((year, index) => {
        return availableColors[index % availableColors.length]; // Assign colors based on year
    });
  
  // Create data for each year to stack the areas
  const datasets = uniqueYears.map((year, index) => {
    const dataForYear = groupedData.map((group) => {
      const areaIndex = group.years.indexOf(year);
      return areaIndex !== -1 ? group.areas[areaIndex] : 0;
    });
  
    return {
      label: year.toString(),
      backgroundColor: backgroundColors[index],
      borderColor: backgroundColors[index],
      borderWidth: 1,
      data: dataForYear,
    };
  });
  
  const data = {
    labels: labelsB,
    datasets: datasets,
  };
  
  const options = {
    indexAxis: 'y' as const,
    plugins: {
      responsive: true,
      maintainAspectRatio: false,
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
            },
        },
        generateLabels: (chart: { data: { labels: any[] } }) => {
          return year_labels.map((label, index) => {
            return {
              text: label, // Use the year as the legend label
              fillStyle: backgroundColors[index], // Assign the corresponding background color
            };
          });
        },
      },
      title: {
        display: true,
        text: `Total area available to ${selectedSpecies}`,
        font: {
          size: 16,
          weight: 'bold' as 'bold',
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        stacked: true, // Enable stacking on the x-axis
        title: {
          display: true,
          text: 'Area (Ha)', // X-axis label
          font: {
            size: 14,
          },
        },
      },
      y: {
        beginAtZero: true,
        stacked: true, // Enable stacking on the y-axis
        ticks: {
          stepSize: 50,
          max: 200,
        },
        title: {
          display: true,
          text: 'Properties', // Y-axis label
          font: {
            size: 14,
          },
        },
      },
    },
  };

    return (
        <Grid>
            {!loading ? (
                <Bar 
                    data={data} 
                    options={options}
                />
            ) : (
                <Loading containerStyle={{ minHeight: 160 }} />
            )}
        </Grid>
    );
};

export default PropertyAvailableBarChart;

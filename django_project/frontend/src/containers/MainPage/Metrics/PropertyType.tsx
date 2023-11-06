import React, { useEffect, useState } from 'react';
import { Grid } from "@mui/material";
import { Bar } from 'react-chartjs-2';
import "./index.scss";
import Loading from '../../../components/Loading';
import axios from 'axios';
import ChartContainer from "../../../components/ChartContainer";

interface PropertyTypeData {
  backgroundColor: any;
  property_type__name: string;
  name: string;
  total_area: number;
}

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

const FETCH_SPECIES_DENSITY = '/api/total-area-per-property-type/';

const PropertyTypeBarChart = (props: any) => {
  const { selectedSpecies, propertyId, startYear, endYear, loading, setLoading, onEmptyDatasets } = props;
  const [propertyTypeData, setPropertyTypeData] = useState<PropertyTypeData[]>([]);
  const labels: string[] = [];
  const legend_labels: string[] = [];
  const totalArea: number[] = [];
  const datasets: any = [];

  const fetchActivityPercentageData = () => {
    setLoading(true);
    axios
      .get(`${FETCH_SPECIES_DENSITY}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`)
      .then((response) => {
        setLoading(false);
        if (response.data) {
          if(response.data.length > 0){
            onEmptyDatasets(true)
          }else {
            onEmptyDatasets(false)
          }
          const uniquePropertyTypes: Record<string, number> = {};
          const uniqueColors: Record<string, string> = {};
  
          const filtered_data = response.data.filter(
            (item: { total_area: number; }) => item.total_area !== 0 && item.total_area !== null
          );
  
          filtered_data.forEach((item: PropertyTypeData, index: number) => {
            if (!uniquePropertyTypes[item.property_type__name]) {
              uniquePropertyTypes[item.property_type__name] = 0;
              uniqueColors[item.property_type__name] = colors[index % colors.length]; // Assign a color from the array
            }
            uniquePropertyTypes[item.property_type__name] += item.total_area;
          });
  
          const newData: PropertyTypeData[] = Object.keys(uniquePropertyTypes).map((property_type__name) => ({
            property_type__name,
            name: '', 
            total_area: uniquePropertyTypes[property_type__name],
            backgroundColor: uniqueColors[property_type__name], // Assign the color
          }));
  
          const sortedData = newData.sort((a, b) => a.property_type__name.localeCompare(b.property_type__name));
          setPropertyTypeData(sortedData);
        }
      })
      .catch((error) => {
        setLoading(false);
        console.log(error);
      });
  };
  

  useEffect(() => {
    fetchActivityPercentageData();
  }, [propertyId, startYear, endYear, selectedSpecies]);

  for (const each of propertyTypeData) {
    labels.push(each.property_type__name); // Use 'property_type__name' as label
    legend_labels.push(each.name);
    totalArea.push(each.total_area);
  }

  for (var count = 0; count < labels.length; count++) {

    // Create an array with leading zeros based on the index
    const dataWithLeadingZeros = Array(count).fill(0);
    dataWithLeadingZeros.push(totalArea[count]);

    datasets.push(
        {
            label: labels[count],
            data: dataWithLeadingZeros,
            backgroundColor: propertyTypeData[count].backgroundColor, // Use the assigned color
        }
    );
}

  const data = {
    labels: labels,
    datasets: datasets,
  };

  const options = {
  indexAxis: 'x' as const,
  scales: {
    x: {
      beginAtZero: false,
      display: true,
      stacked: true,
      title: {
        display: true,
        text: 'Property type', // X-axis label
        font: {
          size: 14,
        },
      },
      barPercentage: 1, // Set barPercentage to 1 to make bars fill the label space
      categoryPercentage: 1, // Set categoryPercentage to 1 to make bars fill the label space
    },
    y: {
      display: true,
      stacked: true,
      grid: {
        display: false,
      },
      ticks: {
        color: "black",
      },
      title: {
        display: true,
        text: 'Area (Ha)', // Y-axis label
        font: {
          size: 14,
        },
      },
      callback: (value: string, index: number) => {
        return labels[index];
      },
    },
  },
  plugins: {
    responsive: true,
    maintainAspectRatio: false,
    tooltip: {
      enabled: true,
      callbacks: {
        label: (context: { dataset: any; parsed: any; dataIndex: number; }) => {
          const datasetLabel = context.dataset.label || '';
          const value = context.parsed.y;
          const property = propertyTypeData[context.dataIndex];
          return `${datasetLabel}: ${property.name} - ${value} Ha`;
        },
      },
    },
    datalabels: {
      display: false,
    },
    legend: {
      display: false,
      position: 'right' as 'right',
      labels: {
        boxWidth: 20,
        boxHeight: 13,
        padding: 12,
        font: {
          size: 10,
          weight: "bold" as "bold"
        }
      },
    }
  },
} as const;


  return (
    <Grid>
      {!loading ? (
        <ChartContainer title={'Total area per property type'} chart={
          <Bar
            data={data}
            options={options}
            className={'bar-chart'}
          />
        }/>
      ) : (
        <Loading containerStyle={{ minHeight: 160 }} />
      )}
    </Grid>
  );
};

export default PropertyTypeBarChart;

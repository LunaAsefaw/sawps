import React from 'react';
import {Bar} from 'react-chartjs-2';
import "./index.scss";
import Loading from '../../../components/Loading';
import ChartContainer from "../../../components/ChartContainer";
import BarChart from "../../../components/BarChart";

type AvailableColors = {
  [key: string]: string;
};

type ageGroup = {
  total_adult_female: number;
  total_adult_male: number;
  total_juvenile_female: number;
  total_juvenile_male: number;
  total_sub_adult_female: number;
  total_sub_adult_male: number;
}

const availableColors: AvailableColors = {
  'Adult male': 'rgba(112, 178, 118, 1)', // Solid color for male
  'Adult female': 'rgba(112, 178, 118, 0.5)', // 50% transparency for female
  'Sub-adult male': 'rgba(250, 167, 85, 1)', // Solid color for male
  'Sub-adult female': 'rgba(250, 167, 85, 0.5)', // 50% transparency for female
  'Juvenile male': 'rgba(157, 133, 190, 1)', // Solid color for male
  'Juvenile female': 'rgba(157, 133, 190, 0.5)', // 50% transparency for female
};
const AgeGroupBarChart = (props: any) => {
  const {loading, ageGroupData} = props;

  const filteredData = ageGroupData;

  // Extract the species name
  const species = ageGroupData.length > 0 ? ageGroupData[0].taxon__common_name_varbatim : '';


  // Define the labels (years) dynamically from ageGroupData and sort them from highest to lowest
  const labels = filteredData.map((data: any) => data.total_year).sort((a: number, b: number) => b - a);

  // Define age groups and their corresponding data properties
  const ageGroups = [
    {label: 'Adult male', dataProperty: 'total_adult_male'},
    {label: 'Adult female', dataProperty: 'total_adult_female'},
    {label: 'Sub-adult male', dataProperty: 'total_sub_adult_male'},
    {label: 'Sub-adult female', dataProperty: 'total_sub_adult_female'},
    {label: 'Juvenile male', dataProperty: 'total_juvenile_male'},
    {label: 'Juvenile female', dataProperty: 'total_juvenile_female'},
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
      backgroundColor: availableColors[ageGroup.label]
    };

    datasets.push(dataset);
  }

  const addUnspecifiedData = () => {
    let unspecifiedData: number[] = [];
    for (let i = 0; i < filteredData.length; i++) {
      let total = 0;
      for (const ageGroup of ageGroups) {
        // Map the data for the current age group
        total += filteredData[i][ageGroup.dataProperty] || 0;
      }
      if (total === 0) {
        unspecifiedData.push(filteredData[i]['total_total'])
      } else {
        unspecifiedData.push(0)
      }
    }

    // Rearrange the data to match the sorted labels
    const sortedData = labels.map((year: any) => {
      const index = filteredData.findIndex((item: { total_year: any }) => item.total_year === year);
      return unspecifiedData[index];
    });

    datasets.push({
      label: 'Unspecified',
      data: sortedData,
      backgroundColor: 'rgba(204, 204, 204, 1)'
    });
  }

  addUnspecifiedData();

  let data = null;

  if (labels.length > 0 && datasets.length > 0) {
    data = {
      labels: labels,
      datasets: datasets,
    };
  } else return null;

  return (
    <>
      {!loading ? (
        <BarChart
            chartData={data}
            chartId={'age-group-bar-chart'}
            chartTitle={`Population per age group for ${species}`}
            yLabel={'Year'}
            xLabel={'Count'}
        />
      ) : (
        <Loading containerStyle={{minHeight: 160}}/>
      )}
    </>
  );
};

export default AgeGroupBarChart;

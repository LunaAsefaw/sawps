import React, { useEffect, useState } from "react";
import { Doughnut } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import Loading from "../../../components/Loading";
import axios from "axios";
import "./index.scss";
import ChartContainer from "../../../components/ChartContainer";
import DoughnutChart from "../../../components/DoughnutChart";

Chart.register(CategoryScale);
Chart.register(ChartDataLabels);

const FETCH_POPULATION_ESTIMATE_CATEGORY_COUNT = "/api/total-count-per-population-estimate/";

const availableColors = [
  'rgba(112, 178, 118, 1)',
  'rgba(250, 167, 85, 1)',
  'rgba(157, 133, 190, 1)',
  '#FF5252',
  '#616161',
  // additional transparency colors for years
  'rgba(112, 178, 118, 0.5)', // 50% transparency
  'rgba(255, 82, 82, 0.5)', // 50% transparency
  'rgba(97, 97, 97, 0.5)', // 50% transparency
  'rgba(157, 133, 190, 0.5)', // 50% transparency
  'rgba(250, 167, 85, 0.5)', // 50% transparency
];

const PopulationEstimateCategoryCount = (props: any) => {
  const {
    selectedSpecies,
    propertyId,
    startYear,
    endYear,
    activityData
  } = props;
  let year: number | null = null;
  const [speciesData, setSpeciesData] = useState([]);
  const [loading, setLoading] = useState<boolean>(false);

  const [backgroundImageUrl, setBackgroundImageUrl] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (activityData && activityData.length > 0) {
      const firstItem = activityData[0];
      if (firstItem.graph_icon) {
        setBackgroundImageUrl(firstItem.graph_icon);
      } else {
        setBackgroundImageUrl(undefined);
      }
    } else {
      setBackgroundImageUrl(undefined)
    }
  }, [activityData]);

  const fetchPopulationEstimateCategoryCount = () => {
    setLoading(true);
    axios
      .get(
        `${FETCH_POPULATION_ESTIMATE_CATEGORY_COUNT}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`
      )
      .then((response) => {
        setLoading(false);
        if (response.data) {
          setSpeciesData(response.data);
        } else {
          setSpeciesData([])
        }
      })
      .catch((error) => {
        console.log(error);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchPopulationEstimateCategoryCount();
  }, [propertyId, startYear, endYear, selectedSpecies]);

  // Initialize variables
  const labels: string[] = [];
  const data: number[] = [];
  const uniqueColors: string[] = [];

  // Iterate through the keys of speciesData
  for (const category in speciesData) {
    if (speciesData.hasOwnProperty(category)) {
      const categoryData = speciesData[category];
      const count = categoryData.count;
      year = categoryData.years[0];

      let paddedLabel = category

      if(category.length > 25){
        paddedLabel = category.substring(0, 22) + '...';
      }

      labels.push(paddedLabel.padEnd(50, ' ')); // Use the padded label

      data.push(count);
      uniqueColors.push(availableColors[labels.length - 1]);
    }
  }

  // Create the chartData object
  const chartData = {
    labels: labels,
    datasets: [
      {
        data: data,
        backgroundColor: uniqueColors,
      },
    ],
  };

  // Create chart title
  let chartTitle = "Please select a species for the chart to show available data";

  if (selectedSpecies) {
    if (Object.keys(speciesData).length > 0) {
      chartTitle = `Total count per population estimate category for ${selectedSpecies}`;
      if (year) {
        chartTitle += ` year ${year}`;
      }
    } else {
      chartTitle = "No data available for current filter selections";
    }
  }

  return (
    <>
      {!loading ? (
          <ChartContainer title={chartTitle}>
            <DoughnutChart
                chartId={'population-estimate-category'}
                chartData={chartData}
                icon={backgroundImageUrl}
            />
          </ChartContainer>
      ) : (
        <Loading containerStyle={{ minHeight: 160 }} />
      )}
    </>
  );
};


export default PopulationEstimateCategoryCount;

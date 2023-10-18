import React, { useEffect, useState } from "react";
import { Doughnut } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import Loading from "../../../components/Loading";
import axios from "axios";
import "./index.scss";

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

const PopulationEstimateAsPercentage = (props: any) => {
  const {
    selectedSpecies,
    propertyId,
    startYear,
    endYear,
    loading,
    setLoading,
    activityData,
    onEmptyDatasets
  } = props;

  const [speciesData, setSpeciesData] = useState<any>({});
  const [backgroundImageUrl, setBackgroundImageUrl] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (activityData && activityData.length > 0) {
      const firstItem = activityData[0];
      if (firstItem.graph_icon) {
        setBackgroundImageUrl(firstItem.graph_icon);
      }

    }
  }, [activityData]);

  const fetchPopulationEstimateCategoryCount = () => {
    setLoading(true);
    axios
      .get(
        `${FETCH_POPULATION_ESTIMATE_CATEGORY_COUNT}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`
      )
      .then((response) => {
        if (response.data) {
          if (Object.keys(response.data).length === 0) {
              onEmptyDatasets(false)
          } else {
              onEmptyDatasets(true)
          }
          setSpeciesData(response.data);
          setLoading(false);
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
  let year: number | null = null;

  // Iterate through the keys of speciesData
  for (const category in speciesData) {
    if (speciesData.hasOwnProperty(category)) {
      const categoryData = speciesData[category];
      const percentage = categoryData.percentage;
      year = categoryData.years[0];

      const paddedLabel = category.padEnd(50, ' '); // Pad with spaces
          
      labels.push(paddedLabel); // Use the padded label

      // labels.push(category);
      data.push(percentage);
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
  let chartTitle = `Population estimate category count as % of the total population for ${selectedSpecies} year ${year}`;

  if (!selectedSpecies) {
    chartTitle = "Please select a species for the chart to show available data";
  } else if (Object.keys(speciesData).length === 0) {
    chartTitle = "No data available for current filter selections";
  }

  const options = {
    cutout: "54%",
    plugins: {
      legend: {
        position: "right" as "right",
        display: true,
        labels: {
          boxWidth: 20,
          boxHeight: 13,
          padding: 12,
          font: {
            size: 12,
          },
        },
      },
      datalabels: {
        color: "#fff",
        formatter: (value: number) => {
          return `${value.toFixed(2)}%`;
        },
        font: {
          size: 12,
        },
      },
      title: {
        display: true,
        text: chartTitle,
        align: 'start' as 'start',
        font: {
          size: 16,
          weight: 'bold' as 'bold',
        },
      },
    },
  };

 // custom styling for donut charts
 const chartContainerStyle: React.CSSProperties = {
  position: "relative",
  backgroundImage: `url(${backgroundImageUrl})`,
  backgroundSize: "18% 20%", // width and height of image
  backgroundPosition: "19.6% 57%", //horizontal and vertical position respectively
  backgroundRepeat: "no-repeat",
  whiteSpace: "pre-wrap", // Allow text to wrap
};

    return (
      <>
        {!loading ? (
            <Doughnut
              data={chartData}
              options={options}
              style={chartContainerStyle}
            />
        ) : (
          <Loading containerStyle={{ minHeight: 160 }} />
        )}
      </>
    );
};

export default PopulationEstimateAsPercentage;

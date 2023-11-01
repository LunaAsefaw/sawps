import React, { useEffect, useState } from "react";
import { Doughnut } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import Loading from "../../../components/Loading";
import "./index.scss";



Chart.register(CategoryScale);
Chart.register(ChartDataLabels);

const availableColors = [
  'rgba(112, 178, 118, 1)',
  'rgba(250, 167, 85, 1)',
  'rgba(157, 133, 190, 1)',
  '#FF5252',
  '#616161',
  // additional transparency colors for years
  'rgba(112, 178, 118, 0.5)',  // 50% transparency
  'rgba(255, 82, 82, 0.5)',  // 50% transparency
  'rgba(97, 97, 97, 0.5)',  // 50% transparency
  'rgba(157, 133, 190, 0.5)',  // 50% transparency
  'rgba(250, 167, 85, 0.5)',  // 50% transparency
];


function processDataForChart(data: any) {
  const activityCounts: any = {};
  const colors = [];

  data.forEach((item: any) => {
    item.activities.forEach((activity: any) => {
      if (!activityCounts[activity.activity_type]) {
        activityCounts[activity.activity_type] = 0;
      }
      activityCounts[activity.activity_type] += activity.total;
    });
  });

  for (const activityType of Object.keys(activityCounts)) {
      colors.push(availableColors[Object.keys(activityCounts).indexOf(activityType)]);
  }

  return {
    labels: Object.keys(activityCounts),
    datasets: [{
      label: 'Total Count per Activity Type',
      data: Object.values(activityCounts),
      backgroundColor: colors
    }]
  };
}

interface SpeciesDataItem {
    province: string;
    species: string;
    year: number | null;
    count: number | null;
}


  const TotalCountPerActivity = (props: any) => {
    const {
      selectedSpecies,
      propertyId,
      startYear,
      endYear,
      loading,
      activityData,
      onEmptyDatasets
    } = props;
    const [backgroundImageUrl, setBackgroundImageUrl] = useState<string | undefined>(undefined);

    useEffect(() => {
      if (activityData && activityData.length > 0) {
        onEmptyDatasets(true)
        const firstItem = activityData[0];
        if (firstItem.graph_icon) {
          setBackgroundImageUrl(firstItem.graph_icon);
        }
      }else onEmptyDatasets(false)
    }, [propertyId,startYear,endYear,activityData, selectedSpecies]);

    // Initialize variables
    const labels: string[] = [];
    const data: number[] = [];
    const uniqueColors: string[] = [];
    let year: number = endYear; // Set the year to the provided startYear

    if (activityData && activityData.length > 0) {
      // Iterate through activityData
      activityData.forEach((speciesData: any) => {
        const speciesActivities = speciesData.activities;

        // Find the activity entry that matches the provided startYear
        const matchingActivity = speciesActivities.find(
          (activity: any) => activity.year === endYear? activity: null
        );

        if (matchingActivity) {
          onEmptyDatasets(true)
          const activityType = matchingActivity.activity_type;
          const total = matchingActivity.total;

          // Check if the activityType is not in the labels list
          if (!labels.includes(activityType)) {
            let paddedLabel = activityType + '';
            if (activityType.length > 25) {
              // Trim the name to 22 characters and add '...' at the end
              paddedLabel = activityType.substring(0, 22) + '...';
            }

            labels.push(paddedLabel.padEnd(50, ' ')); // Use the padded label
            data.push(total);
            uniqueColors.push(availableColors[labels.length - 1]);
          }
        } else onEmptyDatasets(false)
      });
    }

    // Create the chartData object
    const chartData = processDataForChart(activityData);

    // Define chart title based on conditions
    let chartTitle = 'No data available for current filter selections';

    if (selectedSpecies && activityData && activityData.length > 0) {
      chartTitle = `Total count per activity for ${selectedSpecies} year ${year}`;
    }

    if (!selectedSpecies){
        chartTitle = "Please select a species for the chart to show available data";
    }

    const options = {
      cutout: '54%',
      plugins: {
        legend: {
          position: 'right' as 'right',
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
          color: '#fff',
          font: {
            size: 12,
          },
        },
        title: {
          display: true,
          text: chartTitle,
          align: 'start' as 'start',
          font: {
            size: 20,
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
        backgroundPosition: "19.5% 57%", //horizontal and vertical position respectively
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

  export default TotalCountPerActivity;

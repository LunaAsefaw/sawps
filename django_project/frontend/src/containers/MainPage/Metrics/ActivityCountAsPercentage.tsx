import React, { useEffect, useState } from "react";
import { Doughnut } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import Loading from "../../../components/Loading";
import "./index.scss";

Chart.register(CategoryScale);
Chart.register(ChartDataLabels);

interface ActivityItem {
  activity_type: string;
  year: number;
  total: number;
}

interface ActivityDataItem {
  graph_icon: any;
  species_name: string;
  activities: ActivityItem[];
  total: number;
}

interface Props {
  selectedSpecies: string;
  startYear: number;
  endYear: number;
  loading: boolean;
  activityData: ActivityDataItem[];
  onEmptyDatasets: any
}

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

const ActivityCountAsPercentage: React.FC<Props> = ({
  selectedSpecies,
  startYear,
  endYear,
  loading,
  activityData,
  onEmptyDatasets
}: Props) => {
  // Initialize variables
  const labels: string[] = [];
  const data: string[] = [];
  const uniqueColors: string[] = [];
  let year: number | null = null; //use effect to update this guy
  const recentActivitiesMap: Record<string, any> = {};

  const [backgroundImageUrl, setBackgroundImageUrl] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (activityData && activityData.length > 0) {
      const firstItem = activityData[0];
      if (firstItem.graph_icon) {
        setBackgroundImageUrl(firstItem.graph_icon);
      }
    }
  }, [activityData, selectedSpecies,startYear,endYear]);

  // Iterate through activityData
  activityData.forEach((speciesData: ActivityDataItem) => {
    if (speciesData.species_name.toLocaleLowerCase() !== selectedSpecies.toLocaleLowerCase()) {
      // Rule 1: If species doesn't match, assign null data
      year = null;
      return;
    }

    const speciesActivities = speciesData.activities;

    // Iterate through activities to find the most recent year
    speciesActivities.forEach((activity: ActivityItem) => {
      if (year === null || activity.year > year) {
        year = activity.year;
      }
    });

    // Rule 3: If the year doesn't match startYear or endYear, use the most recent year
    if (year !== null && (year < startYear || year > endYear)) {
      year = null;
    }

    // Rule 2: Only save the activities with the most recent year
    const recentActivities = speciesActivities.filter(
      (activity: ActivityItem) => activity.year === year
    );

    // Get the total for the most recent year
    const totalForMostRecentYear = speciesData.total;

    // Rule 4: Store activities in a cleaner object and calculate percentages
    recentActivities.forEach((recentActivity: ActivityItem) => {
      const activityType = recentActivity.activity_type;
      const total = recentActivity.total;

      // Calculate the percentage using the total from the most recent year
      const percentage = ((total / totalForMostRecentYear) * 100).toFixed(2) ;//+ "%";

      // Rule 4: Save unique activity types
      // Check if the activityType is not in the labels list
      if (!labels.includes(activityType)) {
        // Remove text before "/" to get text after "/"
        // const modifiedLabel = activityType.split('/').pop(); // Get text after "/"
        const paddedLabel = activityType.padEnd(50, ' '); // Pad with spaces
          
        labels.push(paddedLabel); // Use the padded label
        // labels.push(activityType); // Use modified label or the original if there's no text after "/"
        data.push(percentage);
        uniqueColors.push(availableColors[labels.length - 1]);
     }
      

      // Rule 4: Store activities in a cleaner object
      if (!recentActivitiesMap[activityType]) {
        recentActivitiesMap[activityType] = {
          total: 0,
          year: year,
        };
      }
      recentActivitiesMap[activityType].total += total;
    });
  });

   if(labels.length>0){
    onEmptyDatasets(true)
  }else onEmptyDatasets(false);

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
            return `${value}%`;
        },
        font: {
          size: 12,
        },
      },
      title: {
        display: true,
        text: year
          ? `Activity count as % of total population for ${selectedSpecies} year ${year}`
          : `No data available for ${selectedSpecies} current filter selections`,
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

export default ActivityCountAsPercentage;

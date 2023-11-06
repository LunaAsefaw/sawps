import React, { useEffect, useState } from "react";
import axios from "axios";
import Loading from "../../../components/Loading";
import ChartContainer from "../../../components/ChartContainer";
import DoughnutChart from "../../../components/DoughnutChart";

const FETCH_ACTVITY_COUNT = "/api/species-count-per-province/";

type ProvinceData = {
  total_area: number;
  species_area: number;
  percentage: string;
};

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


type SpeciesData = {
  [speciesName: string]: {
    [provinceName: string]: ProvinceData;
  };
};



interface SpeciesDataItem {
  province: string;
  species: string;
  year: number | null;
  count: number | null;
}



const SpeciesCountAsPercentage = (props: any) => {
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
  const [speciesData, setSpeciesData] = useState<SpeciesDataItem[]>([]);
  const [backgroundImageUrl, setBackgroundImageUrl] = useState<string | undefined>(undefined);
  console.debug(activityData)

  const fetchActivityCount = () => {
    setLoading(true);
    axios
      .get(
        `${FETCH_ACTVITY_COUNT}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`
      )
      .then((response) => {
        if (response.data) {
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
    fetchActivityCount();
  }, [propertyId, startYear, endYear, selectedSpecies]);

  useEffect(() => {
    if (activityData && activityData.length > 0) {
      const firstItem = activityData[0];
      if (firstItem.graph_icon) {
        setBackgroundImageUrl(firstItem.graph_icon);
      }

    }else setBackgroundImageUrl('')
  }, [activityData]);

  // Filter speciesData based on the most recent year
  const legendLabels: number[] = Array.from(new Set(speciesData.map((item) => item.year)))
    .filter((year) => year !== null) as number[];

  const currentYear = new Date().getFullYear();
  const endYearOrCurrent = endYear === currentYear ? Math.max(...legendLabels) : endYear;
  const mostRecentYear = Math.max(startYear, endYearOrCurrent);

  const filteredSpeciesData = speciesData.filter((item) => item.year === mostRecentYear);

  const total = filteredSpeciesData.reduce((acc, item) => acc + (item.count || 0), 0);

  const calculatedPercentageValues = filteredSpeciesData.map((item) => ({
    ...item,
    percentage: (item.count / total) * 100,
  }));

  const labels = calculatedPercentageValues.map((item) => {
    // Check if the province name is longer than 25 characters
    if (item.province.length > 25) {
      // Trim the name to 22 characters and add '...' at the end
      return item.province.substring(0, 22) + '...';
    }
    return item.province.padEnd(50, ' ');
  });
  
  const percentages = calculatedPercentageValues.map((item) => item.percentage);

  const uniqueBackgroundColors = Array.from(new Set(labels)).map(
    (_, index) => {
      const colorIndex = index % availableColors.length;
      return availableColors[colorIndex];
    }
  );

  const chartData = {
    labels: labels,
    datasets: [
      {
        data: percentages,
        backgroundColor: uniqueBackgroundColors,
      },
    ],
  };

  if (filteredSpeciesData.length === 0) {
    return null;
  }
  
  // Define chart title based on conditions
  let chartTitle = "Please select a species for the chart to show available data";

  if (selectedSpecies) {
    if (filteredSpeciesData.length > 0) {
      chartTitle = `Total count as % of total population per province for ${selectedSpecies} year ${mostRecentYear}`;
    } else {
      chartTitle = "No data available for current filter selections";
      return null;
    }
  }

  return (
    <>
      {!loading ? (
            <ChartContainer title={chartTitle} chart={
              <DoughnutChart
                  chartData={chartData}
                  chartId={'species-count-as-percentage'}
                  icon={backgroundImageUrl}
              />
            } icon={backgroundImageUrl}/>
      ) : (
        <Loading containerStyle={{ minHeight: 160 }} />
      )}
    </>
  );
};

export default SpeciesCountAsPercentage;


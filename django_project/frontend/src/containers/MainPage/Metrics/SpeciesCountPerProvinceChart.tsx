import React, { useEffect, useState } from "react";
import axios from "axios";
import Loading from "../../../components/Loading";
import { Bar } from 'react-chartjs-2';
import { Grid } from "@mui/material";
import ChartContainer from "../../../components/ChartContainer";
import BarChart from "../../../components/BarChart";

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
  'rgba(112, 178, 118, 0.5)',
  'rgba(250, 167, 85, 0.5)',
  'rgba(157, 133, 190, 0.5)',
  'rgba(255, 82, 82, 0.5)',
  'rgba(97, 97, 97, 0.5)'
];

interface SpeciesDataItem {
  province: string;
  species: string;
  year: number | null;
  count: number | null;
}

const SpeciesCountPerProvinceChart = (props: any) => {
  const {
    selectedSpecies,
    propertyId,
    startYear,
    endYear,
    loading,
    setLoading
  } = props;
  const [speciesData, setSpeciesData] = useState<SpeciesDataItem[]>([]);

  const fetchActivityCount = () => {
    setLoading(true);
    axios
      .get(
        `${FETCH_ACTVITY_COUNT}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`
      )
      .then((response) => {
        if (response.data) {
          let render_chart = false;
          // Check if the array is not empty
          if (response.data.length > 0) {
            for (const item of response.data) {
              if (item.year !== null) {
                render_chart = true;
                break;
              }
            }
          }
          setSpeciesData(response.data);
          setLoading(false);
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
    fetchActivityCount();
  }, [propertyId, startYear, endYear, selectedSpecies]);

  const horizontalLabels: string[] = Array.from(new Set(speciesData.map((item) => item.province)));
  const legendLabels: number[] = Array.from(new Set(speciesData.map((item) => item.year)))
    .filter((year) => year !== null) as number[];

  // sort the years from highest
  legendLabels.sort((a: number, b: number) => b - a);

    // Create datasets for each year using available colors
    const datasets = legendLabels.map((year, yearIndex) => {
      const backgroundColor = availableColors[yearIndex];

      // Initialize variables to keep track of repeating provinces
      let repeatingProvinceCount = 0;
      let firstRepeatingProvinceIndex = -1;

      const data = horizontalLabels.map((province, provinceIndex) => {
        const item = speciesData.find((d) => d.year === year && d.province === province);

        if (item) {
          // Check if this province has been seen before
          if (horizontalLabels.slice(0, provinceIndex).includes(province)) {
            // Find the index where this province first appeared
            const firstAppearanceIndex = horizontalLabels.indexOf(province);

            // Calculate the number of leading zeros
            const leadingZeros = provinceIndex - firstAppearanceIndex;
            return leadingZeros;
          } else {
            // This province is not repeating, reset repeatingProvinceCount and firstRepeatingProvinceIndex
            repeatingProvinceCount = 0;
            firstRepeatingProvinceIndex = -1;
            return item.count || 0;
          }
        } else {
          return 0;
        }
      });

      return {
        label: year.toString(),
        backgroundColor,
        data,
      };
    });

  // Reverse the order of datasets
  datasets.reverse();

  const data = {
    labels: horizontalLabels,
    datasets: datasets
  };

  const chartTitle = `Total count of ${selectedSpecies} per province`;

  return (
    <Grid>
      {!loading ? (
          <BarChart
              indexAxis={'x'}
              yLabel={'Count'}
              xLabel={'Provinces'}
              chartData={data}
              chartId={'species-count-per-province-chart'}
              chartTitle={chartTitle}/>
      ) : (
        <Loading containerStyle={{ minHeight: 160 }} />
      )}
    </Grid>
  );
};

export default SpeciesCountPerProvinceChart;

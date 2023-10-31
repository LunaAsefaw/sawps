import React, {useEffect, useRef, useState} from "react";
import {Box, Button, Grid, Typography} from "@mui/material";
import {useAppSelector} from "../../../app/hooks";
import {RootState} from "../../../app/store";
import PopulationTrend, {NationalTrendInterface} from "../Metrics/PopulationTrend";
import {useGetTaxonDetailQuery} from "../../../services/api";
import './index.scss';

const FETCH_GRAPH_SPECIES_LIST = '/api/species/trend-page/'

const Trends = () => {
  const selectedSpecies = useAppSelector((state: RootState) => state.SpeciesFilter.selectedSpecies)
  const propertyId = useAppSelector((state: RootState) => state.SpeciesFilter.propertyId)
  const startYear = useAppSelector((state: RootState) => state.SpeciesFilter.startYear)
  const endYear = useAppSelector((state: RootState) => state.SpeciesFilter.endYear)
  const [loading, setLoading] = useState(false)
  const [jsonDoc,setJsonDoc] = useState<NationalTrendInterface[]>()
  const [rerender, setRerender] = useState<boolean>(false)
  const contentRef = useRef(null);
  const {data: taxonDetail, isLoading: isTaxonDetailLoading, isSuccess} = useGetTaxonDetailQuery(selectedSpecies)

  // Declare errorMessage as a state variable
  const [showCharts, setShowCharts] = useState(false);

  const downloadTxtFile = () => {
    const element = document.createElement("a");
    const file = new Blob([JSON.stringify(jsonDoc)], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `${selectedSpecies}.json`;
    document.body.appendChild(element); // Required for this to work in FireFox
    element.click();
  }

  useEffect(() => {
    if (selectedSpecies) {
      setRerender(false)
      setShowCharts(true)
    } else {
      setShowCharts(false);
    }
  }, [propertyId, startYear, endYear, selectedSpecies])

  useEffect(() => {
    if (taxonDetail?.id) {
      setRerender(true)
    }
  }, [isSuccess, taxonDetail])

  return (
    <Box>
      <Box className="charts-container">

        {showCharts ? (
          <Grid container
                ref={contentRef}
                // spacing={2}
             spacing={0}
              direction="column"
              alignItems="center"
              justifyContent="center"
          >
            {selectedSpecies && rerender && (
              <Grid item xs={12} md={6}>
                <div className='species-card-container-trends' data-testid='species-card-container-trends'>
                  <div className='species-card-image-container'>
                    <img
                      src={taxonDetail.graph_icon ? taxonDetail.graph_icon : '/static/images/default-species.png'}
                      className='species-card-image'
                      data-testid='species-card-image'
                    />
                    <p className='species-card-text species-name-text'> {selectedSpecies} </p>
                    {/*<hr/>*/}
                  </div>
                  <div className='species-card-text-container'>
                    <p className='species-card-text' data-testid='species-card-population'>Total Population
                      : {taxonDetail.total_population}</p>
                    <p className='species-card-text' data-testid='species-card-total-area'>Total Area
                      : {+taxonDetail.total_area.toFixed(2)}</p>
                  </div>
                  <div className='ChartHolder'>
                    <PopulationTrend
                      selectedSpecies={selectedSpecies}
                      propertyId={propertyId}
                      startYear={startYear}
                      endYear={endYear}
                      loading={loading}
                      setLoading={setLoading}
                      setResult={setJsonDoc}
                      lineColor={'#000000'}
                      onEmptyDatasets={() => {
                      }}
                    />
                  </div>
                </div>
              </Grid>
            )}
          </Grid>) : (
          // Render message to user
          <Grid container justifyContent="center" alignItems="center" flexDirection={'column'}>
            <Grid item>
              <Typography variant="body1" color="textPrimary" style={{fontSize: '20px', fontWeight: 'bold'}}>
                Ready to explore?
              </Typography>
            </Grid>
            <Grid>
              <Typography variant="body1" color="textPrimary" style={{fontSize: '16px', fontWeight: 'bold'}}>
                Choose a species to view the data as charts.
              </Typography>
            </Grid>
          </Grid>
        )}
      </Box>
      {showCharts && (
        <Box className="download-btn-box" style={{position: 'fixed', bottom: '20px', right: '20px'}}>
          <Button
            onClick={downloadTxtFile}
            variant="contained"
            color="primary"
          >
            Download JSON Document
          </Button>
        </Box>
      )}
    </Box>
  )
}

export default Trends

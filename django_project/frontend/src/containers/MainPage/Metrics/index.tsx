import React, { useEffect, useRef, useState } from "react";
import { Box, Button, Grid, Typography, Modal } from "@mui/material";
import DensityBarChart from "./DensityBarChart";
import PopulationCategoryChart from "./PopulationCategoryChart";
import { useAppSelector } from "../../../app/hooks";
import { RootState } from "../../../app/store";
import PropertyAvailableBarChart from "./PropertyAvailable";
import PropertyTypeBarChart from "./PropertyType";
import AgeGroupBarChart from "./AgeGroupBarChart";
import AreaAvailableLineChart from "./AreaAvailableLineChart";
import axios from "axios";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import SpeciesCountPerProvinceChart from "./SpeciesCountPerProvinceChart";
import SpeciesCountAsPercentage from "./SpeciesCountAsPercentage";
import TotalCountPerActivity from "./TotalCountPerActivity";
import ActivityCountAsPercentage from "./ActivityCountAsPercentage";
import PopulationEstimateCategoryCount from "./PopulationEstimateCategory";
import PopulationEstimateAsPercentage from "./PopulationEstimateCategoryAsPercentage";
import PopulationTrend from "./PopulationTrend";
import {
    useGetActivityAsObjQuery,
    useGetUserInfoQuery,
} from "../../../services/api";
import Topper from "../Data/Topper";
import Loading from "../../../components/Loading";


const FETCH_POPULATION_AGE_GROUP = '/api/population-per-age-group/'
const FETCH_ACTIVITY_PERCENTAGE_URL = '/api/activity-percentage/'
const FETCH_ACTIVITY_TOTAL_COUNT = '/api/total-count-per-activity/'
const FETCH_PROPERTY_POPULATION_SPECIES = '/api/total-area-vs-available-area/'

const Metrics = () => {
    const selectedSpecies = useAppSelector((state: RootState) => state.SpeciesFilter.selectedSpecies)
    const activityId = useAppSelector((state: RootState) => state.SpeciesFilter.activityId)
    const propertyId = useAppSelector((state: RootState) => state.SpeciesFilter.propertyId)
    const startYear = useAppSelector((state: RootState) => state.SpeciesFilter.startYear)
    const endYear = useAppSelector((state: RootState) => state.SpeciesFilter.endYear)
    const [loading, setLoading] = useState(false)
    const [activityData, setActivityData] = useState([])
    const [activityType, setActivityType] = useState({})
    const [totalCoutData, setTotalCountData] = useState([])
    const [ageGroupData, setAgeGroupData] = useState([])
    const [open, setOpen] = useState(false)
    const labels = Object.keys(activityType);
    const totalCountLabel = labels.filter(item => item !== "Base population");
    const [areaData, setAreaData] = useState([])

    const [densityData, setDensityData] = useState([])
    const [speciesData, setSpeciesData] = useState([])
    const contentRef = useRef(null);

    // Declare errorMessage as a state variable
    const [showCharts, setShowCharts] = useState(false);

    const [hasEmptyPopulationTrend, setHasEmptyPopulationTrend] = useState(true);
    const [hasEmptyPopulationCategory, setHasEmptyPopulationCategory] = useState(true);
    const [hasEmptyPropertyType, setHasEmptyPropertyType] = useState(true);
    const [hasEmptyDensity, setHasEmptyDensity] = useState(true);
    const [hasEmptyProvinceCount, setHasEmptyProvinceCount] = useState(true);
    const [hasEmptyProvinceCountPercentage, setHasEmptyProvinceCountPercentage] = useState(true);
    const [hasEmptyTotalCountPerActivity, setHasEmptyTotalCountPerActivity] = useState(true);
    const [hasEmptyPopulationEstimateCategoryCount, setHasEmptyPopulationEstimateCategoryCount] = useState(true);
    const [hasEmptyPopulationEstimateCategoryCountPercentage, setHasEmptyhasEmptyPopulationEstimateCategoryCountPercentage] = useState(true);
    const [hasEmptyPropertyAvailable, setHasEmptyPropertyAvailable] = useState(true);
    const [hasEmptyAreaAvailable, setHasEmptyAreaAvailable] = useState(true);

    const { data: userInfoData, isLoading, isSuccess } = useGetUserInfoQuery();
    const [userPermissions, setUserPermissions] = useState([]);

    const {
        data: activityList,
        isLoading: isActivityLoading,
        isSuccess: isActivitySuccess
    } = useGetActivityAsObjQuery()

    let activityParams = activityId;
    if (activityList) {
        activityParams = activityId.split(',').length === activityList.length ? 'all': activityId
    }

    useEffect(() => {
        if (isSuccess) {
            // Extract user permissions
            setUserPermissions(userInfoData?.user_permissions.map((permission) => permission.toLowerCase().replace(/\s/g, '')) || []);
        }
    }, [isSuccess, userInfoData]);

    // Pass callback functions to each child component for the specific type
    const handleEmptyPopulationTrend = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyPopulationTrend(isEmpty);
    };
    const handleEmptyPopulationCategory = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyPopulationCategory(isEmpty);
    };
    const handleEmptyPropertyType = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyPropertyType(isEmpty);
    };
    const handleEmptyDensity = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyDensity(isEmpty);
    };
    const handleEmptyPropertyAvailable = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyPropertyAvailable(isEmpty);
    };
    const handleEmptyProvinceCount = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyProvinceCount(isEmpty);
    };
    const handleEmptyProvinceCountPercentage = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyProvinceCountPercentage(isEmpty);
    };
    const handleEmptyTotalCountPerActivity = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyTotalCountPerActivity(isEmpty);
    };
    const handleEmptyTopulationEstimateCategoryCount = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyPopulationEstimateCategoryCount(isEmpty);
    };
    const handleEmptyPopulationEstimateCategoryCountPercentage = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyhasEmptyPopulationEstimateCategoryCountPercentage(isEmpty);
    };
    const handleHasEmptyAreaAvailable = (isEmpty: boolean | ((prevState: boolean) => boolean)) => {
        setHasEmptyAreaAvailable(isEmpty);
    };

    const fetchActivityPercentageData = () => {
        setLoading(true)
        axios.get(`${FETCH_ACTIVITY_PERCENTAGE_URL}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&activity=${activityParams}&property=${propertyId}`).then((response) => {
            setLoading(false)
            if (response.data) {
                setActivityData(response.data.data)
                setActivityType(response.data.activity_colours)
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }

    const fetchActivityTotalCount = () => {
        setLoading(true)
        axios.get(`${FETCH_ACTIVITY_TOTAL_COUNT}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&activity=${activityParams}&property=${propertyId}`).then((response) => {
            setLoading(false)
            if (response.data) {
                setTotalCountData(response.data)
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }

    const fetchPopulationAgeGroupData = () => {
        setLoading(true)
        axios.get(`${FETCH_POPULATION_AGE_GROUP}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`).then((response) => {
            setLoading(false)
            if (response.data) {
                console.log('fetched data: ',response.data)
                setAgeGroupData(response.data)
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }


    const fetchAreaAvailableLineData = () => {
        setLoading(true)
        axios.get(`${FETCH_PROPERTY_POPULATION_SPECIES}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`).then((response) => {
            setLoading(false)
            if (response.data) {
                setAreaData(response.data)
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }

    useEffect(() => {
        if(selectedSpecies){
            setShowCharts(true)
            fetchActivityPercentageData();
            fetchActivityTotalCount();
            fetchPopulationAgeGroupData();
            fetchAreaAvailableLineData();
        }else {
            setShowCharts(false);
        }
        // allow rerender
        setHasEmptyPopulationTrend(true)
        setHasEmptyPopulationCategory(true)
        setHasEmptyPropertyType(true)
        setHasEmptyDensity(true)
        setHasEmptyPropertyAvailable(true)
        setHasEmptyProvinceCountPercentage(true)
        setHasEmptyTotalCountPerActivity(true)
        setHasEmptyPopulationEstimateCategoryCount(true)
        setHasEmptyhasEmptyPopulationEstimateCategoryCountPercentage(true)
        handleHasEmptyAreaAvailable(true)


    }, [propertyId, startYear, endYear, selectedSpecies])

    // downloads all charts rendered on page
    const handleDownloadPdf = async () => {
        setOpen(true)
        const data = document.getElementById('charts-container');
        html2canvas(data, {scale: 2}).then((canvas:any) => {
          const imgWidth = 208;
          const pageHeight = 295;
          const imgHeight = (canvas.height * imgWidth) / canvas.width;
          let heightLeft = imgHeight;
          let position = 0;
          heightLeft -= pageHeight;
          const doc = new jsPDF('p', 'mm');
          doc.setFillColor('245');
          doc.addImage(canvas, 'PNG', 0, position, imgWidth, imgHeight, '', 'FAST');
          while (heightLeft >= 0) {
            position = heightLeft - imgHeight;
            doc.addPage();
            doc.addImage(canvas, 'PNG', 0, position, imgWidth, imgHeight, '', 'FAST');
            heightLeft -= pageHeight;
          }
          setOpen(false)
          doc.save(`${selectedSpecies} - metrics.pdf`);
        });
    }

    type Constants = {
        [key: string]: boolean;
    };

    // TODO: Improve this, we don't need constants here, we can simply check the permissions directly
    const constants: Constants = {
        canViewPopulationTrend: false,
        canViewPopulationCategory: false,
        canViewPropertyType: false,
        canViewDensityBar: false,
        canViewPropertyAvailable: false,
        canViewAgeGroup: false,
        canViewAreaAvailable: false,
        canViewProvinceSpeciesCount: false,
        canViewProvinceSpeciesCountAsPercentage: false,
        canViewTotalCount: false,
        canViewCountAsPercentage: false,
        canViewPopulationEstimate: false,
        canViewPopulationEstimateAsPercentage: false,
    };


    function updateConstants(userPermissions: string[], constants: Constants) {
        for (const permission of userPermissions) {
            for (const key in constants) {
              if (constants.hasOwnProperty(key) && key.toLowerCase() === permission) {
                constants[key] = true;
              }
            }
        }
    }

    // Example usage:
    // userPermissions is an array of permission strings
    // Example: ['CanViewPopulationCategory', 'CanEditData', ...]

    // Call the function with user permissions
    updateConstants(userPermissions, constants);


    return (
        <Box>
            <Box>
                <Modal
                  id={'pdf-modal'}
                  open={open}
                >
                    <Box>
                        <Typography variant="h6" component="h2">
                            Generating PDF!
                        </Typography>
                        <Typography id="modal-modal-description" sx={{mt: 2}}>
                            This might take a while.
                        </Typography>
                        <Loading />
                    </Box>
                </Modal>
            </Box>
            <Box className="charts-container" id={'charts-container'}>

                {showCharts ? (
                        <>
                        <Topper></Topper>
                        <Grid container spacing={1} ref={contentRef}>
                            {
                            constants.canViewPopulationTrend &&
                            selectedSpecies &&
                            hasEmptyPopulationTrend && (
                                <Grid item xs={12} md={12} lg={6}>
                                    <PopulationTrend
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        loading={loading}
                                        setLoading={setLoading}
                                        onEmptyDatasets={handleEmptyPopulationTrend}
                                    />
                                </Grid>
                            )}


                            {
                            constants.canViewPopulationCategory &&
                            selectedSpecies &&
                            hasEmptyPopulationCategory && (
                                <Grid item xs={12} md={12} lg={6}>
                                    <PopulationCategoryChart
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        onEmptyDatasets={handleEmptyPopulationCategory}
                                    />
                                </Grid>
                            )}

                             {
                             constants.canViewPropertyType &&
                             hasEmptyPropertyType && (
                                <Grid item xs={12} md={12} lg={6}>
                                    <PropertyTypeBarChart
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        loading={loading}
                                        setLoading={setLoading}
                                        onEmptyDatasets={handleEmptyPropertyType}
                                    />
                                </Grid>
                            )}


                            {
                            constants.canViewDensityBar &&
                            selectedSpecies &&
                            hasEmptyDensity && (
                                <Grid item xs={12} md={12} lg={6}>
                                    <DensityBarChart
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        loading={loading}
                                        setLoading={setLoading}
                                        densityData={densityData}
                                        setDensityData={setDensityData}
                                        onEmptyDatasets={handleEmptyDensity}
                                    />
                                </Grid>
                            )}


                            {
                            constants.canViewPropertyAvailable &&
                            selectedSpecies &&
                            hasEmptyPropertyAvailable && (
                                <Grid item xs={12} md={12} lg={6}>
                                    <PropertyAvailableBarChart
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        loading={loading}
                                        activity={activityParams}
                                        setLoading={setLoading}
                                        onEmptyDatasets={handleEmptyPropertyAvailable}
                                    />
                                </Grid>
                            )}


                            {
                            userInfoData?.user_permissions.includes('Can view age group') &&
                            ageGroupData.map((data) => (
                                <Grid item key={data.id} xs={12} md={12} lg={6}>
                                    <AgeGroupBarChart
                                        loading={loading}
                                        ageGroupData={data?.age_group}
                                        icon={data?.graph_icon}
                                        colour={data?.colour}
                                        name={data?.common_name_varbatim}
                                    />
                                </Grid>
                            ))}


                            {
                            constants.canViewAreaAvailable &&
                            hasEmptyAreaAvailable && areaData.map((data, index) => (
                                <Grid item key={index} xs={12} md={12} lg={6}>
                                    {data?.area?.owned_species ? (
                                        <AreaAvailableLineChart
                                            selectedSpecies={selectedSpecies}
                                            propertyId={propertyId}
                                            startYear={startYear}
                                            endYear={endYear}
                                            loading={loading}
                                            areaData={data?.area?.owned_species}
                                            species_name={data?.common_name_varbatim}
                                            onEmptyDatasets={handleHasEmptyAreaAvailable}
                                        />
                                    ) : null}
                                </Grid>
                            ))}


                            {
                            constants.canViewProvinceSpeciesCount &&
                            selectedSpecies &&
                            hasEmptyProvinceCount && (
                                <Grid item xs={12} md={12} lg={6}>
                                    <SpeciesCountPerProvinceChart
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        loading={loading}
                                        setLoading={setLoading}
                                        onEmptyDatasets={handleEmptyProvinceCount}
                                    />
                                </Grid>
                            )}


                            {
                            constants.canViewProvinceSpeciesCountAsPercentage &&
                            selectedSpecies &&
                            (
                                <Grid item xs={12} md={12} lg={6}>
                                    <SpeciesCountAsPercentage
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        loading={loading}
                                        setLoading={setLoading}
                                        activityData={activityData}
                                        onEmptyDatasets={handleEmptyProvinceCountPercentage}
                                    />
                                </Grid>
                            )}


                            {
                            constants.canViewTotalCount &&
                            selectedSpecies && (
                                <Grid item xs={12} md={12} lg={6}>
                                    <TotalCountPerActivity
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        loading={loading}
                                        activityData={totalCoutData}
                                        onEmptyDatasets={handleEmptyTotalCountPerActivity}
                                    />
                                </Grid>
                            )}


                            {
                            userInfoData?.user_permissions.includes('Can view count as percentage') &&
                            selectedSpecies &&
                            totalCoutData.length > 0 && (
                                <Grid item xs={12} md={12} lg={6}
                                >
                                    <ActivityCountAsPercentage
                                        selectedSpecies={selectedSpecies}
                                        startYear={startYear}
                                        endYear={endYear}
                                        loading={loading}
                                        activityData={totalCoutData}
                                    />
                                </Grid>
                                )}


                            {
                            constants.canViewPopulationEstimate &&
                            selectedSpecies &&
                            hasEmptyPopulationEstimateCategoryCount && (
                                <Grid item xs={12} md={12} lg={6}>
                                    <PopulationEstimateCategoryCount
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        activityData={activityData}
                                        onEmptyDatasets={handleEmptyTopulationEstimateCategoryCount}
                                    />
                                </Grid>
                                )}


                            {
                            constants.canViewPopulationEstimateAsPercentage &&
                            selectedSpecies &&
                            hasEmptyPopulationEstimateCategoryCountPercentage && (
                                <Grid item xs={12} md={12} lg={6}>
                                    <PopulationEstimateAsPercentage
                                        selectedSpecies={selectedSpecies}
                                        propertyId={propertyId}
                                        startYear={startYear}
                                        endYear={endYear}
                                        loading={loading}
                                        setLoading={setLoading}
                                        activityData={activityData}
                                        onEmptyDatasets={handleEmptyPopulationEstimateCategoryCountPercentage}
                                    />
                                </Grid>
                            )}

                    </Grid>
                        </>
                ): (
                    // Render message to user
                    <Grid container justifyContent="center" alignItems="center" flexDirection={'column'}>
                        <Grid item>
                            <Typography variant="body1" color="textPrimary" style={{ fontSize: '20px', fontWeight: 'bold' }}>
                                Ready to explore?
                            </Typography>
                        </Grid>
                        <Grid>
                            <Typography variant="body1" color="textPrimary" style={{ fontSize: '16px', fontWeight: 'bold' }}>
                                Choose a species to view the data as charts.
                            </Typography>
                        </Grid>
                    </Grid>
                )}
            </Box>
            {/* for decision makers only */}
            {/* {userRole === 'decision maker' && (
                <GenerateChartImages />
            )} */}
            {showCharts && (
                <Box className="download-btn-box" style={{ position: 'fixed', bottom: '20px', right: '20px' }}>
                    <Button onClick={handleDownloadPdf} variant="contained" color="primary">
                        Download data visualizations
                    </Button>
                </Box>
            )}

        </Box>
    );
};

export default Metrics;

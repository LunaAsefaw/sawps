import React, {useEffect, useState} from 'react';
import {v4 as uuidv4} from 'uuid';
import axios from "axios";
import {
    Autocomplete,
    Box,
    TextField,
    Typography
} from '@mui/material';
import List from '@mui/material/List';
import CircularProgress from '@mui/material/CircularProgress';
import InputAdornment from '@mui/material/InputAdornment';
import {debounce} from '@mui/material/utils';
import SearchIcon from '@mui/icons-material/Search';
import {RootState} from '../../../app/store';
import {useAppDispatch, useAppSelector} from '../../../app/hooks';
import Slider from '@mui/material/Slider';
import Loading from '../../../components/Loading';
import {
    selectedActivityId,
    selectedOrganisationId,
    selectedPropertyId,
    setEndYear,
    setSelectedInfoList,
    setSpatialFilterValues,
    selectedOrganisationName,
    selectedPropertyName,
    setStartYear,
    toggleSpecies,
    selectedActivityName
} from '../../../reducers/SpeciesFilter';
import './index.scss';
import {MapEvents} from '../../../models/Map';
import {triggerMapEvent} from '../../../reducers/MapState';
import SpatialFilter from "./SpatialFilter";
import {
    useGetUserInfoQuery,
    useGetActivityQuery,
    useGetOrganisationQuery,
    useGetPropertyQuery,
    useGetSpeciesQuery,
    Organisation,
    Activity,
    Property
} from "../../../services/api";
import {isMapDisplayed} from "../../../utils/Helpers";
import Button from "@mui/material/Button";
import {AutoCompleteCheckbox} from "../../../components/SideBar/index";

const yearRangeStart = 1960;
const yearRangeEnd = new Date().getFullYear();
const FETCH_PROPERTY_LIST_URL = '/api/property/list/'
const SEARCH_PROPERTY_URL = '/api/property/search'
const FETCH_PROPERTY_DETAIL_URL = '/api/property/detail/'

interface SearchPropertyResult {
    name: string;
    bbox: any;
    id: string;
    type: string;
    fclass?: string;
}

function Filter(props: any) {
    const dispatch = useAppDispatch()
    const startYear = useAppSelector((state: RootState) => state.SpeciesFilter.startYear)
    const endYear = useAppSelector((state: RootState) => state.SpeciesFilter.endYear)
    const [loading, setLoading] = useState(false)
    const [selectedSpecies, setSelectedSpecies] = useState<string>('');
    const [selectedProperty, setSelectedProperty] = useState([]);
    const [selectAllProperty, setSelectAllProperty] = useState(true);
    const [selectedActivity, setSelectedActivity] = useState<number[]>([]);
    const [selectAllActivity, setSelectAllActivity] = useState<boolean>(true);
    const [localStartYear, setLocalStartYear] = useState(startYear);
    const [localEndYear, setLocalEndYear] = useState(endYear);
    const [selectedInfo, setSelectedInfo] = useState<string[]>(['Species report']);
    const [selectAllInfo, setSelectAllInfo] = useState(null);
    const [searchOpen, setSearchOpen] = useState(false)
    const [searchInputValue, setSearchInputValue] = useState<string>('')
    const [searchResults, setSearchResults] = useState<SearchPropertyResult[]>([])
    const [selectedOrganisation, setSelectedOrganisation] = useState([]);
    const [selectAllOrganisation, setSelectAllOrganisation] = useState(true);
    const [tab, setTab] = useState<string>('')
    const [searchSpeciesList, setSearchSpeciesList] = useState([])
    const [nominatimResults, setNominatimResults] = useState([]);
    const [allowPropertiesSelection, setPropertiesSelection] = useState(false)
    const [allowOrganisationSelection, setOrganisationSelection] = useState(false)
    const { data: userInfoData, isLoading, isSuccess } = useGetUserInfoQuery()
    const {
        data: organisationList,
        isLoading: isOrganisationLoading,
        isSuccess: isOrganisationSuccess
    } = useGetOrganisationQuery()
    const {
        data: activityList,
        isLoading: isActivityLoading,
        isSuccess: isActivitySuccess
    } = useGetActivityQuery()
    const {
        data: propertyList,
        isLoading: isPropertyLoading,
        isSuccess: isPropertySuccess
    } = useGetPropertyQuery(selectedOrganisation.join(','))
    const {
        data: SpeciesFilterList,
        isLoading: isSpeciesLoading,
        isSuccess: isSpeciesSuccess
    } = useGetSpeciesQuery(selectedOrganisation.join(','))

    type Information = {
        id?: string,
        name?: string
    }
    let informationList: Information[] = []

    const roleExists = (role: string) => {
        if (!userInfoData || !userInfoData.user_roles) return false;
        return userInfoData.user_roles.includes(role);
    }

    if (userInfoData) {
        informationList = [
            {
                id: "Activity report",
                name: "Activity report",
            },
            {
                id: "Property report",
                name: "Property report"
            },
            {
                id: "Species report",
                name: "Species report"
            },
        ]

        const provinceReportRoles = [
            'National data scientist',
            'Regional data scientist',
            'Organisation member',
            'Organisation manager'
        ]
        if (provinceReportRoles.some(roleExists)) {
            informationList.push({
                id: "Province report",
                name: "Province report"
            })
        }

        const samplingReportRoles = [
            'National data consumer',
            'National data scientist'
        ]
        if (samplingReportRoles.some(roleExists)) {
            informationList.push({
                id: "Sampling report",
                name: "Sampling report"
            })
        }
        informationList = informationList.sort((a, b) => a.id > b.id ? 1 : -1)

    }

    // Select all organisations by default
    useEffect(() => {
        if (organisationList) {
            setSelectedOrganisation(organisationList.map((organisation: Organisation) => organisation.id))
        }
    }, [organisationList]);

    // Select all properties by default
    useEffect(() => {
        if (propertyList) {
            if (selectedOrganisation.length > 0) {
                setSelectedProperty(propertyList.map(property => property.id))
            } else {
                setSelectedProperty([])
            }
        }
    }, [propertyList]);

    // Select all activities by default
    useEffect(() => {
        if (activityList) {
            setSelectedActivity(activityList.map((activity: Activity) => activity.id))
        }
    }, [activityList]);

    // intial map state vars for zoom out
    const center = [25.86, -28.52]; // Center point in backend
    const width = 10;
    const height = 10;

     // Calculate the bounding box
    const halfWidth = width / 2;
    const halfHeight = height / 2;
    const boundingBox = [
        center[0] - halfWidth,
        center[1] - halfHeight,
        center[0] + halfWidth,
        center[1] + halfHeight,
    ];


    const handleInputChange = (value: string) => {
        setSearchInputValue(value);

        // Update searchResults with the results from existing search
        searchProperty({ input: value }, (results) => {
          if (results) {
            setSearchResults(results.data as SearchPropertyResult[]);
          } else {
            setSearchResults([]);
          }
        });

        // Perform Nominatim-based search and update nominatimResults
        performNominatimSearch(value);
    };

    const performNominatimSearch = async (value: string) => {
        try {
            setNominatimResults([]);
            const encodedValue = encodeURIComponent(value);
            const response = await axios.get(
              `https://nominatim.openstreetmap.org/search?format=json&q=${encodedValue}&countrycodes=AFR`
            );
            const updatedNominatimResults = response.data
            .filter((result: { display_name: string | string[]; }) => result.display_name.includes("South Africa"))
            .map((result: { place_id: any; }, index: any) => ({
                ...result,
                key: `nominatim_${result.place_id}`,
            }));

            setNominatimResults(updatedNominatimResults);

        } catch (error) {
          console.error('Error fetching Nominatim address suggestions:', error);
        }
      };

    useEffect(() => {
        const pathname = window.location.pathname.replace(/\//g, '');
        setTab(pathname)
    }, [window.location.pathname])

    const handleChange = (event: any, newValue: number | number[]) => {
        if (Array.isArray(newValue)) {
            setLocalStartYear((newValue[0]))
            dispatch(setStartYear(newValue[0]));
            setLocalEndYear((newValue[1]))
            dispatch(setEndYear(newValue[1]));
        }
    };

    const handleSelectedSpecies = (value: string) => {
        setSelectedSpecies(value);
    };

    useEffect(() => {
        dispatch(toggleSpecies(selectedSpecies));
    }, [selectedSpecies])

    useEffect(() => {
        dispatch(toggleSpecies(selectedSpecies));
    }, [selectedSpecies])

    useEffect(() => {
        const values = selectedInfo.join(',')
        dispatch(setSelectedInfoList(values));
    }, [selectedInfo])

    useEffect(() => {
        if (selectAllInfo) {
            setSelectedInfo(informationList.map((info) => info.id));
        } else if (selectAllInfo === false) {
            setSelectedInfo([]);
        }
    }, [selectAllInfo])

    const mergeBoundingBoxes = (boundingBoxes: number[][]): number[] => {
        let minLeft: number = 180;
        let minBottom: number = 90;
        let maxRight: number = -180;
        let maxTop: number = -90;

        boundingBoxes.forEach(([left, bottom, right, top]) => {
          if (left < minLeft) minLeft = left;
          if (bottom < minBottom) minBottom = bottom;
          if (right > maxRight) maxRight = right;
          if (top > maxTop) maxTop = top;
        });

        return [minLeft, minBottom, maxRight, maxTop];
      };


    const zoomToCombinedBoundingBox = async (propertyIds: number[]) => {

        try {
          const propertyBoundingBoxes: number[][] = [];

          // Fetch and collect bounding boxes for each property
          await Promise.all(
            propertyIds.map(async (propertyId) => {
              const response = await axios.get(`${FETCH_PROPERTY_DETAIL_URL}${propertyId}/`);
              if (response.data && response.data.bbox && response.data.bbox.length === 4) {
                propertyBoundingBoxes.push(response.data.bbox);
              }
            })
          );

          if (propertyBoundingBoxes.length > 0) {
            // Merge the collected bounding boxes
            const combinedBoundingBox = mergeBoundingBoxes(propertyBoundingBoxes);


            adjustMapToBoundingBox(combinedBoundingBox)
          } else {
            console.error('No valid bounding boxes found for selected properties.');
          }

          setLoading(false);
        } catch (error) {
          setLoading(false);
          console.error(error);
        }
      };

      const adjustMapToBoundingBox = (boundingBox: any[]) => {
        dispatch(
            triggerMapEvent({
                id: uuidv4(),
                name: MapEvents.PROPERTY_SELECTED,
                date: Date.now(),
                payload: boundingBox.map(String),
            })
        );
      };


    // Handle selecting all properties
    const handleSelectAllProperty = () => {
        if (propertyList) {
            let propertyIds = selectAllProperty ? propertyList.map((property: Property) => property.id) : []
            setSelectedProperty(propertyIds);
            if (propertyIds.length > 0) {
                zoomToCombinedBoundingBox(propertyIds);
            } else {
                adjustMapToBoundingBox(boundingBox)
            }
        }
    };

    useEffect(() => {
        handleSelectAllProperty()
    }, [selectAllProperty])

    useEffect(() => {
        if (propertyList) {
            dispatch(selectedPropertyId(selectedProperty.join(',')));
            const selectedPropertyNames = propertyList.filter(
              propertyObj => selectedProperty.includes(propertyObj.id)
            ).map(propertyObj => propertyObj.name)
            dispatch(selectedPropertyName(selectedPropertyNames.length > 0 ? selectedPropertyNames.join(', ') : ''));
        }
    }, [selectedProperty])

    // Handle selecting all organisation
    const handleSelectAllOrganisation = () => {
        if (organisationList) {
            let organisationIds = selectAllOrganisation ? organisationList.map((organisation: Organisation) => organisation.id) : []
            setSelectedOrganisation(organisationIds);
        }
    };

    useEffect(() => {
        handleSelectAllOrganisation()
    }, [selectAllOrganisation])

    useEffect(() => {
        if (organisationList) {
            dispatch(selectedOrganisationId(selectedOrganisation.join(',')))
            const selectedOrganisationNames = organisationList.filter(
              organisationObj => selectedOrganisation.includes(organisationObj.id)
            ).map(organisationObj => organisationObj.name)
            dispatch(selectedOrganisationName(selectedOrganisationNames.length > 0 ? selectedOrganisationNames.join(', ') : ''));
        }
    }, [selectedOrganisation])

    useEffect(() => {
        if (activityList) {
            dispatch(selectedActivityId(selectedActivity.join(',')));
            const selectedActivityNames = activityList.filter(
              activityObj => selectedActivity.includes(activityObj.id)
            ).map(activityObj => activityObj.name)
            dispatch(selectedActivityName(selectedActivityNames.length > 0 ? selectedActivityNames.join(',') : ''));
        }
    }, [selectedActivity])

    // Handle selecting all activities
    const handleSelectAllActivity = () => {
        if (activityList) {
            let activityIds = selectAllActivity ? activityList.map((activity: Activity) => activity.id) : []
            setSelectedActivity(activityIds);
        }
    };

    useEffect(() => {
        handleSelectAllActivity()
    }, [selectAllActivity])

    const handleStartYearChange = (value: string) => {
        const newValue = parseInt(value, 10);
        setLocalStartYear(newValue);
        if (newValue < yearRangeStart || newValue > yearRangeEnd) {
            setTimeout(() => {
                setLocalStartYear(yearRangeStart)
                dispatch(setStartYear(yearRangeStart));
            }, 3000);
        } else {
            dispatch(setStartYear(newValue));
        }
    }

    const handleEndYearChange = (value: string) => {
        const newValue = parseInt(value, 10);
        setLocalEndYear(newValue);
        if (newValue > yearRangeEnd || newValue < yearRangeStart) {
            setTimeout(() => {
                setLocalEndYear(yearRangeEnd);
                dispatch(setEndYear(yearRangeEnd));
            }, 3000);
        } else {
            dispatch(setEndYear(newValue));
        }
    }

    const searchProperty = React.useMemo(
        () =>
            debounce(
                (
                    request: { input: string },
                    callback: (results?: any) => void,
                ) => {
                    let _queryParam = `search_text=${request.input}`
                    axios.get(`${SEARCH_PROPERTY_URL}?${_queryParam}`).then(
                        response => {
                            callback(response)
                        }
                    ).catch(error => {
                        console.log('Failed search property ', error)
                        callback(null)
                    })
                },
                400,
            ),
        [],
    )

    const clearFilter = () => {
        setSelectAllProperty(false)
        setSelectAllOrganisation(false)
        setSelectedSpecies('')
        setSelectAllActivity(false)
        setSelectAllInfo(false)
        setLocalStartYear(yearRangeStart)
        setLocalEndYear(yearRangeEnd)
        dispatch(setStartYear(yearRangeStart));
        dispatch(setEndYear(yearRangeEnd));
    }

    useEffect(() => {
        let active = true;
        if (searchInputValue.length <= 1) {
            setSearchResults([])
            return undefined;
        }
        searchProperty({ input: searchInputValue }, (results: any) => {
            if (active) {
                if (results) {
                    setSearchResults(results.data as SearchPropertyResult[])
                } else {
                    setSearchResults([])
                }
            }
        })
        return () => {
            active = false
        };
    }, [searchInputValue, searchProperty])

    useEffect(() => {
        setSearchOpen(searchInputValue.length > 1)
        if (searchInputValue.length <= 1) {
            setSearchResults([])
        }
    }, [searchInputValue])


    useEffect(() => {
        if (SpeciesFilterList) {
            const sList: any = []
            SpeciesFilterList.map((item: any) => {
                sList.push(item.scientific_name)
            })
            if (selectedOrganisation.length === 0) {
                setSearchSpeciesList([])
            } else {
                setSearchSpeciesList(sList)
            }
        }
    }, [SpeciesFilterList])

    useEffect(() => {
        if (!isSuccess) return;

        const userRoles = userInfoData.user_roles
        if (userRoles.length === 0) return;

        // TODO : Update to use permissions
        const allowedRoles = new Set(["National data scientist", "Regional data scientist", "Super user"]);

        if(
            userRoles.some(userRole => allowedRoles.has(userRole))
        ){
            setOrganisationSelection(true)
            setPropertiesSelection(true)
            return;
        }

        const organisationRoles = new Set(['Organisation member', 'Organisation manager'])
        if (
            userRoles.some(userRole => organisationRoles.has(userRole))
        ) {
          setPropertiesSelection(true)
          setOrganisationSelection(false)
        }
    }, [isSuccess, userInfoData]);

    return (
        <Box sx={{position: 'relative'}}>
            {isLoading ?
                <div
                    className='sidepanel-loading-container'
                >
                    <CircularProgress color="inherit" />
                </div> : null }
            <Box className='sidebarBox' style={{ marginTop: 10 }}>
                <Box className='clear-button-container'>
                    <Button onClick={clearFilter}>Clear All</Button>
                </Box>
                {isMapDisplayed() && (
                <Box style={{marginTop: '5%', marginBottom: '10%'}} >
                    <Box className="sidebarBoxHeading" style={{ display: 'flex', alignItems: 'center', marginBottom: '15px'}}>
                        <SearchIcon
                            style={{
                                color: '#70B276',
                            }}
                        />
                        <Typography color='#75B37A' fontSize='medium'>Search place</Typography>
                    </Box>
                    <Autocomplete
                        disablePortal={false}
                        id="search-property-autocomplete"
                        open={searchOpen}
                        onOpen={() => setSearchOpen(searchInputValue.length > 1)}
                        onClose={() => setSearchOpen(false)}
                        options={[
                            ...searchResults.map((result) => ({
                            ...result,
                            key: `searchResult_${result.id}`,
                            })),
                            ...nominatimResults.map((result) => ({
                            ...result,
                            key: `nominatim_${result.place_id}`,
                            display_name: result.display_name,
                            })),
                        ]}
                        getOptionLabel={(option) => {
                            if (option.fclass) {
                            return `${option.name} (${option.fclass})`;
                            } else if (option.display_name) {
                            return option.display_name;
                            }
                            return ''; // Return an empty string if neither fclass nor display_name exists
                        }}
                        renderInput={(params) => (
                            <TextField
                            variant="outlined"
                            placeholder="Search place"
                            {...params}
                            InputProps={{
                                ...params.InputProps,
                                endAdornment: (
                                <InputAdornment position="end">
                                    <SearchIcon />
                                </InputAdornment>
                                ),
                            }}
                            />
                        )}
                        onChange={(event, newValue) => {
                            if (newValue && newValue.bbox && newValue.bbox.length === 4) {
                            // trigger zoom to property
                            let _bbox = newValue.bbox.map(String);
                            dispatch(triggerMapEvent({
                                'id': uuidv4(),
                                'name': MapEvents.ZOOM_INTO_PROPERTY,
                                'date': Date.now(),
                                'payload': _bbox
                            }));
                            setSearchInputValue('');
                            }
                            else if (newValue && newValue.boundingbox && newValue.boundingbox.length === 4) {
                                let _bbox = newValue.boundingbox.map(String);
                                dispatch(triggerMapEvent({
                                    'id': uuidv4(),
                                    'name': MapEvents.ZOOM_INTO_PROPERTY,
                                    'date': Date.now(),
                                    'payload': _bbox
                                }));
                                setSearchInputValue('');
                            }
                        }}

                        onInputChange={(event, newInputValue) => {
                            setSearchInputValue(newInputValue);
                            handleInputChange(newInputValue);
                        }}
                        filterOptions={(x) => x}
                        isOptionEqualToValue={(option, value) => option.id === value.id}
                    />
                </Box>
                )}
                <Box className='sidebarBoxHeading'>
                    <img src="/static/images/species/Elephant.svg" alt='species image' />
                    <Typography color='#75B37A' fontSize='medium'>Species</Typography>
                </Box>
                <List className='ListItem' component="nav" aria-label="">
                    {loading || isSpeciesLoading ? <Loading /> :
                        (
                            <Autocomplete
                                id="combo-box-demo"
                                disableClearable={true}
                                value={selectedSpecies}
                                options={searchSpeciesList}
                                sx={{ width: '100%' }}
                                onChange={(event, value) => handleSelectedSpecies(value)}
                                renderInput={(params) => <TextField {...params} placeholder="Select" />}
                            />
                        )
                    }
                </List>
                {tab === 'reports' &&
                    <Box>
                        <Box className='sidebarBoxHeading'>
                            <img src="/static/images/Information.svg" alt='Info image' />
                            <Typography color='#75B37A' fontSize='medium'>Report Type</Typography>
                        </Box>
                        <List className='ListItem' component="nav" aria-label="">
                            {loading ? <Loading /> :
                              (
                                <AutoCompleteCheckbox
                                    options={informationList}
                                    selectedOption={selectedInfo}
                                    singleTerm={'Report'}
                                    pluralTerms={'Reports'}
                                    selectAllFlag={selectAllInfo}
                                    setSelectAll={(val) => setSelectAllInfo(val)}
                                    setSelectedOption={setSelectedInfo}
                                  />
                              )
                            }
                        </List>
                    </Box>
                }
                 {tab !== 'trends' &&
                   <Box>
                        <Box className='sidebarBoxHeading'>
                            <img src="/static/images/Activity.svg" alt='Property image' />
                            <Typography color='#75B37A' fontSize='medium'>Activity</Typography>
                        </Box>
                        <List className='ListItem' component="nav" aria-label="">
                            {loading || isActivityLoading ? <Loading /> :
                                (
                                    <AutoCompleteCheckbox
                                        options={activityList}
                                        selectedOption={selectedActivity}
                                        singleTerm={'Activity'}
                                        pluralTerms={'Activities'}
                                        selectAllFlag={selectAllActivity}
                                        setSelectAll={(val) => {
                                            setSelectAllActivity(val)
                                        }}
                                        setSelectedOption={setSelectedActivity}
                                      />
                                )
                            }
                        </List>
                    </Box>
                 }
                {
                    allowOrganisationSelection && <Box>
                        <Box className='sidebarBoxHeading'>
                            <img src="/static/images/organisation.svg" alt='Organisation image' />
                            <Typography color='#75B37A' fontSize='medium'>Organisation</Typography>
                        </Box>
                        <List className='ListItem' component="nav" aria-label="">
                            {loading || isLoading || isOrganisationLoading? <Loading /> :
                                <AutoCompleteCheckbox
                                    options={organisationList}
                                    selectedOption={selectedOrganisation}
                                    singleTerm={'Organisation'}
                                    pluralTerms={'Organisations'}
                                    selectAllFlag={selectAllOrganisation}
                                    setSelectAll={(val) => {
                                        setSelectAllOrganisation(val)
                                    }}
                                    setSelectedOption={setSelectedOrganisation}
                                  />
                            }
                        </List>
                    </Box>
                }
                {
                    allowPropertiesSelection &&
                    <Box>
                        <Box className='sidebarBoxHeading'>
                            <img src="/static/images/Property.svg" alt='Property image' />
                            <Typography color='#75B37A' fontSize='medium'>Property</Typography>
                        </Box>
                        <List className='ListItem' component="nav" aria-label="">
                            {loading || isPropertyLoading ? (
                                <Loading />
                            ) : (
                              <AutoCompleteCheckbox
                                options={propertyList}
                                selectedOption={selectedOrganisation.length > 0 ? selectedProperty : []}
                                singleTerm={'Property'}
                                pluralTerms={'Properties'}
                                selectAllFlag={selectAllProperty}
                                setSelectAll={(val) => setSelectAllProperty(val)}
                                setSelectedOption={(newValues) => {
                                    setSelectedProperty(newValues)
                                    if (newValues.length === 0) {
                                        adjustMapToBoundingBox(boundingBox)
                                    } else {
                                      // Call zoomToCombinedBoundingBox with the updated list of selected properties
                                      zoomToCombinedBoundingBox(newValues);
                                    }
                                }}
                              />
                            )}
                        </List>
                    </Box>
                }

                <Box>
                      <Box className='sidebarBoxHeading'>
                          <img src="/static/images/Clock.svg" alt='watch image'/>
                          <Typography color='#75B37A' fontSize='medium'>Year</Typography>
                      </Box>
                      <Box className='sliderYear'>
                          <Slider
                            value={[startYear, endYear]}
                            onChange={handleChange}
                            valueLabelDisplay="auto"
                            min={yearRangeStart}
                            max={yearRangeEnd}
                            style={{color: 'black'}}
                          />
                      </Box>

                      <Box className='formboxInput'>
                          <Box className='form-inputFild'>
                              <TextField type="number" size='small' value={localStartYear}
                                         onChange={(e: any) => handleStartYearChange(e.target.value)}/>
                              <Typography className='formtext'>From</Typography>
                          </Box>
                          <Box className='form-inputFild right-flids'>
                              <TextField type="number" size='small' value={localEndYear}
                                         onChange={(e: any) => handleEndYearChange(e.target.value)}/>
                              <Typography className='formtext'>To</Typography>
                          </Box>
                      </Box>
                </Box>

                {tab != 'trends' &&
                  <Box>
                      <Box className='sidebarBoxHeading'>
                          <img src="/static/images/Layers.svg" alt='Filter image'/>
                          <Typography color='#75B37A' fontSize='medium'>Spatial filters</Typography>
                      </Box>
                      <Box>
                          <SpatialFilter loading={loading}
                                         onSpatialFilterValuesUpdate={(spatialFilterValues: string[]) =>
                                           dispatch(setSpatialFilterValues(spatialFilterValues))}/>
                      </Box>
                  </Box>
                }
            </Box>
        </Box >
    )
}


export default Filter;

import React, { useState, useEffect } from 'react';
import {v4 as uuidv4} from 'uuid';
import axios from "axios";
import Grid from "@mui/material/Grid";
import Button from "@mui/material/Button";
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import OutlinedInput from '@mui/material/OutlinedInput';
import IconButton from "@mui/material/IconButton";
import InputAdornment from "@mui/material/InputAdornment";
import SearchIcon from '@mui/icons-material/Search';
import MenuItem from '@mui/material/MenuItem';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import {RootState} from '../../../app/store';
import {useAppDispatch, useAppSelector } from '../../../app/hooks';
import {
    setSelectedProperty,
    setSelectedParcels,
    triggerMapEvent,
    resetSelectedProperty
} from '../../../reducers/MapState';
import {
    setUploadState
} from '../../../reducers/UploadState';
import UploadWizard from './UploadWizard';
import PropertyInterface from '../../../models/Property';
import { UploadMode } from '../../../models/Upload';
import { MapEvents } from '../../../models/Map';
import { SeachPlaceResult } from '../../../utils/SearchPlaces';
import SearchPlace from '../../../components/SearchPlace';
import './index.scss';

const FETCH_PROPERTY_LIST_URL = '/api/property/list/'
const FETCH_PROPERTY_DETAIL_URL = '/api/property/detail/'

function Upload() {
    const dispatch = useAppDispatch()
    const [loading, setLoading] = useState(false)
    const uploadMode = useAppSelector((state: RootState) => state.uploadState.uploadMode)
    const [selectedPropertyId, setSelectedPropertyId] = useState<number>(0)
    const selectedProperty = useAppSelector((state: RootState) => state.mapState.selectedProperty)
    const [propertyList, setPropertyList] = useState<PropertyInterface[]>([])

    const fetchPropertyList = () => {
        setLoading(true)
        axios.get(FETCH_PROPERTY_LIST_URL).then((response) => {
            setLoading(false)
            if (response.data) {
                setPropertyList(response.data as PropertyInterface[])
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }

    useEffect(() => {
        fetchPropertyList()
    }, [])

    useEffect(() => {
        if (selectedPropertyId) {
            // fetch property detail
            setLoading(true)
            axios.get(`${FETCH_PROPERTY_DETAIL_URL}${selectedPropertyId}/`).then((response) => {
                setLoading(false)
                if (response.data) {
                    // set selected parcels+property
                    let _property = response.data as PropertyInterface
                    dispatch(setSelectedProperty(_property))
                    dispatch(setSelectedParcels(_property.parcels))
                    dispatch(setUploadState(UploadMode.PropertySelected))
                    // trigger map zoom to bbox
                    if (_property.bbox && _property.bbox.length === 4) {
                        let _bbox = _property.bbox.map(String)
                        dispatch(triggerMapEvent({
                            'id': uuidv4(),
                            'name': MapEvents.PROPERTY_SELECTED,
                            'date': Date.now(),
                            'payload': _bbox
                        }))
                    }
                }
            }).catch((error) => {
                setLoading(false)
                console.log(error)
            })
        }
    }, [selectedPropertyId])

    return (
        <Grid container flexDirection={'column'} className='Upload'>
            <Grid item className='Header'>
                DATA UPLOAD
            </Grid>
            <Grid item className='FlexContainerFill'>
                <Grid container className='UploadContainer'>
                    { uploadMode === UploadMode.SelectProperty &&
                    <Grid item className='SearchArea'>
                        <SearchPlace onPlaceSelected={(place: SeachPlaceResult) => {
                            if (place && place.bbox && place.bbox.length === 4) {
                                // trigger zoom to property
                                let _bbox = place.bbox.map(String)
                                dispatch(triggerMapEvent({
                                    'id': uuidv4(),
                                    'name': MapEvents.ZOOM_INTO_PROPERTY,
                                    'date': Date.now(),
                                    'payload': _bbox
                                }))
                            }
                        }} />
                    </Grid>
                    }
                    <Grid item className='FlexContainerFill'>
                        <Grid container className='UploadContent'>
                            { uploadMode === UploadMode.SelectProperty &&
                                <Grid container flexDirection={'column'}>
                                    <Grid item>
                                        <FormControl fullWidth>
                                            <Select
                                                id="property-select"
                                                value={selectedPropertyId.toString()}
                                                displayEmpty
                                                disabled={loading}
                                                onChange={(event: SelectChangeEvent) => {
                                                    setSelectedPropertyId(parseInt(event.target.value))
                                                }}
                                                renderValue={(selected) => {
                                                    if (selected.length === 0 || selected === '0') {
                                                        return <span className='SelectPlaceHolder'>Select Property</span>
                                                    }
                                        
                                                    return selected
                                                }}
                                            >
                                                { propertyList.map((property: PropertyInterface) => {
                                                    return (
                                                        <MenuItem key={property.id} value={property.id}>{property.name}</MenuItem>
                                                    )
                                                })}
                                            </Select>
                                        </FormControl>
                                    </Grid>
                                    <Grid item className='ButtonContainer'>
                                        <Button variant='contained' disabled={loading} onClick={() => {
                                            dispatch(resetSelectedProperty())
                                            dispatch(setSelectedParcels([]))
                                            dispatch(setUploadState(UploadMode.CreateNew))
                                        }}>CREATE A NEW PROPERTY</Button>
                                    </Grid>
                                </Grid>
                            }
                            { uploadMode === UploadMode.CreateNew && 
                                <Grid item className='FlexContainerFillHeight'>
                                    <UploadWizard />
                                </Grid>
                            }
                            { uploadMode === UploadMode.PropertySelected && selectedProperty && 
                                <Grid item className='FlexContainerFillHeight'>
                                    <UploadWizard initialProperty={selectedProperty} />
                                </Grid>
                            }
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    )
}


export default Upload;

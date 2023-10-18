import React, { useEffect, useState, useRef } from 'react';
import List from '@mui/material/List';

import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import axios from "axios";
import {Checkbox} from "@mui/material";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import {delay} from "../../../utils/Helpers";


interface SpatialFilterInterface {
    layer_title: string;
    values: string[];
}

interface SpatialFilterProp {
    loading: boolean;
    onSpatialFilterValuesUpdate: Function;
}

const FETCH_AVAILABLE_SPATIAL_FILTERS = '/api/spatial-filter-list/'

function SpatialFilter(props: SpatialFilterProp) {
    const [checkedSpatialFilterValues, setCheckedSpatialFilterValues] = (
        useState<string[] | null>(null)
    )
    const [selectedSpatialFilterGroups, setSelectedSpatialFilterGroups] = (
        useState<string[]>([])
    )
    const [spatialFilters, setSpatialFilters] = (
        useState<SpatialFilterInterface[] | null>(null)
    )
    const listGroupRefs = useRef({});

    const fetchSpatialFilters = () => {
        axios.get(FETCH_AVAILABLE_SPATIAL_FILTERS).then((response) => {
            if (response.data) {
                let spatial_filters = response.data as SpatialFilterInterface[]
                setSpatialFilters(spatial_filters)
            }
        })
    }

    useEffect(() => {
        if (!spatialFilters) {
            fetchSpatialFilters();
        }
    }, [spatialFilters]);

    useEffect(() => {
        if (spatialFilters && checkedSpatialFilterValues !== null) {
            props.onSpatialFilterValuesUpdate(checkedSpatialFilterValues);
        }
    }, [spatialFilters, checkedSpatialFilterValues]);

    const onSpatialFilterSelect = (spatialFilterValue: string) => {
        let _checkedSpatialFilterValues = checkedSpatialFilterValues;
        if (_checkedSpatialFilterValues === null) {
            _checkedSpatialFilterValues = [];
        }
        const isValueChecked = _checkedSpatialFilterValues.includes(spatialFilterValue);
        let newValues;
        if (isValueChecked) {
            newValues = _checkedSpatialFilterValues.filter(value => value !== spatialFilterValue);
        } else {
            newValues = [..._checkedSpatialFilterValues, spatialFilterValue];
        }

        setCheckedSpatialFilterValues(newValues);
    }

    const onSpatialFilterGroupSelect = (spatialFilterGroupName: string) => {
        const isGroupSelected = selectedSpatialFilterGroups.includes(spatialFilterGroupName);
        let newGroups;
        if (isGroupSelected) {
            newGroups = selectedSpatialFilterGroups.filter(group => group !== spatialFilterGroupName);
        } else {
            newGroups = [...selectedSpatialFilterGroups, spatialFilterGroupName];
        }
        setSelectedSpatialFilterGroups(newGroups);
        if (!isGroupSelected) {
            delay(100).then(() => {
                // @ts-ignore
                listGroupRefs.current[spatialFilterGroupName]?.scrollIntoView({
                    behavior: 'smooth'
                });
            })
        }
    }

    return (
        <div className='sidebarArrowsBox' id='sidebarArrowsBox'>
            <ul>
            {spatialFilters?.map((spatialFilter: SpatialFilterInterface) => <li key={spatialFilter.layer_title}>
                <ListItemButton
                    onClick={(e) => onSpatialFilterGroupSelect(
                    spatialFilter.layer_title
                )}>
                    <ListItemIcon>
                        {selectedSpatialFilterGroups.includes(spatialFilter.layer_title) ?
                            <ArrowDropDownIcon /> : <ArrowRightIcon />}
                    </ListItemIcon>
                    <ListItemText>
                        {spatialFilter.layer_title}
                    </ListItemText>
                </ListItemButton>
                { selectedSpatialFilterGroups.includes(spatialFilter.layer_title) ?
                <List
                    component="nav"
                    aria-label=""
                    // @ts-ignore
                    ref={(el) => { listGroupRefs.current[spatialFilter.layer_title] = el; }}
                >
                    {spatialFilter?.values?.map((spatialFilterValue: string, index: number) =>
                        <ListItemButton
                            key={`${spatialFilter.layer_title}-${index}`}
                            disabled={props.loading}
                            className='ListItemButton ml-4'
                            onClick={(event) =>
                                onSpatialFilterSelect(spatialFilterValue)}
                        >
                            <ListItemIcon>
                                <Checkbox
                                    edge="start"
                                    checked={
                                        checkedSpatialFilterValues !== null ?
                                            checkedSpatialFilterValues.includes(spatialFilterValue) :
                                            false}
                                    inputProps={{ 'aria-labelledby': spatialFilterValue }}
                                />
                            </ListItemIcon>
                            <ListItemText id={spatialFilterValue} primary={spatialFilterValue} />
                        </ListItemButton>)}
                </List> : null }
            </li>)}
            </ul>
        </div>
    )
}


export default SpatialFilter;

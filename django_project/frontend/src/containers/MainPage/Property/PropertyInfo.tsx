import React, {useEffect, useState} from 'react';
import axios from "axios";
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import TextField from '@mui/material/TextField';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import PropertyInterface, {
    PropertyValidation,
    PropertyTypeInterface,
    OpenCloseInterface
} from '../../../models/Property';
import { OrganisationInterface } from '../../../models/Stakeholder';
import './index.scss';

interface PropertyInfoInterface {
    property: PropertyInterface,
    enableForm: boolean,
    onUpdated?: (data: PropertyInterface, validation: PropertyValidation) => void,
    validationError?: PropertyValidation
}

const PROPERTY_METADATA_URL = '/api/property/metadata/list/'


/**
 * Display property information table with input
 * @param props PropertyInfoInterface
 * @returns 
 */
export default function PropertyInfo(props: PropertyInfoInterface) {
    const [loading, setLoading] = useState(false)
    const [propertyTypeList, setPropertyTypeList] = useState<PropertyTypeInterface[]>([])
    const [organisationList, setOrganisationList] = useState<OrganisationInterface[]>([])
    const [openCloseList, setOpenCloseList] = useState<OpenCloseInterface[]>([])

    const fetchMetadataList = () => {
        setLoading(true)
        axios.get(PROPERTY_METADATA_URL).then((response) => {
            setLoading(false)
            if (response.data) {
                setPropertyTypeList(response.data['types'])
                setOrganisationList(response.data['organisations'])
                setOpenCloseList(response.data['opens'])
                let _initial_data:any = {}
                if (response.data['organisations'].length === 1) {
                    _initial_data['organisation'] = response.data['organisations'][0]['name']
                    _initial_data['organisation_id'] = response.data['organisations'][0]['id']
                }
                if (response.data['user_name']) {
                    _initial_data['owner'] = response.data['user_name']
                }
                if (response.data['user_email']) {
                    _initial_data['owner_email'] = response.data['user_email']
                }
                if (_initial_data && props.onUpdated) {
                    props.onUpdated({ ...props.property, ..._initial_data }, {})
                }
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }

    useEffect(() => {
        fetchMetadataList()
    }, [])

    return (
        <TableContainer component={Paper}>
            <Table className='PropertyInfoTable' aria-label="property info table" size='small'>
                <colgroup>
                    <col width="50%" />
                    <col width="50%" />
                </colgroup>
                <TableHead>
                    <TableRow>
                        <TableCell>Property Information</TableCell>
                        <TableCell>Input</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {!props.enableForm && (
                    <TableRow key='property_short_code'>
                        <TableCell component="th" scope="row">
                            Property Code
                        </TableCell>
                        <TableCell className='TableCellText'>
                            <span>{props.property.short_code ? props.property.short_code : '-'}</span>
                        </TableCell>
                    </TableRow>
                    )}
                    <TableRow key='property_name'>
                        <TableCell component="th" scope="row">
                            Property Name
                        </TableCell>
                        <TableCell>
                            <TextField
                                error={props.validationError?.name}
                                disabled={loading || !props.enableForm}
                                id="input_propertyname"
                                hiddenLabel={true}
                                type={"text"}
                                onChange={val => {
                                    if (props.onUpdated) {
                                        props.onUpdated({ ...props.property, name: val.target.value }, {name:false})
                                    }
                                }}
                                value={props.property.name}
                                sx={{ width: '100%' }}
                            />
                        </TableCell>
                    </TableRow>
                    <TableRow key='owner_name'>
                        <TableCell component="th" scope="row">
                            Owner Name
                        </TableCell>
                        <TableCell>
                            <TextField
                                disabled={true}
                                id="input_ownername"
                                hiddenLabel={true}
                                type={"text"}
                                value={props.property.owner}
                                sx={{ width: '100%' }}
                            />
                        </TableCell>
                    </TableRow>
                    <TableRow key='owner_email'>
                        <TableCell component="th" scope="row">
                            Owner Email
                        </TableCell>
                        <TableCell>
                            <TextField
                                error={props.validationError?.email}
                                disabled={true}
                                id="input_owneremail"
                                hiddenLabel={true}
                                type={"text"}
                                onChange={val => {
                                    if (props.onUpdated) {
                                        props.onUpdated({ ...props.property, owner_email: val.target.value }, {email:false})
                                    }
                                }}
                                value={props.property.owner_email}
                                sx={{ width: '100%' }}
                            />
                        </TableCell>
                    </TableRow>

                    <TableRow key='open'>
                        <TableCell component="th" scope="row">
                            Open/Closed System
                        </TableCell>
                        <TableCell>
                            <FormControl fullWidth size="small">
                                <Select
                                    id="open-close-system-select"
                                    error={props.validationError?.property_type}
                                    value={ props.property.open_id ? props.property.open_id.toString() : ''}
                                    displayEmpty
                                    disabled={loading || !props.enableForm}
                                    onChange={(event: SelectChangeEvent) => {
                                        if (props.onUpdated) {
                                            let _selected = openCloseList.find(e => e.id === parseInt(event.target.value))
                                            props.onUpdated({ ...props.property, open_id: _selected.id,  open: _selected.name }, {property_type:false})
                                        }
                                    }}
                                >
                                    { openCloseList.map((open: OpenCloseInterface) => {
                                        return (
                                            <MenuItem key={open.id} value={open.id}>{open.name}</MenuItem>
                                        )
                                    })}
                                </Select>
                            </FormControl>
                        </TableCell>
                    </TableRow>

                    <TableRow key='property_type'>
                        <TableCell component="th" scope="row">
                            Property Type
                        </TableCell>
                        <TableCell>
                            <FormControl fullWidth size="small">
                                <Select
                                    id="property-type-select"
                                    error={props.validationError?.property_type}
                                    value={ props.property.property_type_id ? props.property.property_type_id.toString() : ''}
                                    displayEmpty
                                    disabled={loading || !props.enableForm}
                                    onChange={(event: SelectChangeEvent) => {
                                        if (props.onUpdated) {
                                            let _selected = propertyTypeList.find(e => e.id === parseInt(event.target.value))
                                            props.onUpdated({ ...props.property, property_type_id: _selected.id,  property_type: _selected.name }, {property_type:false})
                                        }
                                    }}
                                >
                                    { propertyTypeList.map((property_type: PropertyTypeInterface) => {
                                        return (
                                            <MenuItem key={property_type.id} value={property_type.id}>{property_type.name}</MenuItem>
                                        )
                                    })}
                                </Select>
                            </FormControl>
                        </TableCell>
                    </TableRow>
                    { props.property.id !== 0 &&
                        <TableRow key='province'>
                            <TableCell component="th" scope="row">
                                Province
                            </TableCell>
                            <TableCell className='TableCellText'>
                                <span>{props.property.province}</span>
                            </TableCell>
                        </TableRow>
                    }
                    { props.property.id !== 0 &&
                        <TableRow key='size'>
                            <TableCell component="th" scope="row">
                                Property Size
                            </TableCell>
                            <TableCell className='TableCellText'>
                                <span>{props.property.size ? props.property.size.toFixed(2) : '0'} ha</span>                                
                            </TableCell>
                        </TableRow>
                    }
                    <TableRow key='organisation'>
                        <TableCell component="th" scope="row">
                            Organisation
                        </TableCell>
                        <TableCell className='TableCellText'>
                            <span>{props.property.organisation ? props.property.organisation : '-'}</span>
                        </TableCell>
                    </TableRow>
                </TableBody>
            </Table>
        </TableContainer>
    )
}
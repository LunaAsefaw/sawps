import React from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import PropertyInterface from '../../models/Property';


interface PropertySummaryTableInterface {
    propertyItem: PropertyInterface;
}

export default function PropertySummaryTable(props: PropertySummaryTableInterface) {
    const localStorageItem = localStorage.getItem('description') ? localStorage.getItem('description') : '';
    var descriptionParts = localStorageItem ? localStorageItem.split(': ') : [];

    if(localStorageItem.includes('<hr/>')){
        const lines = localStorageItem.split("<hr/>");
        for (var count=0; count < lines.length; count++){
            if(lines[count].trim().includes('Ecosystem Type:')){
                const content = lines[1].trim();
                descriptionParts = content.split(": ")
            }
        }
    }

    return (
        <TableContainer component={Paper}>
            <Table className='PropertySiteDetailTable' aria-label="property site detail table" size='small'>
                <colgroup>
                    <col width="50%" />
                    <col width="50%" />
                </colgroup>
                <TableHead>
                </TableHead>
                <TableBody>
                    <TableRow key='property_short_code'>
                        <TableCell component="th" scope="row">
                            Property Code
                        </TableCell>
                        <TableCell>
                            {props.propertyItem.short_code ? props.propertyItem.short_code : '-'}
                        </TableCell>
                    </TableRow>
                    <TableRow key='property_name'>
                        <TableCell component="th" scope="row">
                            Property Name
                        </TableCell>
                        <TableCell>
                            {props.propertyItem.name}
                        </TableCell>
                    </TableRow>
                    <TableRow key='property_type'>
                        <TableCell component="th" scope="row">
                            Property Type
                        </TableCell>
                        <TableCell>
                            {props.propertyItem.property_type}
                        </TableCell>
                    </TableRow>
                    <TableRow key='size'>
                        <TableCell component="th" scope="row">
                            Property Size
                        </TableCell>
                        <TableCell>
                            {props.propertyItem.size}ha
                        </TableCell>
                    </TableRow>
                    <TableRow key='organisation'>
                        <TableCell component="th" scope="row">
                            Organisation
                        </TableCell>
                        <TableCell>
                            {props.propertyItem.organisation}
                        </TableCell>
                    </TableRow>
                    <TableRow key='province'>
                        <TableCell component="th" scope="row">
                            Province
                        </TableCell>
                        <TableCell>
                            {props.propertyItem.province}
                        </TableCell>
                    </TableRow>
                        {descriptionParts.length === 2 && descriptionParts[0] === 'Ecosystem Type' && (
                        <TableRow key='ecosystem_type'>
                            <TableCell component="th" scope="row">
                                {descriptionParts[0]}
                            </TableCell>
                            <TableCell>
                                {descriptionParts[1]}
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </TableContainer>
    )
}

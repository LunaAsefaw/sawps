import React, { useState } from 'react';
import Grid from "@mui/material/Grid";
import Button from "@mui/material/Button";
import PropertyInterface from '../../../models/Property';
import { PropertyInfo } from '../Property';
import Uploader from './SpeciesUploader';
import AlertMessage from "../../../components/AlertMessage";

interface Step3Interface {
    property: PropertyInterface;
    onUpdateBoundary: () => void;
}

export default function Step3(props: Step3Interface) {
    const [openUploader, setOpenUploader] = useState(false)


    return (
        <Grid container className='UploadSection Step3' rowGap={2}>
            <Grid item className='UploadSectionHeader'>
                <span className='UploadSectionHeaderIcon Population'></span>
                <span>Upload Species Population Data</span>
            </Grid>
            <Grid item className='UploadSectionContent'>
                <Grid container flexDirection={'row'} flexWrap={'nowrap'} justifyContent={'space-between'} rowGap={2} className='ButtonContainer'>
                    <Button variant='contained' className='ManualForm' href={`/upload-data/${props.property.id}/`}>ONLINE FORM</Button>
                    <Button variant='contained' className='Download' onClick={()=>window.location.href = "/static/data_template/2023-integrated-dataset-template-V6.xlsx"}>DOWNLOAD TEMPLATE</Button>
                    <Button variant='contained' className='Upload' onClick={() => setOpenUploader(true)}>UPLOAD DATA</Button>
                </Grid>
            </Grid>
            <Grid item className='UploadSectionHeader'>
                <span className='UploadSectionHeaderIcon SiteDetail'></span>
                <span>Selected Property Information</span>
            </Grid>
            <Grid item className='UploadSectionContent'>
                <Grid container flexDirection={'column'} flexWrap={'nowrap'} rowGap={2} className='ButtonContainer'>
                    <Button variant='contained' className='UpdateBoundary' onClick={props.onUpdateBoundary}>UPDATE PROPERTY BOUNDARY</Button>
                </Grid>
            </Grid>
            <Grid item className='UploadSectionContent'>
                <PropertyInfo property={props.property} enableForm={false} />
            </Grid>
            <Grid item>
                <Uploader open={openUploader} onClose={() => setOpenUploader(false)} property={props.property.id.toString()} />
            </Grid>
        </Grid>
    )
}

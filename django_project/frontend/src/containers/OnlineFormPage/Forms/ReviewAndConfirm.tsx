import React, { useState } from 'react';
import moment from 'moment';
import Grid from "@mui/material/Grid";
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import EditNoteIcon from '@mui/icons-material/EditNote';
import TextField from '@mui/material/TextField';
import InputAdornment from '@mui/material/InputAdornment';
import MaleIcon from '@mui/icons-material/Male';
import FemaleIcon from '@mui/icons-material/Female';
import Divider from '@mui/material/Divider';
import {
    GridRowId 
} from '@mui/x-data-grid';
import {
    UploadSpeciesDetailInterface,
    AnnualPopulationPerActivityInterface,
    SubpopulationTotal
} from '../../../models/Upload';
import Loading from '../../../components/Loading';
import {EventType} from './EventDetailForm';
import ActivityDataTable from './ActivityDataTable';


interface ReviewAndConfirmInterface {
    loading: boolean;
    initialData: UploadSpeciesDetailInterface;
    handleBack: (data: UploadSpeciesDetailInterface) => void;
    handleStepChange: (newStep: number) => void;
    handleSubmit: () => void;
    handleSaveDraft: () => void;
}

interface ReviewItemInterface {
    data: UploadSpeciesDetailInterface;
}

const displayText = (value: string):string => {
    return value && value.trim() ? value.trim() : '-'
}

const displayNumber = (value: number):number => {
    return value ? value : 0
}

const displayBoolean = (value: Boolean):string => {
    return value ? 'Yes':'No'
}

function SpeciesDetailReview(props: ReviewItemInterface) {
    const { data } = props;
    const [subpopulationTotal, setSubpopulationTotal] = useState<SubpopulationTotal>({
        adult: data.annual_population.adult_male + data.annual_population.adult_female,
        sub_adult: data.annual_population.sub_adult_male + data.annual_population.sub_adult_female,
        juvenile: data.annual_population.juvenile_male + data.annual_population.juvenile_female
    })
    return (
        <Grid container className='DataPreview' flexDirection={'column'} rowSpacing={2}>
            <Grid item>
                <Grid container flexDirection={'row'} spacing={4}>
                    <Grid item xs={12} md={6}>
                        <Grid container flexDirection={'column'} rowSpacing={1}>
                            <Grid item className='InputContainer'>
                                <TextField id='scientific-name' label='Scientific Name' defaultValue={displayText(data.taxon_name)}
                                    variant='standard' disabled fullWidth />
                            </Grid>
                            <Grid item className='InputContainer'>
                                <TextField id='common-name' label='Common Name' defaultValue={displayText(data.common_name)}
                                    variant='standard' disabled fullWidth />
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                        <TextField id='scientific-name' label='Year of Count' defaultValue={`${moment({year: data.year}).format('YYYY')}`}
                                            variant='standard' disabled fullWidth />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <TextField id='present' label='Species Present on Property' defaultValue={displayBoolean(data.annual_population.present)}
                                            variant='standard' disabled fullWidth />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                        <TextField id='survey-method' label='Survey Method' defaultValue={displayText(data.annual_population.survey_method_name)}
                                            variant='standard' disabled fullWidth />
                                    </Grid>
                                    <Grid item xs={6}>
                                        { data.annual_population.survey_method_other &&
                                            <TextField id='survey-method-other' label='If other, please explain' defaultValue={displayText(data.annual_population.survey_method_other)}
                                                variant='standard' disabled fullWidth />
                                        }
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                        <TextField id='sampling-effort-coverage' label='Sampling Effort Coverage' defaultValue={displayText(data.annual_population.sampling_effort_coverage_name)}
                                            variant='standard' disabled fullWidth />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <TextField id='population status' label='Population Status' defaultValue={displayText(data.annual_population.population_status_name)}
                                            variant='standard' disabled fullWidth />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                        <TextField id='population-estimate-category' label='Population Estimate Category' defaultValue={displayText(data.annual_population.population_estimate_category_name)}
                                            variant='standard' disabled fullWidth />
                                    </Grid>
                                    <Grid item xs={6}>
                                        { data.annual_population.population_estimate_category_other &&
                                            <TextField id='population-estimate-category-other' label='If other, please explain' defaultValue={displayText(data.annual_population.population_estimate_category_other)}
                                                variant='standard' disabled fullWidth />
                                        }
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <TextField id='sampling_note' label='Sampling Notes' defaultValue={displayText(data.annual_population.note)}
                                    variant='standard' disabled fullWidth />
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Grid container flexDirection={'column'} rowSpacing={1}>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={4}>
                                        <TextField
                                            id='subpopulation_total_adult'
                                            label='Total Adult'
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(subpopulationTotal.adult)}
                                            disabled
                                        />
                                    </Grid>
                                    <Grid item xs={4}>
                                        <TextField
                                            id='adult_male'
                                            label='Adult Males'
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <MaleIcon />
                                                    </InputAdornment>
                                                ),
                                            }}
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(data.annual_population.adult_male)}
                                            disabled
                                        />
                                    </Grid>
                                    <Grid item xs={4}>
                                        <TextField
                                            id='adult_female'
                                            label='Adult Females'
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <FemaleIcon />
                                                    </InputAdornment>
                                                ),
                                            }}
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(data.annual_population.adult_female)}
                                            disabled  
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={4}>
                                        <TextField
                                            id='subpopulation_total_sub_adult'
                                            label='Total Subadult'
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(subpopulationTotal.sub_adult)}
                                            disabled
                                        />
                                    </Grid>
                                    <Grid item xs={4}>
                                        <TextField
                                            id='subadult_male'
                                            label='Subadult Males'
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <MaleIcon />
                                                    </InputAdornment>
                                                ),
                                            }}
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(data.annual_population.sub_adult_male)}
                                            disabled
                                        />
                                    </Grid>
                                    <Grid item xs={4}>
                                        <TextField
                                            id='subadult_female'
                                            label='Subadult Females'
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <FemaleIcon />
                                                    </InputAdornment>
                                                ),
                                            }}
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(data.annual_population.sub_adult_female)}
                                            disabled
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={4}>
                                        <TextField
                                            id='subpopulation_total_juvenile'
                                            label='Total Juvenile'
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(subpopulationTotal.juvenile)}
                                            disabled
                                        />
                                    </Grid>
                                    <Grid item xs={4}>
                                        <TextField
                                            id='juvenile_male'
                                            label='Juvenile Males'
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <MaleIcon />
                                                    </InputAdornment>
                                                ),
                                            }}
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(data.annual_population.juvenile_male)}
                                            disabled
                                        />
                                    </Grid>
                                    <Grid item xs={4}>
                                        <TextField
                                            id='juvenile_female'
                                            label='Juvenile Females'
                                            InputProps={{
                                                startAdornment: (
                                                    <InputAdornment position="start">
                                                        <FemaleIcon />
                                                    </InputAdornment>
                                                ),
                                            }}
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(data.annual_population.juvenile_female)}
                                            disabled
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                        <TextField
                                            id='total_count'
                                            label='Total Count'
                                            disabled
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(data.annual_population.total)}                                            
                                        />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <TextField
                                            id='area_available_to_species'
                                            label='Area available to species'
                                            variant="standard"
                                            defaultValue={displayText(data.annual_population.area_available_to_species ? `${data.annual_population.area_available_to_species} ha` : '0 Ha')}
                                            disabled
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <TextField id='group' label='Number of groups (prides, herds, etc.)' defaultValue={displayNumber(data.annual_population.group)}
                                    variant='standard' disabled fullWidth />
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                        <TextField
                                            id='population_estimate_certainty'
                                            label='Population Estimate Certainty'
                                            disabled
                                            variant="standard"
                                            fullWidth
                                            defaultValue={data.annual_population.population_estimate_certainty}
                                        />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <TextField
                                            id='certainty_of_bounds'
                                            label='Certainty of Bounds'
                                            variant="standard"
                                            defaultValue={displayNumber(data.annual_population.certainty_of_bounds)}
                                            disabled
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                        <TextField
                                            id='upper_confidence_level'
                                            label='Upper Confidence Level'
                                            disabled
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(data.annual_population.upper_confidence_level)}                                            
                                        />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <TextField
                                            id='lower_confidence_level'
                                            label='Lower Confidence Level'
                                            disabled
                                            variant="standard"
                                            fullWidth
                                            defaultValue={displayNumber(data.annual_population.lower_confidence_level)}                                            
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    )
}

function ActivityDetailReview(props: ReviewItemInterface) {
    const { data } = props;
    const [selectedIntakeActivity, setSelectedIntakeActivity] = useState<AnnualPopulationPerActivityInterface>(null)
    const [selectedOfftakeActivity, setSelectedOfftakeActivity] = useState<AnnualPopulationPerActivityInterface>(null)

    return (
        <Grid container className='DataPreview' flexDirection={'column'} rowSpacing={2}>
            <Grid item>
                <Grid container flexDirection={'row'} spacing={4}>
                    <Grid item xs={12} md={6}>
                        <Grid container flexDirection={'column'} rowSpacing={1}>
                            <Grid item>
                                <Typography variant='h6'>Introduction/Reintroduction</Typography>
                            </Grid>
                            <Grid item>
                                <ActivityDataTable data={data.intake_populations} eventType={EventType.intake}
                                    isReadOnly={true} handlePreviewRow={(id: GridRowId, eventType: EventType) => {
                                        if (selectedIntakeActivity && selectedIntakeActivity.id === id) {
                                            setSelectedIntakeActivity(null)
                                        } else {
                                            let _row = data.intake_populations.find((row) => row.id === id)
                                            if (_row) {
                                                setSelectedIntakeActivity({..._row})
                                            } else {
                                                setSelectedIntakeActivity(null)
                                            }
                                        }
                                    }} />
                            </Grid>
                            <Grid item>
                                { selectedIntakeActivity && 
                                    <Grid container className='ActivityPreviewContainer' flexDirection={'column'} rowSpacing={1}>
                                        <Grid item className='InputContainer'>
                                            <Grid container flexDirection={'row'} spacing={2}>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='intake_adult_male'
                                                        label='Adult Males'
                                                        InputProps={{
                                                            startAdornment: (
                                                                <InputAdornment position="start">
                                                                    <MaleIcon />
                                                                </InputAdornment>
                                                            ),
                                                        }}
                                                        variant="standard"
                                                        fullWidth
                                                        disabled
                                                        value={displayNumber(selectedIntakeActivity.adult_male)}                                            
                                                    />
                                                </Grid>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='intake_adult_female'
                                                        label='Adult Females'
                                                        InputProps={{
                                                            startAdornment: (
                                                                <InputAdornment position="start">
                                                                    <FemaleIcon />
                                                                </InputAdornment>
                                                            ),
                                                        }}
                                                        variant="standard"
                                                        fullWidth
                                                        disabled
                                                        value={displayNumber(selectedIntakeActivity.adult_female)}                                            
                                                    />
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <Grid container flexDirection={'row'} spacing={2}>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='intake_juvenile_male'
                                                        label='Juvenile Males'
                                                        InputProps={{
                                                            startAdornment: (
                                                                <InputAdornment position="start">
                                                                    <MaleIcon />
                                                                </InputAdornment>
                                                            ),
                                                        }}
                                                        variant="standard"
                                                        fullWidth
                                                        disabled
                                                        value={displayNumber(selectedIntakeActivity.juvenile_male)}                                            
                                                    />
                                                </Grid>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='intake_juvenile_female'
                                                        label='Juvenile Females'
                                                        InputProps={{
                                                            startAdornment: (
                                                                <InputAdornment position="start">
                                                                    <FemaleIcon />
                                                                </InputAdornment>
                                                            ),
                                                        }}
                                                        variant="standard"
                                                        fullWidth
                                                        disabled
                                                        value={displayNumber(selectedIntakeActivity.juvenile_female)}                                            
                                                    />
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <Grid container flexDirection={'row'} spacing={2}>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='intake_total_count'
                                                        label='Total Count'
                                                        disabled
                                                        variant="standard"
                                                        fullWidth
                                                        value={displayNumber(selectedIntakeActivity.total)}                                            
                                                    />
                                                </Grid>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='intake_founder population'
                                                        label='Founder Population'
                                                        disabled
                                                        required
                                                        variant="standard"
                                                        fullWidth
                                                        value={displayBoolean(selectedIntakeActivity.founder_population)}                                            
                                                    />
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <TextField
                                                id='intake_event'
                                                label='Event'
                                                disabled
                                                required
                                                variant="standard"
                                                fullWidth
                                                value={displayText(selectedIntakeActivity.activity_type_name)}                                    
                                            />
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <TextField id='intake_source' label='Source' required value={displayText(selectedIntakeActivity.reintroduction_source)}
                                                variant='standard' fullWidth disabled />
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <TextField id='intake_permit' label='Permit Number' value={displayText(selectedIntakeActivity.permit ? selectedIntakeActivity.permit.toString() : '')}
                                                variant='standard' fullWidth disabled />
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <TextField id='intake_note' label='Notes' value={displayText(selectedIntakeActivity.note)}
                                                variant='standard' fullWidth disabled />
                                        </Grid>
                                    </Grid>
                                }
                            </Grid>
                            
                        </Grid>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Grid container flexDirection={'column'} rowSpacing={1}>
                            <Grid item>
                                <Typography variant='h6'>Off-take</Typography>
                            </Grid>
                            <Grid item>
                                <ActivityDataTable data={data.offtake_populations} eventType={EventType.offtake}
                                    isReadOnly={true} handlePreviewRow={(id: GridRowId, eventType: EventType) => {
                                        if (selectedOfftakeActivity && selectedOfftakeActivity.id === id) {
                                            setSelectedOfftakeActivity(null)
                                        } else {
                                            let _row = data.offtake_populations.find((row) => row.id === id)
                                            if (_row) {
                                                setSelectedOfftakeActivity({..._row})
                                            } else {
                                                setSelectedOfftakeActivity(null)
                                            }
                                        }
                                    }} />
                            </Grid>
                            <Grid item>
                                { selectedOfftakeActivity && 
                                    <Grid container className='ActivityPreviewContainer' flexDirection={'column'} rowSpacing={1}>
                                        <Grid item className='InputContainer'>
                                            <Grid container flexDirection={'row'} spacing={2}>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='offtake_adult_male'
                                                        label='Adult Males'
                                                        InputProps={{
                                                            startAdornment: (
                                                                <InputAdornment position="start">
                                                                    <MaleIcon />
                                                                </InputAdornment>
                                                            ),
                                                        }}
                                                        variant="standard"
                                                        fullWidth disabled
                                                        value={displayNumber(selectedOfftakeActivity.adult_male)} 
                                                    />
                                                </Grid>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='offtake_adult_female'
                                                        label='Adult Females'
                                                        InputProps={{
                                                            startAdornment: (
                                                                <InputAdornment position="start">
                                                                    <FemaleIcon />
                                                                </InputAdornment>
                                                            ),
                                                        }}
                                                        variant="standard"
                                                        fullWidth disabled
                                                        value={displayNumber(selectedOfftakeActivity.adult_female)} 
                                                    />
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <Grid container flexDirection={'row'} spacing={2}>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='offtake_juvenile_male'
                                                        label='Juvenile Males'
                                                        InputProps={{
                                                            startAdornment: (
                                                                <InputAdornment position="start">
                                                                    <MaleIcon />
                                                                </InputAdornment>
                                                            ),
                                                        }}
                                                        variant="standard"
                                                        fullWidth disabled
                                                        value={displayNumber(selectedOfftakeActivity.juvenile_male)} 
                                                    />
                                                </Grid>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='offtake_juvenile_female'
                                                        label='Juvenile Females'
                                                        InputProps={{
                                                            startAdornment: (
                                                                <InputAdornment position="start">
                                                                    <FemaleIcon />
                                                                </InputAdornment>
                                                            ),
                                                        }}
                                                        variant="standard"
                                                        fullWidth disabled
                                                        value={displayNumber(selectedOfftakeActivity.juvenile_female)} 
                                                    />
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <Grid container flexDirection={'row'} spacing={2}>
                                                <Grid item xs={6}>
                                                    <TextField
                                                        id='offtake_total_count'
                                                        label='Total Count'
                                                        disabled
                                                        variant="standard"
                                                        fullWidth
                                                        value={displayNumber(selectedOfftakeActivity.total)}                                            
                                                    />
                                                </Grid>
                                                <Grid item xs={6}>
                                                </Grid>
                                            </Grid>
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <TextField
                                                id='offtake-activity-label'
                                                label='Event'
                                                disabled
                                                variant="standard"
                                                fullWidth
                                                value={displayText(selectedOfftakeActivity.activity_type_name)}                                    
                                            />
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <TextField id='offtake_translocation_destination' label='Translocation Destination' required value={displayText(selectedOfftakeActivity.translocation_destination)}
                                                variant='standard' disabled fullWidth
                                                />
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <TextField id='offtake_permit' label='Permit Number' value={displayText(selectedOfftakeActivity.permit ? selectedOfftakeActivity.permit.toString() : '')}
                                                variant='standard' disabled fullWidth
                                                />
                                        </Grid>
                                        <Grid item className='InputContainer'>
                                            <TextField id='offtake_note' label='Notes' value={displayText(selectedOfftakeActivity.note)}
                                                variant='standard' disabled fullWidth
                                                />
                                        </Grid>
                                    </Grid>
                                }
                            </Grid>
                            
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    )
}

export default function ReviewAndConfirm(props: ReviewAndConfirmInterface) {
    return (
        <Grid container flexDirection={'column'} rowSpacing={2}>
            <Grid item>
                <Grid container flexDirection={'column'} rowSpacing={1}>
                    <Grid item container flexDirection={'row'} alignItems={'center'}>
                        <Typography variant='h6'>Species Detail</Typography>
                        <IconButton disabled={props.loading} aria-label='Edit Species Detail' title='Edit Species Detail' onClick={() => props.handleStepChange(0)}>
                            <EditNoteIcon />
                        </IconButton>
                    </Grid>
                    <Divider />
                    <Grid item sx={{marginTop: '10px'}}>
                        <SpeciesDetailReview data={props.initialData} />
                    </Grid>
                </Grid>
            </Grid>
            <Grid item>
                <Grid container flexDirection={'column'} rowSpacing={1}>
                    <Grid item container flexDirection={'row'} alignItems={'center'}>
                        <Typography variant='h6'>Activity Detail</Typography>
                        <IconButton disabled={props.loading} aria-label='Edit Activity Detail' title='Edit Activity Detail' onClick={() => props.handleStepChange(1)}>
                            <EditNoteIcon />
                        </IconButton>
                    </Grid>
                    <Divider />
                    <Grid item>
                        <ActivityDetailReview data={props.initialData} />
                    </Grid>
                </Grid>                
            </Grid>
            <Grid item container flexDirection={'row'} justifyContent={'space-between'}>
                <Grid item>
                    <Button variant='outlined' onClick={() => {
                        props.handleSaveDraft()
                    }}>SAVE DRAFT</Button>
                </Grid>
                <Grid item>
                    <Grid container flexDirection={'row'} justifyContent={'flex-end'} columnSpacing={2}>
                        <Grid item>
                            <Button variant='outlined' disabled={props.loading} onClick={() => props.handleBack(props.initialData)}>BACK</Button>
                        </Grid>
                        <Grid item>
                            {!props.loading && (
                                <Button variant='contained' onClick={props.handleSubmit}>SUBMIT</Button>
                            )}
                            {props.loading && (
                                <Button variant='contained'>
                                    <Loading size={20} style={{'color': 'white'}} label='SUBMITTING...' />
                                </Button>
                            )}
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Grid>
    )
}
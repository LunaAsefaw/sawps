import React, { useState, useEffect } from 'react';
import moment, { Moment } from 'moment';
import Grid from "@mui/material/Grid";
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import InputAdornment from '@mui/material/InputAdornment';
import MaleIcon from '@mui/icons-material/Male';
import FemaleIcon from '@mui/icons-material/Female';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormControl from '@mui/material/FormControl';
import FormLabel from '@mui/material/FormLabel';
import FormHelperText from '@mui/material/FormHelperText';
import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import {
    UploadSpeciesDetailInterface,
    getDefaultUploadSpeciesDetail,
    AnnualPopulationInterface,
    TaxonMetadata,
    CommonUploadMetadata,
    UploadSpeciesDetailValidation,
    FIELD_COUNTER,
    OTHER_NUMBER_FIELDS
} from '../../../models/Upload';
import { REQUIRED_FIELD_ERROR_MESSAGE } from '../../../utils/Validation';
import ConfidenceRating from './ConfidenceRating';

interface SpeciesDetailInterface {
    initialData: UploadSpeciesDetailInterface;
    taxonMetadataList: TaxonMetadata[];
    surveyMethodMetadataList: CommonUploadMetadata[];
    sampling_effort_coverages: CommonUploadMetadata[];
    population_statuses: CommonUploadMetadata[];
    population_estimate_categories: CommonUploadMetadata[];
    setIsDirty: (isDirty: boolean) => void;
    handleNext: (data: UploadSpeciesDetailInterface) => void;
    handleSaveDraft: (data: UploadSpeciesDetailInterface) => void;
}

const isOtherSelected = (value: string) => {
    if (value) {
        return value.toLowerCase().includes('other')
    }
    return false
}

export default function SpeciesDetail(props: SpeciesDetailInterface) {
    const [isConfidenceRatingOpen, setIsConfidenceRatingOpen] = useState(false);
    const handleOpenConfidenceRating = () => {
        setIsConfidenceRatingOpen(true);
    };
    const { 
        initialData, taxonMetadataList,
        surveyMethodMetadataList, sampling_effort_coverages,
        population_statuses, population_estimate_categories,
        setIsDirty, handleNext, handleSaveDraft
    } = props
    const [data, setData] = useState<UploadSpeciesDetailInterface>(getDefaultUploadSpeciesDetail(0))
    const [validation, setValidation] = useState<UploadSpeciesDetailValidation>({})

    const updateSpecies = (value: number) => {
        // find taxon
        let _selected = taxonMetadataList.find(x => x.id === value)
        if (_selected) {
            setData({
                ...data,
                taxon_id: value,
                taxon_name: _selected.scientific_name,
                common_name: _selected.common_name_varbatim,
                annual_population: {...data.annual_population},
                intake_populations: [...data.intake_populations],
                offtake_populations: [...data.offtake_populations]            
            })
            setIsDirty(true)
            setValidation({...validation, taxon_id: false})
        }
    }

    const updateYearDetail = (year: number) => {
        setData({
            ...data,
            year: year,
            annual_population: {...data.annual_population},
            intake_populations: [...data.intake_populations],
            offtake_populations: [...data.offtake_populations]            
        })
        setIsDirty(true)
    }

    const updateAnnualPopulation = (field: keyof AnnualPopulationInterface, value: any) => {
        if (field === 'total') {
            // if total is updated, then reset other number fields
            if (isNaN(value)) {
                value = 0
            }
            setData({
                ...data,
                annual_population: {
                    ...data.annual_population,
                    total: value,
                    adult_male: 0,
                    adult_female: 0,
                    sub_adult_male: 0,
                    sub_adult_female: 0,
                    juvenile_male: 0,
                    juvenile_female: 0,
                },
                intake_populations: [...data.intake_populations],
                offtake_populations: [...data.offtake_populations]     
            })
        } else {
            let _total = data.annual_population.total
            if (FIELD_COUNTER.includes(field)) {
                if (isNaN(value)) {
                    value = 0
                }
                // sum the counter fields
                _total = 0
                for (let _field of FIELD_COUNTER) {
                    if (_field === field) {
                        _total += value
                    } else {
                        let _keyField = _field as keyof AnnualPopulationInterface
                        let _fieldVal = data.annual_population[_keyField] as number
                        _total += isNaN(_fieldVal) ? 0 : _fieldVal
                    }
                }
            } else if (OTHER_NUMBER_FIELDS.includes(field)) {
                if (isNaN(value)) {
                    value = 0
                }
            }
            setData({
                ...data,
                annual_population: {
                    ...data.annual_population,
                    [field]: value,
                    total: _total,
                },
                intake_populations: [...data.intake_populations],
                offtake_populations: [...data.offtake_populations]     
            })
        }
        setIsDirty(true)
        setValidation({
            ...validation,
            annual_population: {
                ...validation.annual_population,
                [field]: false
            }
        })
    }

    const updateAnnualPopulationSelectValue = (field: keyof AnnualPopulationInterface, value: number, sourceList: CommonUploadMetadata[]) => {
        let _name_field = field.replace('_id', '_name')
        if (field === 'population_estimate_certainty') {
            _name_field = 'population_estimate_certainty_name'
        }
        let _selected = sourceList.find(element => element.id === value)
        if (_name_field == 'population_estimate_certainty_name') {
            _selected = {
                id: value,
                name: ''
            }
        }

        if (_selected) {
            setData({
                ...data,
                annual_population: {
                    ...data.annual_population,
                    [field]: value,
                    [_name_field]: _selected.name
                },
                intake_populations: [...data.intake_populations],
                offtake_populations: [...data.offtake_populations]            
            })
            setIsDirty(true)
            setValidation({
                ...validation,
                annual_population: {
                    ...validation.annual_population,
                    [field]: false
                }
            })
        }
    }

    const validateSpeciesDetail = () => {
        let _error_validation:UploadSpeciesDetailValidation = {}
        if (data.taxon_id === 0) {
            _error_validation = {..._error_validation, taxon_id: true}
        }
        if (data.year === 0) {
            _error_validation = {..._error_validation, year: true}
        }
        // if (data.annual_population.open_close_id === 0) {
        //     _error_validation = {
        //         ..._error_validation,
        //         annual_population: {
        //             ..._error_validation.annual_population,
        //             open_close_id: true
        //         }
        //     }
        // }
        if (data.annual_population.survey_method_id === 0) {
            _error_validation = {
                ..._error_validation,
                annual_population: {
                    ..._error_validation.annual_population,
                    survey_method_id: true
                }
            }
        } else if (isOtherSelected(data.annual_population.survey_method_name) &&
            (data.annual_population.survey_method_other === null || data.annual_population.survey_method_other === '')) {
                _error_validation = {
                    ..._error_validation,
                    annual_population: {
                        ..._error_validation.annual_population,
                        survey_method_other: true
                    }
                }
        }
        if (data.annual_population.population_estimate_category_id === 0) {
            _error_validation = {
                ..._error_validation,
                annual_population: {
                    ..._error_validation.annual_population,
                    population_estimate_category_id: true
                }
            }
        } else if (isOtherSelected(data.annual_population.population_estimate_category_name) &&
            (data.annual_population.population_estimate_category_other === null || data.annual_population.population_estimate_category_other === '')) {
                _error_validation = {
                    ..._error_validation,
                    annual_population: {
                        ..._error_validation.annual_population,
                        population_estimate_category_other: true
                    }
                }
        }
        setValidation(_error_validation)
        return Object.keys(_error_validation).length === 0
    }

    useEffect(() => {
        setData({
            ...initialData,
            annual_population: {...initialData.annual_population},
            intake_populations: [...initialData.intake_populations],
            offtake_populations: [...initialData.offtake_populations]
        })
        setValidation({})
    }, [initialData])

    return (
        <Grid container flexDirection={'column'} rowSpacing={2}>
            <Grid item>
                <Grid container flexDirection={'row'} spacing={4}>
                    <Grid item xs={12} md={6}>
                        <Grid container flexDirection={'column'} rowSpacing={1}>
                            <Grid item className='InputContainer'>
                                <FormControl variant="standard" required className='DropdownInput' fullWidth
                                        error={validation.taxon_id}>
                                    <InputLabel id="scientific-name-label">Scientific Name</InputLabel>
                                    <Select
                                        labelId="scientific-name-label"
                                        id="scientific-name-select"
                                        value={data.taxon_id ? data.taxon_id.toString() : ""}
                                        onChange={(event: SelectChangeEvent) => updateSpecies(parseInt(event.target.value))}
                                        displayEmpty
                                        label="Scientific Name"
                                    >
                                        { taxonMetadataList.map((taxon: TaxonMetadata) => {
                                            return (
                                                <MenuItem key={taxon.id} value={taxon.id}>
                                                    {taxon.scientific_name}
                                                </MenuItem>
                                            )
                                        })                                            
                                        }
                                    </Select>
                                    <FormHelperText>{validation.taxon_id ? REQUIRED_FIELD_ERROR_MESSAGE : ' '}</FormHelperText>
                                </FormControl>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <TextField id='common-name' label='Common Name' value={data.common_name}
                                    variant='standard' disabled fullWidth helperText=" " />
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                        <LocalizationProvider dateAdapter={AdapterMoment}>
                                            <DatePicker label={'Year of Count'} views={['year']}
                                                slotProps={{ textField: { size: 'small', variant: 'standard', className: 'Calendar', required: true } }}
                                                value={moment({'year': data.year})}
                                                onChange={(newValue: Moment) => updateYearDetail(newValue.year())}
                                            />
                                            <FormHelperText>{' '}</FormHelperText>
                                        </LocalizationProvider>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <FormControl fullWidth>
                                            <FormLabel id="present" className='CustomRadioButtonLabel' required>Species Present on Property</FormLabel>
                                            <RadioGroup
                                                aria-labelledby="present"
                                                name="present-radio-buttons"
                                                row
                                                aria-required
                                                className='RadioGroup'
                                                value={data.annual_population.present}
                                                onChange={(e) => updateAnnualPopulation('present', e.target.value === 'true')}
                                            >
                                                <FormControlLabel value={true} control={<Radio size='small' />} label="Yes" />
                                                <FormControlLabel value={false} control={<Radio size='small' />} label="No" />
                                            </RadioGroup>
                                            <FormHelperText>{' '}</FormHelperText>
                                        </FormControl>
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container spacing={2}>
                                    <Grid item xs={6}>
                                        <FormControl variant="standard" required className='DropdownInput' fullWidth error={validation.annual_population?.survey_method_id}>
                                            <InputLabel id="survey-method-label">Survey Method</InputLabel>
                                            <Select
                                                labelId="survey-method-label"
                                                id="survey-method-select"
                                                value={data.annual_population.survey_method_id ? data.annual_population.survey_method_id.toString() : ""}
                                                onChange={(event: SelectChangeEvent) => updateAnnualPopulationSelectValue('survey_method_id', parseInt(event.target.value), surveyMethodMetadataList)}
                                                displayEmpty
                                                label="Survey Method"
                                            >
                                                { surveyMethodMetadataList.map((common: CommonUploadMetadata) => {
                                                    return (
                                                        <MenuItem key={common.id} value={common.id}>
                                                            {common.name}
                                                        </MenuItem>
                                                    )
                                                })
                                                }
                                            </Select>
                                            <FormHelperText>{validation.annual_population?.survey_method_id ? REQUIRED_FIELD_ERROR_MESSAGE : ' '}</FormHelperText>
                                        </FormControl>
                                    </Grid>
                                    <Grid item xs={6}>
                                        { isOtherSelected(data.annual_population.survey_method_name) && 
                                            <TextField id='survey_method_other' label='If other, please explain' value={data.annual_population.survey_method_other}
                                                variant='standard'
                                                onChange={(e) => updateAnnualPopulation('survey_method_other', e.target.value) } fullWidth
                                                helperText=" " />
                                        }
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                    <FormControl variant="standard" className='DropdownInput' fullWidth>
                                        <InputLabel id="sampling-effort-coverage-label">Sampling Effort Coverage</InputLabel>
                                        <Select
                                        labelId="sampling-effort-coverage-label"
                                        id="sampling-effort-coverage-select"
                                        value={data.annual_population.sampling_effort_coverage_id ? data.annual_population.sampling_effort_coverage_id.toString() : ""}
                                        onChange={(event: SelectChangeEvent) => updateAnnualPopulationSelectValue('sampling_effort_coverage_id', parseInt(event.target.value), sampling_effort_coverages)}
                                        displayEmpty
                                        label="Sampling Effort Coverage"
                                        style={{ width: '300px' }}
                                        >
                                        {sampling_effort_coverages.map((common: CommonUploadMetadata) => {
                                            return (
                                            <MenuItem key={common.id} value={common.id}>
                                                {common.name}
                                            </MenuItem>
                                            )
                                        })}
                                        </Select>
                                        <FormHelperText>{' '}</FormHelperText>
                                    </FormControl>
                                    </Grid>
                                    <Grid item xs={6}>
                                    <FormControl variant="standard" className='DropdownInput' fullWidth>
                                        <InputLabel id="population-status-label">Population Status</InputLabel>
                                        <Select
                                        labelId="population-status-label"
                                        id="population-status-select"
                                        value={data.annual_population.population_status_id ? data.annual_population.population_status_id.toString() : ""}
                                        onChange={(event: SelectChangeEvent) => updateAnnualPopulationSelectValue('population_status_id', parseInt(event.target.value), population_statuses)}
                                        displayEmpty
                                        label="Population Status"
                                        style={{ width: '300px' }}
                                        >
                                        {population_statuses.map((common: CommonUploadMetadata) => {
                                            return (
                                            <MenuItem key={common.id} value={common.id}>
                                                {common.name}
                                            </MenuItem>
                                            )
                                        })}
                                        </Select>
                                        <FormHelperText>{' '}</FormHelperText>
                                    </FormControl>
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container spacing={2}>
                                    <Grid item xs={6}>
                                        <FormControl variant="standard" required className='DropdownInput' fullWidth>
                                            <InputLabel id="population-estimate-category-label">Population Estimate Category</InputLabel>
                                            <Select
                                                labelId="population-estimate-category-label"
                                                id="population-estimate-category-select"
                                                value={data.annual_population.population_estimate_category_id ? data.annual_population.population_estimate_category_id.toString() : ""}
                                                onChange={(event: SelectChangeEvent) => updateAnnualPopulationSelectValue('population_estimate_category_id', parseInt(event.target.value), population_estimate_categories)}
                                                displayEmpty
                                                label="Population Estimate Category"
                                            >
                                                { population_estimate_categories.map((common: CommonUploadMetadata) => {
                                                    return (
                                                        <MenuItem key={common.id} value={common.id}>
                                                            {common.name}
                                                        </MenuItem>
                                                    )
                                                })                                            
                                                }
                                            </Select>
                                            <FormHelperText>{' '}</FormHelperText>
                                        </FormControl>
                                    </Grid>
                                    <Grid item xs={6}>
                                        { isOtherSelected(data.annual_population.population_estimate_category_name) && 
                                            <TextField id='population_estimate_category_other' label='If other, please explain' value={data.annual_population.population_estimate_category_other}
                                                variant='standard'
                                                onChange={(e) => updateAnnualPopulation('population_estimate_category_other', e.target.value) } fullWidth
                                                helperText={validation.annual_population?.population_estimate_category_other ? REQUIRED_FIELD_ERROR_MESSAGE : ' '} />
                                        }
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <TextField id='sampling_note' label='Sampling Notes' value={data.annual_population.note}
                                    variant='standard'
                                    onChange={(e) => updateAnnualPopulation('note', e.target.value) } fullWidth
                                    helperText=" " />
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Grid container flexDirection={'column'} rowSpacing={1}>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
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
                                            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                                            variant="standard"
                                            fullWidth
                                            value={data.annual_population.adult_male}
                                            onChange={(e) => updateAnnualPopulation('adult_male', parseInt(e.target.value))}
                                            helperText=" "
                                        />
                                    </Grid>
                                    <Grid item xs={6}>
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
                                            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                                            variant="standard"
                                            fullWidth
                                            value={data.annual_population.adult_female}
                                            onChange={(e) => updateAnnualPopulation('adult_female', parseInt(e.target.value))}
                                            helperText=" "
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
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
                                            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                                            variant="standard"
                                            fullWidth
                                            value={data.annual_population.sub_adult_male}
                                            onChange={(e) => updateAnnualPopulation('sub_adult_male', parseInt(e.target.value))}
                                            helperText=" "
                                        />
                                    </Grid>
                                    <Grid item xs={6}>
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
                                            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                                            variant="standard"
                                            fullWidth
                                            value={data.annual_population.sub_adult_female}
                                            onChange={(e) => updateAnnualPopulation('sub_adult_female', parseInt(e.target.value))}
                                            helperText=" "
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
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
                                            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                                            variant="standard"
                                            fullWidth
                                            value={data.annual_population.juvenile_male}
                                            onChange={(e) => updateAnnualPopulation('juvenile_male', parseInt(e.target.value))}
                                            helperText=" "
                                        />
                                    </Grid>
                                    <Grid item xs={6}>
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
                                            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                                            variant="standard"
                                            fullWidth
                                            value={data.annual_population.juvenile_female}
                                            onChange={(e) => updateAnnualPopulation('juvenile_female', parseInt(e.target.value))}
                                            helperText=" "
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
                                            inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                                            variant="standard"
                                            fullWidth
                                            value={data.annual_population.total}
                                            onChange={(e) => updateAnnualPopulation('total', parseInt(e.target.value))}
                                            helperText=" "
                                        />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <TextField
                                            id='area_available_to_species'
                                            label='Area available to species'
                                            required
                                            InputProps={{
                                                endAdornment: (
                                                    <InputAdornment position="end">
                                                        ha
                                                    </InputAdornment>
                                                ),
                                                inputProps: { 
                                                    min: 0,
                                                    step: 0.5
                                                }
                                            }}
                                            type='number'
                                            variant="standard"
                                            fullWidth
                                            value={data.annual_population.area_available_to_species.toString()}
                                            onChange={(e) => updateAnnualPopulation('area_available_to_species', parseFloat(e.target.value))}
                                            helperText=" "
                                        />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <TextField id='group' label='Number of groups (prides, herds, etc.)' value={data.annual_population.group ? data.annual_population.group : ''}
                                    inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                                    variant='standard'
                                    onChange={(e) => updateAnnualPopulation('group', parseInt(e.target.value)) } fullWidth
                                    helperText=" " />
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <ConfidenceRating
                                        open={isConfidenceRatingOpen}
                                        onClose={() => setIsConfidenceRatingOpen(false)}
                                        onSubmit={() => setIsConfidenceRatingOpen(false)}
                                        currentConfidence={data.annual_population.population_estimate_certainty}
                                        onConfidenceChange={(newValue: number) =>
                                            updateAnnualPopulationSelectValue(
                                            'population_estimate_certainty',
                                            newValue,
                                            []
                                            )
                                        }
                                        modalHeight="auto"
                                    />

                                    <Grid item xs={6}>
                                        <div className="select-container">
                                            <InputLabel id="population-estimate-certainty-label">
                                            Population Estimate Certainty*
                                            </InputLabel>
                                            <FormControl
                                            variant="standard"
                                            required
                                            className="DropdownInput"
                                            fullWidth
                                            error={validation.annual_population?.population_estimate_certainty}
                                            >
                                            <div
                                                className="select-box"
                                                onClick={handleOpenConfidenceRating}
                                            >
                                                {/* Display the selected value or placeholder */}
                                                <div className="select-value">
                                                {data.annual_population.population_estimate_certainty ||
                                                data.annual_population.population_estimate_certainty == 0
                                                    ? data.annual_population.population_estimate_certainty.toString()
                                                    : 'Select an option'}
                                                </div>
                                            </div>
                                            <FormHelperText>
                                                {validation.annual_population?.population_estimate_certainty
                                                ? REQUIRED_FIELD_ERROR_MESSAGE
                                                : ' '}
                                            </FormHelperText>
                                            </FormControl>
                                        </div>
                                    </Grid>
                                    <Grid item xs={6}>
                                        <TextField id='certainty_of_bounds' label='Certainty of Bounds' value={data.annual_population.certainty_of_bounds ? data.annual_population.certainty_of_bounds : ''}
                                                inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
                                                variant='standard'
                                                onChange={(e) => updateAnnualPopulation('certainty_of_bounds', parseInt(e.target.value)) } fullWidth
                                                helperText=" " />
                                    </Grid>
                                </Grid>
                            </Grid>
                            <Grid item className='InputContainer'>
                                <Grid container flexDirection={'row'} spacing={2}>
                                    <Grid item xs={6}>
                                        <TextField id='upper_confidence_level' label='Upper Confidence Level' value={data.annual_population.upper_confidence_level || data.annual_population.upper_confidence_level == 0 ? data.annual_population.upper_confidence_level : ''}
                                            type='number'
                                            variant='standard'
                                            InputProps={{
                                                inputProps: { 
                                                    min: 0,
                                                    max: 100,
                                                    step: 0.5
                                                }
                                            }}
                                            onChange={(e) => updateAnnualPopulation('upper_confidence_level', parseFloat(e.target.value)) } fullWidth
                                            helperText=" " />
                                    </Grid>
                                    <Grid item xs={6}>
                                        <TextField id='lower_confidence_level' label='Lower Confidence Level' value={data.annual_population.lower_confidence_level || data.annual_population.lower_confidence_level == 0 ? data.annual_population.lower_confidence_level : ''}
                                                type='number'
                                                variant='standard'
                                                InputProps={{
                                                    inputProps: { 
                                                        min: 0,
                                                        max: 100,
                                                        step: 0.5
                                                    }
                                                }}
                                                onChange={(e) => updateAnnualPopulation('lower_confidence_level', parseFloat(e.target.value)) } fullWidth
                                                helperText=" " />
                                    </Grid>
                                </Grid>
                            </Grid>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
            <Grid item container flexDirection={'row'} justifyContent={'space-between'}>
                <Grid item>
                    <Button variant='outlined' onClick={() => {
                        handleSaveDraft(data)
                    }}>SAVE DRAFT</Button>
                </Grid>
                <Grid item>
                    <Button variant='contained' onClick={() => {
                        if (validateSpeciesDetail()) {
                            let _data = {
                                ...data,
                                annual_population: {...data.annual_population},
                                intake_populations: [...data.intake_populations],
                                offtake_populations: [...data.offtake_populations]                                
                            }
                            handleNext(_data)
                        }
                    }}>NEXT</Button>
                </Grid>
            </Grid>
        </Grid>
    )
}

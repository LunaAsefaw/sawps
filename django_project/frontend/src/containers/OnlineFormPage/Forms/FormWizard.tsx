import React, { useState, useEffect, useCallback } from 'react';
import axios from "axios";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepButton from '@mui/material/StepButton';
import TabPanel from '../../../components/TabPanel';
import {UploadSpeciesDetailInterface, getDefaultUploadSpeciesDetail} from '../../../models/Upload'
import './index.scss';
import PropertyInterface from '../../../models/Property';
import SpeciesDetail from './SpeciesDetail';
import ActivityDetail from './ActivityDetail';
import ReviewAndConfirm from './ReviewAndConfirm';
import ConfirmationAlertDialog from '../../../components/ConfirmationAlertDialog';
import FeedbackAlertDialog, {AlertType} from '../../../components/FeedbackAlertDialog';
import AlertMessage from '../../../components/AlertMessage';
import { TaxonMetadata, CommonUploadMetadata } from '../../../models/Upload';
import {postData} from "../../../utils/Requests";

export interface FormMetadata {
    taxons: TaxonMetadata[];
    survey_methods: CommonUploadMetadata[];
    intake_events: CommonUploadMetadata[];
    offtake_events: CommonUploadMetadata[];
    sampling_effort_coverages: CommonUploadMetadata[];
    population_statuses: CommonUploadMetadata[];
    population_estimate_categories: CommonUploadMetadata[];
    certainties: CommonUploadMetadata[];
}

interface FormWizardInterface {
    propertyItem: PropertyInterface;
    metadata: FormMetadata;
    draftUUID?: string;
}

const steps = ['SPECIES DETAIL', 'ACTIVITY DETAIL', 'REVIEW & SUBMIT']
const SUBMIT_SPECIES_DATA = '/api/upload/population/'
const SAVE_DRAFT_SPECIES_DATA = '/api/upload/population/draft/'

function FormWizard(props: FormWizardInterface) {
    const [loading, setLoading] = useState<boolean>(false)
    const [isDirty, setIsDirty] = useState(false)
    const [data, setData] = useState<UploadSpeciesDetailInterface>(getDefaultUploadSpeciesDetail(props.propertyItem.id))
    const [activeStep, setActiveStep] = React.useState(0);
    const [completed, setCompleted] = React.useState<{
        [k: number]: boolean
    }>({})
    const [confirmationOpen, setConfirmationOpen] = useState(false)
    const [navigateTo, setNavigateTo] = useState<number>(-1)
    const [feedbackAlertDialog, setFeedbackAlertDialog] = useState<AlertType>(AlertType.none)
    const [feedbackAlertDesc, setFeedbackAlertDesc] = useState<string>('')
    const [alertMessage, setAlertMessage] = useState<string>('')
    const [draftUUID, setDraftUUID] = useState<string>('')

    const totalSteps = () => {
        return steps.length
    }

    const completedSteps = () => {
        return Object.keys(completed).length
    }

    const isLastStep = () => {
        return activeStep === totalSteps() - 1
    }

    const allStepsCompleted = () => {
        return completedSteps() === totalSteps()
    }

    const handleNext = () => {
        const newActiveStep =
        isLastStep() && !allStepsCompleted()
            ? // It's the last step, but not all steps have been completed,
            // find the first step that has been completed
            steps.findIndex((step, i) => !(i in completed))
            : activeStep + 1
        setActiveStep(newActiveStep)
    }

    const handleBack = () => {
        setActiveStep((prevActiveStep) => prevActiveStep - 1)
    }

    const handleStep = (step: number) => {
        if (isDirty) {
            setNavigateTo(step)
            setConfirmationOpen(true)
        } else {
            setActiveStep(step)
        }
    }

    const onFormSave = (index: number, formData: UploadSpeciesDetailInterface) => {
        setCompleted({
            ...completed,
            [index]: true
        })
        setData({
            ...formData,
            annual_population: {...formData.annual_population},
            intake_populations: [...formData.intake_populations],
            offtake_populations: [...formData.offtake_populations]
        })
        handleNext()
    }

    const onFormBack = (index: number, formData: UploadSpeciesDetailInterface) => {
        setData({
            ...formData,
            annual_population: {...formData.annual_population},
            intake_populations: [...formData.intake_populations],
            offtake_populations: [...formData.offtake_populations]
        })
        handleBack()
    }

    useEffect(() => {
        setIsDirty(false)
    }, [activeStep])

    /* Check Unsaved Changes */
    useEffect(() => {
        window.addEventListener("beforeunload", alertUserUnsavedChanges)
        return () => {
          window.removeEventListener("beforeunload", alertUserUnsavedChanges)
        }
    }, [isDirty])

    const alertUserUnsavedChanges = useCallback((e:any) => {
        if (isDirty) {
            e.preventDefault()
            e.returnValue = ""
        }
    }, [isDirty])

    const handleUnsavedChangesConfirmationClose = () => {
        setConfirmationOpen(false)
        setNavigateTo(-1)
    }

    const handleUnsavedChangesConfirmationOk = () => {
        setActiveStep(navigateTo)
        handleUnsavedChangesConfirmationClose()
    }
    /* End of Check Unsaved Changes */

    /* handle draft and submission */
    const handleSubmit = () => {
        setLoading(true)
        postData(`${SUBMIT_SPECIES_DATA}${props.propertyItem.id}/?uuid=${draftUUID}`, data).then(
            response => {
                setLoading(false)
                setFeedbackAlertDialog(AlertType.success)
                setFeedbackAlertDesc('Your data has been successfully saved!')
            }
          ).catch(error => {
            setLoading(false)
            console.log('error ', error)
            setFeedbackAlertDialog(AlertType.error)
            let _error = 'There is an error while saving the data!'
            if (error.response && error.response.status >= 400 && error.response.status < 500 && 'detail' in error.response.data) {
                _error = error.response.data['detail']
            }
            setFeedbackAlertDesc(_error)
          })
    }

    const handleSaveDraft = (formData: UploadSpeciesDetailInterface) => {
        setLoading(true)
        let _data = {
            'form_data': formData,
            'last_step': activeStep
        }
        postData(`${SAVE_DRAFT_SPECIES_DATA}${props.propertyItem.id}/?uuid=${draftUUID}`, _data).then(
            response => {
                setLoading(false)
                setAlertMessage('The form has been successfully saved as draft!')
                setDraftUUID(response.data['uuid'])
            }
          ).catch(error => {
            setLoading(false)
            console.log('error ', error)
            let _error = 'There is an error while saving the data!'
            if (error.response && error.response.status >= 400 && error.response.status < 500 && 'detail' in error.response.data) {
                _error = error.response.data['detail']
            }
            setAlertMessage(_error)
          })
    }

    useEffect(() => {
        if (props.draftUUID) {
            axios.get(`${SAVE_DRAFT_SPECIES_DATA}${props.draftUUID}/`).then((response) => {
                if (response) {
                    setDraftUUID(props.draftUUID)
                    let _lastStep = response.data['last_step'] as number
                    let _formData = response.data['form_data'] as UploadSpeciesDetailInterface
                    setData({
                        ..._formData,
                        annual_population: {..._formData.annual_population},
                        intake_populations: [..._formData.intake_populations],
                        offtake_populations: [..._formData.offtake_populations]
                    })
                    if (_lastStep > 0) {
                        setActiveStep(_lastStep)
                        if (_lastStep === 2) {
                            setCompleted({
                                ...completed,
                                0: true,
                                1: true
                            })
                        } else {
                            setCompleted({
                                ...completed,
                                0: true
                            })
                        }
                    }
                } else {
                    setAlertMessage('There is an error while fetching draft upload!')
                }
            }).catch((error) => {
                console.log(error)
                setAlertMessage('There is an error while fetching draft upload!')
            })
        }
    }, [props.draftUUID])
    /* end of handle draft and submission */

    return (
        <Grid container className='OnlineFormWizard' flexDirection={'column'}>
            <Box className='TabHeaders'>
                <Stepper nonLinear activeStep={activeStep}>
                    {steps.map((label, index) => (
                    <Step key={label} disabled={loading || (index > activeStep && !completed[index])} completed={completed[index]}>
                        <StepButton color="inherit" onClick={() => handleStep(index)} className={activeStep === index && isDirty ? 'form-dirty' : ''}>
                            {label}
                        </StepButton>
                    </Step>
                    ))}
                </Stepper>
            </Box>
            <Box className='TabPanels FlexContainerFill'>
                <Box className='OnlineFormWizardContent'>
                    <TabPanel key={0} value={activeStep} index={0} noPadding>
                        <SpeciesDetail initialData={data} setIsDirty={setIsDirty} handleNext={(formData)=>onFormSave(0, formData)}
                            taxonMetadataList={props.metadata.taxons}
                            surveyMethodMetadataList={props.metadata.survey_methods}
                            sampling_effort_coverages={props.metadata.sampling_effort_coverages} population_statuses={props.metadata.population_statuses}
                            population_estimate_categories={props.metadata.population_estimate_categories}
                            handleSaveDraft={handleSaveDraft} />
                    </TabPanel>
                    <TabPanel key={1} value={activeStep} index={1} noPadding>
                        <ActivityDetail initialData={data} setIsDirty={setIsDirty} handleNext={(formData)=>onFormSave(1, formData)}
                            handleBack={(formData) => onFormBack(1, formData)}
                            intakeEventMetadataList={props.metadata.intake_events} offtakeEventMetadataList={props.metadata.offtake_events}
                            handleSaveDraft={handleSaveDraft} />
                    </TabPanel>
                    <TabPanel key={2} value={activeStep} index={2} noPadding>
                        <ReviewAndConfirm initialData={data} handleStepChange={(newStep: number) => handleStep(newStep)}
                            handleBack={(formData) => onFormBack(2, formData)}
                            handleSubmit={handleSubmit} loading={loading}
                            handleSaveDraft={() => handleSaveDraft(data)} />
                    </TabPanel>
                </Box>
            </Box>
            <Grid item>
                <ConfirmationAlertDialog open={confirmationOpen} alertClosed={handleUnsavedChangesConfirmationClose}
                    alertConfirmed={handleUnsavedChangesConfirmationOk}
                    alertDialogTitle={'Unsaved changes'}
                    alertDialogDescription={'You have unsaved changes. Are you sure to leave this page?'}
                    confirmButtonText='Leave'
                    confirmButtonProps={{color: 'error', autoFocus: true}}
                />
            </Grid>
            <Grid item>
                <FeedbackAlertDialog type={feedbackAlertDialog} alertDialogTitle='Upload Species Data'
                    alertDialogDescription={feedbackAlertDesc} alertClosed={() => {
                        if (feedbackAlertDialog === AlertType.success) {
                            window.location.replace(window.location.origin + '/map/?tab=1')
                        } else {
                            setFeedbackAlertDialog(AlertType.none)
                        }
                    }} />
            </Grid>
            <Grid item>
                <AlertMessage message={alertMessage} onClose={() => setAlertMessage('')} />
            </Grid>
        </Grid>
    )
}

export default FormWizard;
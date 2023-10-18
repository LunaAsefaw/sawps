import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import {v4 as uuidv4} from 'uuid';
import Alert from "@mui/material/Alert";
import AlertTitle from "@mui/material/AlertTitle";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import DialogTitle from '@mui/material/DialogTitle';
import Dialog from '@mui/material/Dialog';
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import Dropzone, { ILayoutProps, IInputProps } from "react-dropzone-uploader";
import { useAppDispatch, useAppSelector } from '../../../app/hooks';
import {RootState} from '../../../app/store';
import '../../../assets/styles/RDU.styles.scss';
import './index.scss';
import {wait} from "@testing-library/user-event/dist/utils";

interface UploaderInterface {
    open: boolean;
    property: string;
    onClose: () => void;
}

const ALLOWABLE_FILE_TYPES = [
    '.csv',
    '.xlsx'
]

const UPLOAD_FILE_URL = '/api/upload-species/'
const PROCESS_FILE_URL = '/api/save-csv-species/'
const STATUS_URL = '/api/upload-species-status/'

const CustomInput = (props: IInputProps) => {
    const {
      className,
      style,
      getFilesFromEvent,
      accept,
      multiple,
      disabled,
      onFiles,
    } = props

    return (
    <Grid container flexDirection={'column'}>
        <Grid item>
            <span className='CloudUploadIcon'/>
        </Grid>
        <Grid item className='CenterItem'>
            <label>
                <span>Drag & drop files or </span><span className='BrowseLink'>Browse</span>
                <input
                className={className}
                style={style}
                type="file"
                accept={accept}
                multiple={multiple}
                disabled={disabled}
                onChange={async e => {
                    const target = e.target
                    const chosenFiles = await getFilesFromEvent(e)
                    onFiles(chosenFiles)
                    //@ts-ignore
                    target.value = null
                }}
                />
            </label>
        </Grid>
        <Grid item className='CenterItem'>
            <Typography variant='subtitle2' sx={{fontWeight: 400}}>Supported formats: csv and xlsx</Typography>
        </Grid>
    </Grid>

    )
  }

export default function Uploader(props: UploaderInterface) {
    const dispatch = useAppDispatch()
    const { open, onClose } = props;
    const [session, setSession] = useState('')
    const [loading, setLoading] = useState(false)
    const dropZone = useRef(null)
    const [alertMessage, setAlertMessage] = useState('')
    const [isError, setIsError] = useState(false)
    const [savingSpeciesCSV, setSavingSpeciesCSV] = useState(false)
    const uploadMode = useAppSelector((state: RootState) => state.uploadState.uploadMode)
    const [totalFile, setTotalFile] = useState(0)
    const [closeButton, setCloseButton] = useState('CANCEL')
    const [errorFile, setErrorFile] = useState('')

    useEffect(() => {
        if (open) {
            setSession(uuidv4())
            setIsError(false)
            setAlertMessage('')
            setErrorFile('')
            setSavingSpeciesCSV(false)
            setTotalFile(0)
            setLoading(false)
        }
    }, [open])

    // @ts-ignore
    const _csrfToken = csrfToken || '';

    // specify upload params and url for your files
    // @ts-ignore
    const getUploadParams = ({file}) => {
        if (loading) return null
        const body = new FormData()
        body.append('file', file)
        body.append('token', session)
        body.append('property', props.property)
        const headers = {
            'X-CSRFToken': _csrfToken
        }
        return {url: UPLOAD_FILE_URL, body, headers}
    }

    // called every time a file's `status` changes
    // @ts-ignore
    const handleChangeStatus = (file, status) => {
        let {meta, f, xhr} = file
        meta.session = session
        if (status === 'preparing') {
            setIsError(false)
            setAlertMessage('')
        }
        if (status === 'done') {
            setTotalFile(totalFile + 1)
        }
        if (status === 'removed') {
            const dropZoneCurrent = dropZone.current;
            setTotalFile(0)
            if (!dropZoneCurrent) {
                setIsError(true)
                setAlertMessage('Unable to remove the layer file, Please try again!')
                // exit if ref dropZone is not found
                return;
            }
        }

        if (status === 'error_upload') {
            setLoading(true)
            setCloseButton('CLOSE')
            setTimeout(() => {
                file.remove()
                let response = JSON.parse(xhr.response)
                setIsError(true)
                setAlertMessage(response.detail)

            }, 300)
        }
    };

    const handleClose = (event: any, reason: any) => {
        if (reason && (reason == 'backdropClick' || reason == 'escapeKeyDown'))
            return;
        onClose();
    };

    const saveSpeciesFiles = () => {
        setLoading(true)
        fetch(PROCESS_FILE_URL, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': _csrfToken
            },
            body: JSON.stringify({
                'token': session,
                'property': props.property
            })
            }).then( response => {
                setLoading(false)
                setSavingSpeciesCSV(true)
            }).catch((error) => {
                setLoading(false)
                })
    }

    const getStatus = () => {
        axios.get(`${STATUS_URL}${session}/`).then((response) => {
            if (response.data) {
                let status = response.data['status']
                if (status === 'Finished') {
                    setIsError(false)
                    setAlertMessage(response.data['message'])
                    setErrorFile(response.data['error_file'])
                    setTotalFile(0)
                    setSavingSpeciesCSV(false)
                    setCloseButton('CLOSE')
                    setLoading(false)
                } else {
                    setIsError(true)
                    setAlertMessage(response.data['message'])
                    setErrorFile(response.data['error_file'])
                    setTotalFile(totalFile - 1)
                    setSavingSpeciesCSV(false)
                    setCloseButton('CLOSE')
                    setLoading(false)
                }

            } else {
                setIsError(true)
                setAlertMessage('There is something wrong with the data please check again.')
            }
        })
    }

    useEffect(() => {
        if (savingSpeciesCSV) {
            const interval = setInterval(() => {
                getStatus()
            }, 3000);
            return () => clearInterval(interval);
        }
    }, [savingSpeciesCSV])
    const CustomLayout = ({ input, previews, submitButton, dropzoneProps, files, extra: { maxFiles } }: ILayoutProps) => {
        return (
            <Grid container flexDirection={'column'} rowSpacing={2} className='uploader-container'>
                <Grid item>
                    <div {...dropzoneProps}>
                        {input}
                    </div>
                </Grid>
                <Grid item>
                    <Grid container flexDirection={'column'}>
                        <Grid item>
                            <Typography sx={{ fontSize: 14 }} color='text.secondary' gutterBottom>
                                Uploaded File
                            </Typography>
                        </Grid>
                        <Grid item className='UploadedFilesPreview'>
                            {previews}
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        )
    }

        return (
        <Dialog onClose={handleClose} open={open} className='Uploader'>
            <DialogTitle>Upload Data</DialogTitle>
            <Grid container flexDirection={'column'} className='UploaderContent' rowSpacing={2}>
                <Grid item>
                { alertMessage ?
                    <Alert style={{ width: '100%'}} severity={isError ? "error" : errorFile ? "warning" : "success"}>
                    <AlertTitle>{ isError ? 'Error' : <> { errorFile ? 'Warning': 'Success' }</>}</AlertTitle>
                    <div className="display-linebreak">
                        <span>{ alertMessage }</span><br/>
                        { errorFile ?
                            <Button variant='contained' className='ErrorFile' onClick={()=>window.location.href=`${errorFile}`}>Error file</Button>: null }
                    </div>
                    </Alert> : null }
                    <Dropzone
                        ref={dropZone}
                        disabled={loading || savingSpeciesCSV}
                        InputComponent={CustomInput}
                        maxFiles={1}
                        getUploadParams={getUploadParams}
                        onChangeStatus={handleChangeStatus}
                        accept={ALLOWABLE_FILE_TYPES.join(', ')}
                        LayoutComponent={CustomLayout}
                    />
                </Grid>
                <Grid item>
                    <Grid container flexDirection={'row'} justifyContent={'space-between'} spacing={2}>
                        <Grid item>
                            <Button variant='outlined' disabled={false} onClick={() => onClose()}>{closeButton}</Button>
                        </Grid>
                        <Grid item>
                            { savingSpeciesCSV ? (
                                <Button variant='contained' disabled={true}><CircularProgress size={16} sx={{marginRight: '5px' }}/> PROCESSING FILE...</Button>
                            ) : (
                                <Button variant='contained' disabled={loading || savingSpeciesCSV || totalFile === 0} onClick={saveSpeciesFiles}>UPLOAD FILE</Button>
                            )}
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>
        </Dialog>
    )

}

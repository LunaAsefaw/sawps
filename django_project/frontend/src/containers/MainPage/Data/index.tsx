import React, { useEffect, useState } from "react";
import {Box, Button, Checkbox, Grid, ListItemText, Typography} from "@mui/material";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import { DataGrid, GridColDef } from '@mui/x-data-grid';
import Loading from '../../../components/Loading';
import { saveAs } from 'file-saver';
import * as XLSX from 'xlsx';
import axios from "axios";
import { useAppSelector } from "../../../app/hooks";
import { RootState } from "../../../app/store";
import { getTitle } from "../../../utils/Helpers";
import {
    Activity,
    useGetUserInfoQuery,
    useGetActivityAsObjQuery,
    UserInfo
} from "../../../services/api";
import Topper from "./Topper";
import './index.scss';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250,
        },
    },
};

const FETCH_AVAILABLE_DATA = '/api/data-table/'

const DataList = () => {
    const selectedSpecies = useAppSelector((state: RootState) => state.SpeciesFilter.selectedSpecies)
    const startYear = useAppSelector((state: RootState) => state.SpeciesFilter.startYear)
    const endYear = useAppSelector((state: RootState) => state.SpeciesFilter.endYear)
    const selectedInfo = useAppSelector((state: RootState) => state.SpeciesFilter.selectedInfoList)
    const spatialFilterValues = useAppSelector((state: RootState) => state.SpeciesFilter.spatialFilterValues);
    const [selectedColumns, setSelectedColumns] = useState([]);
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState([])
    const [columns, setColumns] = useState([])
    const [rows, setRows] = useState([])
    const [tableData, setTableData] = useState<any>()
    const [activityTableGrid, setActivityTable] = useState<any>()
    const activityDataSet = data ? data.filter(item => item?.Activity_report).flatMap((each) => Object.keys(each)) : [];
    const dataTableList = data ? data.map((data, index) => ({ ...data, id: index })) : [];
    const activity = dataTableList ? dataTableList.filter(item => item.Activity_report).map((item) => item.Activity_report) : [];
    const activityReportList = activity.length > 0 ? activity.flatMap((each) => Object.keys(each)) : [];
    const activityReportdataList = activity.map((data, index) => ({ ...data, id: index }));
    const propertyId = useAppSelector((state: RootState) => state.SpeciesFilter.propertyId)
    const organisationId = useAppSelector((state: RootState) => state.SpeciesFilter.organisationId)
    const activityId = useAppSelector((state: RootState) => state.SpeciesFilter.activityId)
    const [showReports, setShowReports] = useState(false);
    const { data: userInfoData, isLoading, isSuccess } = useGetUserInfoQuery()
    const {
        data: activityList,
        isLoading: isActivityLoading,
        isSuccess: isActivitySuccess
    } = useGetActivityAsObjQuery()

    let dataset: any[] = []
    let reportList: any[] = []
    let defaultColorWidth = {
        "Species_report": {color:"#F9A95D",width:107},
        "Property_report": {color:'#9F89BF',width:131},
        "Sampling_report": {color:"#FF5252",width:168},
        "Province_report": {color:"#FF5252",width:100},
        "Species_population_report": "#9F89BF",
        "Activity_report": checkUserRole(userInfoData) ? {color:"#696969",width:100} : {color:"#75B37A",width:100},
        "Unplanned/natural deaths": {color:"#75B37A",width:106.5},
        "Planned translocation": {color:"#F9A95D",width:106.5},
        "Planned hunt/cull": {color:"#FF5252",width:130.2},
        "Planned euthanasia": {color:"#9F89BF",width:130.2},
        "Unplanned/illegal hunting": {color:"#696969",width:147}
    }

    if (isSuccess) {
        dataset = checkUserRole(userInfoData) ? data.filter(item => !item?.Activity_report)?.flatMap((each) => Object.keys(each)) : data.flatMap((each) => Object.keys(each));
        reportList = checkUserRole(userInfoData) ? dataTableList.filter(item => !item?.Activity_report) : dataTableList;
    }
    const [customColorWidth, setCustomColorWidth] = useState<any>(defaultColorWidth)

    function checkUserRole(userInfo: UserInfo) {
        if (!userInfo?.user_roles) return false;
        // TODO : Update this to use permissions instead
        const allowedRoles = new Set(["Organisation member", "Organisation manager", "National data scientist", "Regional data scientist", "Super user"]);
        return userInfo.user_roles.some(userRole => allowedRoles.has(userRole))
    }

    useEffect(() => {
        if (activityList) {
            setCustomColorWidth({
                ...customColorWidth,
                ...Object.assign({}, ...activityList.map(
                  (x: Activity) => ({[x.name]: {color: x.colour, width: x.width}})
                )
                )
            })
        }
    }, [activityList]);

    const fetchDataList = () => {
        setLoading(true)
        axios.get(`${FETCH_AVAILABLE_DATA}?reports=${selectedInfo.replace(/ /g, '_')}&start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}&organisation=${organisationId}&activity=${activityId}&spatial_filter_values=${spatialFilterValues}`).then((response) => {
            setLoading(false)
            if (response.data) {
                setData(response.data)
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }

    useEffect(() => {
      const getData = setTimeout(() => {
        fetchDataList()
        setShowReports(true)
      }, 500)

      return () => clearTimeout(getData)
    }, [startYear, endYear])

    useEffect(() => {
        setColumns([])
        if (selectedSpecies) {
            fetchDataList()
            setShowReports(true);
        }
    }, [selectedSpecies, selectedInfo, propertyId, organisationId, activityId, spatialFilterValues])

    const handleChange = (event: SelectChangeEvent<typeof selectedColumns>) => {
        const {
            target: { value },
        } = event;
        setSelectedColumns(
            typeof value === 'string' ? value.split(',') : value,
        );
    };

    const filteredColumns = columns.filter((column) =>
        selectedColumns.length > 0 ?
            selectedColumns.includes(column.headerName) : []
    );

    const handleExportCsv = (): void => {
        const csvData = [
            columns.map((column) => column.headerName).join(','),
            ...rows.map((row: any) => columns.map((column) => row[column.field]).join(',')),
        ].join('\n');
        const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8' });
        saveAs(blob, 'data.csv');
    };

    const handleExportExcel = (): void => {
        const worksheet = XLSX.utils.json_to_sheet(rows);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Sheet 1');
        const excelData = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([excelData], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        saveAs(blob, 'data.xlsx');
    };

    useEffect(() => {
        if (!isSuccess) return;
        const dataGrid = dataset.length > 0 && dataset.map((each: any) =>
            <>
                <Box className="data-table data-grid"
                     style={{
                         backgroundColor: (customColorWidth as any)[each]?.color,
                         marginTop: '20px'
                    }}
                >
                    {getTitle(each)}
                </Box>
                {
                    reportList.length > 0 && reportList.map((item, index) => {
                        const cellData = item[each];
                        if (cellData !== undefined && cellData.length > 0) {
                            const cellKeys = Object.keys(cellData[0]);
                            const generatedColumns = cellKeys.map((key) => ({
                                field: key,
                                headerName: getTitle(key),
                                width: (customColorWidth as any)[each]?.width,
                            }));
                            for (const value of generatedColumns) {
                                if (filteredColumns.length === 0) {
                                    columns.push(value);
                                }
                            }
                            const cellRows = cellData.map((row: any, rowIndex: any) => ({
                                id: rowIndex,
                                ...row,
                            }));
                            return (
                                <DataGrid
                                    key={index}
                                    rows={cellRows}
                                    columns={selectedColumns.length > 0 ? filteredColumns : generatedColumns}
                                    disableRowSelectionOnClick
                                    components={{
                                        Pagination: null,
                                    }}
                                />
                            );
                        }
                    })
                }
            </>
        )
        const activityDataGrid = checkUserRole(userInfoData) && activityDataSet.length > 0 && activityDataSet.map((each: any) =>
            <>
                <Box className="data-table"
                     style={{
                         backgroundColor: (customColorWidth as any)[each]?.color,
                         marginTop: '20px',
                    }}
                >
                    {getTitle(each)}
                </Box>
                {activityReportList.map((each: any) =>
                    <>
                        <Box className="data-table" style={{  backgroundColor: (customColorWidth as any)[each]?.color }}>
                            {getTitle(each)}
                        </Box>
                        {activityReportdataList.length > 0 && activityReportdataList.map((item, index) => {
                            const cellData = item[each];
                            if (cellData !== undefined && cellData.length > 0) {
                                const cellKeys = cellData[0] && Object.keys(cellData[0]);
                                const generatedColumns: GridColDef[] = cellKeys.length > 0 && cellKeys.map((key) => ({
                                    field: key,
                                    headerName: getTitle(key),
                                    width: (customColorWidth as any)[each]?.width,
                                }));
                                for (const value of generatedColumns) {
                                    if (filteredColumns.length === 0) {
                                        columns.push(value);
                                    }
                                }
                                const cellRows = cellData.map((row: any, rowIndex: any) => ({
                                    id: rowIndex,
                                    ...row,
                                }));
                                return (
                                    <DataGrid
                                        key={index}
                                        rows={cellRows}
                                        columns={generatedColumns}
                                        disableRowSelectionOnClick
                                        getRowHeight={() => 'auto'}
                                        components={{
                                            Pagination: null,
                                        }}
                                    />
                                );
                            }
                        })}
                    </>
                )}
            </>)
        setActivityTable(activityDataGrid)
        const uniqueColumns = [];
        const seenFields = new Set();
        for (const column of columns) {
            if (!seenFields.has(column.field)) {
                uniqueColumns.push(column);
                seenFields.add(column.field);
            }
        }
        setColumns(uniqueColumns)
        setTableData(dataGrid)
    }, [data, selectedColumns, isSuccess])

    return (
          showReports ? (
            <Box className='dataContainer'>
                <Topper></Topper>
                <Box className="bgGreen">
                    <Box className="selectBox">
                        <FormControl fullWidth>
                            <InputLabel id="demo-simple-select-label" shrink={false}>Filter columns</InputLabel>
                            <Select
                              labelId="demo-multiple-checkbox-label"
                              id="demo-multiple-checkbox"
                              multiple
                              value={selectedColumns}
                              onChange={handleChange}
                              renderValue={(selected: any) => selected.join(', ')}
                              MenuProps={MenuProps}
                            >
                                {columns.map((column) => (
                                  <MenuItem key={column.headerName} value={column.headerName}>
                                      <Checkbox checked={selectedColumns.indexOf(column.headerName) > -1} />
                                      <ListItemText primary={column.headerName} />
                                  </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Box>
                </Box>
                {loading ? <Loading /> :
                  <Box className="dataTable-auto">
                      <Box className="dataTable">
                          {data.length > 0 ?
                            <Box>{tableData}
                                {activityTableGrid}
                            </Box> :
                            <Typography>
                                No Data To Show
                            </Typography>}
                      </Box>
                  </Box>}
                {loading ? <Loading/> : (
                  <Box className="downlodBtn">
                    <Button onClick={handleExportExcel} variant="contained" color="primary">
                        Download data Report
                    </Button>
                    <Button onClick={handleExportCsv} variant="contained" color="primary">
                        Download data CSV
                    </Button>
                </Box>
                )}
            </Box>
          ) : (
            <Grid container justifyContent="center" alignItems="center" flexDirection={'column'}>
                <Grid item>
                    <Typography variant="body1" color="textPrimary" style={{ fontSize: '20px', fontWeight: 'bold' }}>
                        Ready to explore?
                    </Typography>
                </Grid>
                <Grid>
                    <Typography variant="body1" color="textPrimary" style={{ fontSize: '16px', fontWeight: 'bold' }}>
                        Choose a species to view the data as table.
                    </Typography>
                </Grid>
            </Grid>
          )
    )
}

export default DataList

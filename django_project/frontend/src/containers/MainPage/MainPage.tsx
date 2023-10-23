import React, { useEffect, useState } from 'react';
import {useSearchParams, useLocation, useNavigate} from "react-router-dom";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import {RootState} from '../../app/store';
import {useAppDispatch, useAppSelector } from '../../app/hooks';
import TabPanel, { a11yProps } from '../../components/TabPanel';
import {
  LeftSideBar,
  RightSideBar,
  LayerFilterTabs
} from './SideBar';
import Upload from './Upload';
import Map from './Map';
import './index.scss';
import { PropertySummary } from './Property';
import { MapSelectionMode } from "../../models/Map";
import { UploadMode } from "../../models/Upload";
import {
    setUploadState
} from '../../reducers/UploadState';
import {
    setSelectedParcels,
    resetSelectedProperty,
    setMapSelectionMode,
    resetMapState
} from '../../reducers/MapState';
import DataList from './Data';
import Metrics from './Metrics';
import Trends from './Trends';




enum RightSideBarMode {
  None = -1,
  Upload = 0,
  PropertySummary = 1,
  FilteredResult = 2
}

function MainPage() {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const uploadMode = useAppSelector((state: RootState) => state.uploadState.uploadMode)
  const [rightSideBarMode, setRightSideBarMode] = useState(RightSideBarMode.None) // 0: upload data, 1: property summary, 2: filtered properties summary
  const propertyItem = useAppSelector((state: RootState) => state.mapState.selectedProperty)
  const mapSelectionMode = useAppSelector((state: RootState) => state.mapState.selectionMode)

  const initialTabParam = new URLSearchParams(location.search).get('tab');
  const initialSelectedTab = initialTabParam !== null ? parseInt(initialTabParam) : 0;
  const [selectedTab, setSelectedTab] = useState(initialSelectedTab);
  const isUploadUrl = location.pathname === '/upload';

  const tabNameToValue: { [key: string]: number } = {
    'map': 0,
    'reports': 1,
    'charts': 2,
    'trends': 3,
    'upload': 4,
  };

  useEffect(() => {
    const tabParam = new URLSearchParams(location.search).get('tab');
    if (tabParam !== null) {
      const tabName = Object.keys(tabNameToValue).find(key => tabNameToValue[key] === parseInt(tabParam));
      if (tabName) {
        setSelectedTab(tabNameToValue[tabName]); // Set the selected tab based on URL parameter
      }
    }
  }, [location.search]);

  useEffect(() => {
    const tabNames = ['map', 'reports', 'charts', 'trends', 'upload'];
    const selectedTabName = tabNames[selectedTab];
    const newPath = `/${selectedTabName}`;
    if ([1, 2, 3].includes(selectedTab)) {
      // dispatch to reset map state in data or charts tab
      dispatch(resetMapState())
    }
    if (location.pathname !== newPath) {
      navigate(newPath); // Update the URL with the tab name
    }

    if (isUploadUrl) {
      setRightSideBarMode(RightSideBarMode.Upload);
      dispatch(setUploadState(UploadMode.SelectProperty));
      return; //hide all tabs
    }

    // Replace the tab parameter in the URL
    const newUrl = window.location.href.replace(/\?tab=\d/, newPath);
    window.history.replaceState(null, '', newUrl);
  }, [selectedTab, navigate, location.pathname, isUploadUrl]);



  useEffect(() => {
    if (rightSideBarMode === RightSideBarMode.None) {
      dispatch(setUploadState(UploadMode.None))
      dispatch(setMapSelectionMode(MapSelectionMode.Property))
      dispatch(resetSelectedProperty())
      dispatch(setSelectedParcels([]))
    }
  }, [rightSideBarMode])

  useEffect(() => {
    if (mapSelectionMode === MapSelectionMode.Property && uploadMode === UploadMode.None) {
      if (propertyItem.id > 0) {
        // show right side bar
        setRightSideBarMode(RightSideBarMode.PropertySummary)
      } else {
        setRightSideBarMode(RightSideBarMode.None)
      }
    } else if (uploadMode === UploadMode.PropertySelected && rightSideBarMode !== RightSideBarMode.Upload) {
      setSelectedTab(4)
      setRightSideBarMode(RightSideBarMode.Upload)
    }
  }, [propertyItem, mapSelectionMode, uploadMode])

  return (
    <div className="App">
      <div className="MainPage">
        <Grid container flexDirection={'row'}>
          <Grid item>
            { rightSideBarMode === RightSideBarMode.Upload ? <LeftSideBar element={Upload} /> : <LeftSideBar element={LayerFilterTabs} additionalProps={{
              'selectedMainTabIdx': selectedTab
            }} />}
          </Grid>
          <Grid item flex={1} className="grayBg customWidth">
            <Grid container className="Content" flexDirection={'column'}>
              <Grid item>
              <Box className="TabHeaders" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                {rightSideBarMode === RightSideBarMode.Upload || isUploadUrl ? null : (
                  <Tabs
                    value={selectedTab}
                    onChange={(event: React.SyntheticEvent, newValue: number) => {
                      const tabNames = ['map', 'reports', 'charts', 'trends', 'upload'];
                      const selectedTabName = tabNames[newValue];
                      setSelectedTab(newValue);
                      if (selectedTabName === 'upload') {
                        setRightSideBarMode(RightSideBarMode.Upload);
                        dispatch(setUploadState(UploadMode.SelectProperty));
                      } else {
                        setRightSideBarMode(RightSideBarMode.None);
                      }
                      navigate(`/${selectedTabName}`);
                    }}
                    aria-label="Main Page Tabs"
                  >
                    <Tab key={0} label={'MAP'} {...a11yProps(0)} />
                    <Tab key={1} label={'REPORTS'} {...a11yProps(1)} />
                    <Tab key={2} label={'CHARTS'} {...a11yProps(2)} />
                    <Tab key={3} label={'TRENDS'} {...a11yProps(3)} />
                  </Tabs>
                )}
                <div style={{ flex: 1 }}></div>
              </Box>

              </Grid>
              <Grid item className="TabPanels">
                <TabPanel key={0} value={selectedTab} index={-1} indexList={[0, 4]} noPadding>
                  <Map />
                </TabPanel>
                <TabPanel key={1} value={selectedTab} index={1} noPadding>
                  <DataList/>
                </TabPanel>
                <TabPanel key={2} value={selectedTab} index={2} noPadding>
                  <Metrics/>
                </TabPanel>
                <TabPanel key={3} value={selectedTab} index={3} noPadding>
                  <Trends/>
                </TabPanel>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
        { rightSideBarMode === RightSideBarMode.PropertySummary ? <RightSideBar element={PropertySummary} /> : null}
      </div>
    </div>
  );
}

export default MainPage;

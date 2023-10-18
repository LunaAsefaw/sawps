import React, { useState, useEffect } from 'react';
import Box from "@mui/material/Box";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import TabPanel, { a11yProps } from '../../../components/TabPanel';
import Layers from './Layers';
import './index.scss';
import Filter from './Filter';
import {isMapDisplayed} from "../../../utils/Helpers";

function LayerFilterTabs(props: { selectedMainTabIdx: number }) {
    const [selectedTabSideBar, setSelectedTabSideBar] = useState(0);
    const [showLayerFilter, setLayerFilter] = useState(false);

    useEffect(() => {
        // Check if the URL contains a pattern that indicates the presence of charts
        if (
          isMapDisplayed()
        ) {
            setLayerFilter(false);
        } else setLayerFilter(true)
        setSelectedTabSideBar(1);

    }, [props.selectedMainTabIdx]);

    return (
        <Box className='LeftSideBar'>
            <Box className='TabHeaders'>
                <Tabs value={selectedTabSideBar}
                    onChange={(event: React.SyntheticEvent, newValue: number) => {
                        if (isMapDisplayed()) {
                            setSelectedTabSideBar(newValue);
                        }
                    }} aria-label="Left Side Bar Tabs"
                    centered={showLayerFilter}
                >
                    {!showLayerFilter && (
                        <Tab key={0} label={'LAYERS'} {...a11yProps(0)} />
                     )}

                    <Tab key={1} label={'FILTERS'} {...a11yProps(1)} />
                </Tabs>
            </Box>
            <Box className='TabPanels FlexContainerFill'>
                <Box className='LeftSideBarContent'>
                    {!showLayerFilter && (
                        <TabPanel key={0} value={selectedTabSideBar} index={0} noPadding>
                            <Layers />
                        </TabPanel>
                    )}
                    <TabPanel key={1} value={selectedTabSideBar} index={1} noPadding>
                        <Filter />
                    </TabPanel>
                </Box>
            </Box>
        </Box>
    );
}

export default LayerFilterTabs;

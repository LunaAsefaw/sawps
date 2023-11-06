import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import ParcelInterface from "../models/Parcel";
import { MapSelectionMode, MapEventInterface, MapTheme, PopulationCountLegend } from "../models/Map";
import PropertyInterface, { createNewProperty } from "../models/Property";
import { UploadMode } from "../models/Upload";

const DEFAULT_SELECTION_MODE = MapSelectionMode.Property


export interface MapStateInterface {
    isMapReady: boolean;
    selectionMode: MapSelectionMode; // none, property, parcel, digitise, parcelJSON,
    selectedParcels: ParcelInterface[];
    selectedProperty: PropertyInterface;
    mapEvents: MapEventInterface[];
    theme: MapTheme;
    provinceCounts: PopulationCountLegend[];
    propertiesCounts: PopulationCountLegend[];
    dynamicMapSession: string; // this session is used for filtering of the property
    selectedSpeciesName: string;
}

const initialState: MapStateInterface = {
    isMapReady: false,
    selectionMode: DEFAULT_SELECTION_MODE,
    selectedParcels: [],
    selectedProperty: createNewProperty(),
    mapEvents: [],
    theme: MapTheme.Light,
    provinceCounts: [],
    propertiesCounts: [],
    dynamicMapSession: '',
    selectedSpeciesName: ''
}

/* reset all selectedParcels */
const resetSelectedParcels = (parcels: ParcelInterface[]): ParcelInterface[] => {
    let _selection = [...parcels]
    _selection.forEach(function(item, index, object) {
        item.isRemoved = true
    })
    return _selection
}


export const MapStateSlice = createSlice({
    name: 'MapState',
    initialState,
    reducers: {
        setMapReady: (state, action: PayloadAction<boolean>) => {
            state.isMapReady = action.payload
        },
        setMapSelectionMode: (state, action: PayloadAction<MapSelectionMode>) => {
            state.selectionMode = action.payload
        },
        toggleDigitiseSelectionMode: (state, action: PayloadAction<null>) => {
            if (state.selectionMode === MapSelectionMode.Digitise) {
                state.selectionMode = DEFAULT_SELECTION_MODE
            } else {
                state.selectionMode = MapSelectionMode.Digitise
            }
        },
        toggleParcelSelectionMode: (state, action: PayloadAction<UploadMode>) => {
            // reset selectedProperty if uploadMode is None
            if (action.payload === UploadMode.None) {
                state.selectedProperty = createNewProperty()
            }
            if (state.selectionMode === MapSelectionMode.Parcel) {
                // disable parcel selection mode
                state.selectionMode = DEFAULT_SELECTION_MODE
                if (action.payload !== UploadMode.PropertySelected && action.payload !== UploadMode.CreateNew) {
                    // remove selectedParcels if not selected parcel mode
                    state.selectedParcels = resetSelectedParcels(state.selectedParcels)
                }
            } else {
                state.selectionMode = MapSelectionMode.Parcel
            }
        },
        toggleParcelSelectedState: (state, action: PayloadAction<ParcelInterface>) => {
            let _idx = state.selectedParcels.findIndex((element) => element.id === action.payload.id && element.layer === action.payload.layer)
            if (_idx > -1) {
                // remove selection
                let _selection = [...state.selectedParcels]
                _selection[_idx].isRemoved = true
                state.selectedParcels = _selection
            } else {
                state.selectedParcels = [...state.selectedParcels, action.payload]
            }
        },
        setSelectedParcels: (state, action: PayloadAction<ParcelInterface[]>) => {
            // current selectedParcels must be empty or the action.payload must be empty
            if (state.selectedParcels.length === 0 && action.payload.length) {
                state.selectedParcels = [...action.payload]
            } else if (state.selectedParcels.length > 0 && action.payload.length === 0) {
                // remove selectedParcels if not selected parcel mode
                state.selectedParcels = resetSelectedParcels(state.selectedParcels)
            }
        },
        setSelectedProperty: (state, action: PayloadAction<PropertyInterface>) => {
            state.selectedProperty = {...action.payload}
        },
        resetSelectedProperty: (state, action: PayloadAction<null>) => {
            // reset selectedProperty
            state.selectedProperty = createNewProperty()
        },
        selectedParcelsOnRenderFinished: (state, action: PayloadAction<null>) => {
            // called when selected parcels have been rendered
            let _selection = [...state.selectedParcels]
            _selection.forEach(function(item, index, object) {
                if (item.isRemoved) {
                  object.splice(index, 1);
                }
            })
            state.selectedParcels = _selection
        },
        triggerMapEvent: (state, action: PayloadAction<MapEventInterface>) => {
            state.mapEvents = [...state.mapEvents, action.payload]
        },
        onMapEventProcessed: (state, action: PayloadAction<MapEventInterface[]>) => {
            let _events = [...state.mapEvents]
            _events.forEach(function(item, index, object) {
                if (action.payload.find((e: MapEventInterface) => e.id === item.id)) {
                    object.splice(index, 1)
                }
            })
            state.mapEvents = _events
        },
        toggleMapTheme: (state, action: PayloadAction<null>) => {
            if (state.theme === MapTheme.Light) {
                state.theme = MapTheme.Dark
            } else if (state.theme === MapTheme.Dark) {
                state.theme = MapTheme.Light
            }
        },
        setInitialMapTheme: (state, action: PayloadAction<MapTheme>) => {
            state.theme = action.payload
        },
        resetMapState: (state, action: PayloadAction<null>) => {
            state.isMapReady = false
            state.selectionMode = DEFAULT_SELECTION_MODE
            state.selectedParcels = []
            state.selectedProperty = createNewProperty()
            state.mapEvents = []
            state.provinceCounts = []
            state.propertiesCounts = []
        },
        setPopulationCountLegends: (state, action: PayloadAction<PopulationCountLegend[][]>) => {
            state.provinceCounts = [...action.payload[0]]
            state.propertiesCounts = [...action.payload[1]]
        },
        setDynamicMapSession: (state, action: PayloadAction<string>) => {
            state.dynamicMapSession = action.payload
        }
    }
})

export const {
    setMapReady,
    setMapSelectionMode,
    toggleDigitiseSelectionMode,
    toggleParcelSelectionMode,
    toggleParcelSelectedState,
    setSelectedParcels,
    setSelectedProperty,
    resetSelectedProperty,
    selectedParcelsOnRenderFinished,
    triggerMapEvent,
    onMapEventProcessed,
    toggleMapTheme,
    setInitialMapTheme,
    resetMapState,
    setPopulationCountLegends,
    setDynamicMapSession
} = MapStateSlice.actions

export default MapStateSlice.reducer;
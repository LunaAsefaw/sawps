import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import SpeciesLayer from "../models/SpeciesLayer";

export interface SpeciesFilterInterface {
  SpeciesFilterList: SpeciesLayer[];
  selectedSpecies: string;
  months: string[];
  selectedMonths: string;
  startYear: number;
  endYear: number;
  propertyId:string;
  selectedInfoList: string;
  organisationId:string;
  activityId:string;
  spatialFilterValues: string,
  activityName: string,
  propertyName:string;
  organisationName:string;
}

const initialState: SpeciesFilterInterface = {
  SpeciesFilterList: [],
  selectedSpecies: "",
  months: [],
  selectedMonths: "",
  startYear: 1960,
  endYear:new Date().getFullYear(),
  propertyId:"",
  selectedInfoList:"",
  organisationId:"",
  activityId:"",
  spatialFilterValues: "",
  activityName: "",
  propertyName:"",
  organisationName: ""
};

export const SpeciesFilterSlice = createSlice({
  name: 'SpeciesFilter',
  initialState,
  reducers: {
    setSpeciesFilter: (state, action: PayloadAction<SpeciesLayer[]>) => {
      state.SpeciesFilterList = [...action.payload];

      const selectedSpecies = action.payload
        .filter(obj => obj.is_selected)
        .map(obj => obj.common_name_varbatim);
      state.selectedSpecies = selectedSpecies.join(',');
    },
    setSelectedSpecies: (state, action: PayloadAction<number[]>) => {
      let _updatedData = state.SpeciesFilterList.map((species) => {
        if (action.payload.includes(species.id)) {
          species.is_selected = true;
        } else {
          species.is_selected = false;
        }
        return species;
      });
      state.SpeciesFilterList = [..._updatedData];

      const selectedSpecies = _updatedData
        .filter(obj => obj.is_selected)
        .map(obj => obj.common_name_varbatim);
      state.selectedSpecies = selectedSpecies.join(',');
    },
    toggleSpecies: (state, action: PayloadAction<string>) => {
      state.selectedSpecies = action.payload;
    },
    setSelectedInfoList: (state, action: PayloadAction<string>) => {
      state.selectedInfoList = action.payload;
    },

    selectedPropertyId: (state, action: PayloadAction<string>) => {
      state.propertyId = action.payload;
    },

    selectedOrganisationId: (state, action: PayloadAction<string>) => {
      state.organisationId = action.payload;
    },
    selectedActivityId: (state, action: PayloadAction<string>) => {
      state.activityId = action.payload;
    },
    setMonths: (state, action: PayloadAction<string[]>) => {
      state.months = [...action.payload];
      state.selectedMonths = action.payload.join(',');
    },

    setStartYear: (state, action: PayloadAction<number>) => {
      state.startYear = action.payload;
    },

    setEndYear: (state, action: PayloadAction<number>) => {
      state.endYear = action.payload;
    },
    setSpatialFilterValues: (state, action: PayloadAction<string[]>) => {
      state.spatialFilterValues = action.payload.join(',');
    },
    selectedActivityName: (state, action: PayloadAction<string>) => {
      state.activityName = action.payload;
    },
    selectedPropertyName: (state, action: PayloadAction<string>) => {
      state.propertyName = action.payload;
    },
    selectedOrganisationName: (state, action: PayloadAction<string>) => {
      state.organisationName = action.payload;
    }
  },
});

export const {
  setSpeciesFilter,
  toggleSpecies,
  setSelectedSpecies,
  selectedPropertyId,
  selectedOrganisationId,
  selectedActivityId,
  setMonths,
  setStartYear,
  setEndYear,
  setSelectedInfoList,
  setSpatialFilterValues,
  selectedActivityName,
  selectedPropertyName,
  selectedOrganisationName
} = SpeciesFilterSlice.actions;

export default SpeciesFilterSlice.reducer;

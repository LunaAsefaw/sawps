import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import LayerFilterReducer from '../reducers/LayerFilter';
import MapStateReducer from '../reducers/MapState';
import UploadStateReducer from '../reducers/UploadState';
import SpeciesFilterReducer from '../reducers/SpeciesFilter';
import {userApi} from "../services/api";


export const store = configureStore({
    reducer: {
      layerFilter: LayerFilterReducer,
      mapState: MapStateReducer,
      uploadState: UploadStateReducer,
      SpeciesFilter:SpeciesFilterReducer,
      [userApi.reducerPath]: userApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware().concat(userApi.middleware)
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;

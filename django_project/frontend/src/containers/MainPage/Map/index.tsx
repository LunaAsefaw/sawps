import React, { useRef, useEffect, useCallback, useState } from 'react';
import axios from 'axios';
import {v4 as uuidv4} from 'uuid';
import maplibregl, {Map as MapLibreMap, FeatureIdentifier, IControl} from 'maplibre-gl';
import MapboxDraw, { constants as MapboxDrawConstant } from '@mapbox/mapbox-gl-draw';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import {RootState} from '../../../app/store';
import { debounce } from '@mui/material/utils';
import {useAppDispatch, useAppSelector } from '../../../app/hooks';
import {
  setMapReady,
  toggleParcelSelectedState,
  setSelectedProperty,
  resetSelectedProperty,
  selectedParcelsOnRenderFinished,
  onMapEventProcessed,
  toggleDigitiseSelectionMode,
  setSelectedParcels,
  toggleParcelSelectionMode,
  triggerMapEvent,
  toggleMapTheme,
  setPopulationCountLegends,
  setDynamicMapSession
} from '../../../reducers/MapState';
import ParcelInterface from '../../../models/Parcel';
import { MapSelectionMode, MapTheme, MapEvents, PopulationCountLegend } from "../../../models/Map";
import { UploadMode } from "../../../models/Upload";
import './index.scss';
import CustomNavControl from './NavControl';
import {
  checkLayerVisibility,
  renderHighlightParcelLayers,
  removeHighlightParcelLayers,
  findParcelLayer,
  searchParcel,
  searchProperty,
  getSelectParcelLayerNames,
  MIN_SELECT_PARCEL_ZOOM_LEVEL,
  MIN_SELECT_PROPERTY_ZOOM_LEVEL,
  findAreaLayers,
  isContextLayerSelected,
  getMapPopupDescription,
  addParcelInvisibleFillLayers,
  drawPropertiesLayer,
  MAX_PROVINCE_ZOOM_LEVEL,
  MIN_PROVINCE_ZOOM_LEVEL,
  showExtrudeLayer,
  removeExtrudeLayer
} from './MapUtility';
import PropertyInterface from '../../../models/Property';
import CustomDrawControl from './CustomDrawControl';
import LoadingIndicatorControl from './LoadingIndicatorControl';
import {useGetUserInfoQuery} from "../../../services/api";
import LegendControl from './LegendControl';

const MAP_STYLE_URL = window.location.origin + '/api/map/styles/'
const MAP_PROPERTIES_LEGENDS_URL = '/api/map/legends/properties/'
const MAP_SOURCES = ['sanbi', 'sanbi-dynamic', 'NGI Aerial Imagery']
const AERIAL_SOURCE_ID = 'NGI Aerial Imagery'

const TIME_QUERY_PARAM_REGEX = /\?t=\d+.*/
const UPLOAD_FILE_URL = '/api/upload/boundary-file/'

// @ts-ignore
const _csrfToken = csrfToken || '';

const uploadGeoJsonFile = (geojson: string, session: string, callback: (success: boolean, error?: any) => void) => {
  const body = new FormData()
  let _blob = new Blob([geojson], {type: 'application/geo+json'})
  let _file = new File([_blob], `digitise_${session}.geojson`)
  body.append('file', _file)
  body.append('meta_id', uuidv4())
  body.append('session', session)
  const headers = {
    'Content-Disposition': `attachment; filename=digitise_${session}.geojson`,
    'X-CSRFToken': _csrfToken,
    'Content-Type': 'multipart/form-data'
  }
  axios.post(UPLOAD_FILE_URL, body, {
    headers: headers
  }).then((response) => {
    callback(true)
  }).catch((error) => {
    callback(false, error)
  })
}

const getEmptyFeature = (): FeatureIdentifier => {
  return {
    id: '',
    source: '',
    sourceLayer: ''
  }
}

interface MapInterface {
  isDataUpload?: boolean
}

export default function Map(props: MapInterface) {
  const dispatch = useAppDispatch()
  const contextLayers = useAppSelector((state: RootState) => state.layerFilter.contextLayers)
  const isMapReady = useAppSelector((state: RootState) => state.mapState.isMapReady)
  const selectionMode = useAppSelector((state: RootState) => state.mapState.selectionMode)
  const selectedParcels = useAppSelector((state: RootState) => state.mapState.selectedParcels)
  const selectedProperty = useAppSelector((state: RootState) => state.mapState.selectedProperty)
  const uploadMode = useAppSelector((state: RootState) => state.uploadState.uploadMode)
  const mapEvents = useAppSelector((state: RootState) => state.mapState.mapEvents)
  const mapTheme = useAppSelector((state: RootState) => state.mapState.theme)
  const [zoom, setZoom] = useState(5)
  const [show3dLayer, setShow3dLayer] = useState(false)
  const mapContainer = useRef(null);
  const map = useRef(null);
  const mapDraw = useRef(null);
  const mapDrawLoading = useRef(null);
  const [savingBoundaryDigitise, setSavingBoundaryDigitise] = useState(false)
  const [boundaryDigitiseSession, setBoundaryDigitiseSession] = useState(null)
  const mapNavControl = useRef(null)
  const mapPopupRef = useRef(null)
  const mapLegendControlRef = useRef(null)
  const [highlightedParcel, setHighlightedParcel] = useState<FeatureIdentifier>(getEmptyFeature())
  // Map Properties Filters
  const selectedSpecies = useAppSelector((state: RootState) => state.SpeciesFilter.selectedSpecies)
  const startYear = useAppSelector((state: RootState) => state.SpeciesFilter.startYear)
  const endYear = useAppSelector((state: RootState) => state.SpeciesFilter.endYear)
  const spatialFilterValues = useAppSelector((state: RootState) => state.SpeciesFilter.spatialFilterValues)
  const propertyId = useAppSelector((state: RootState) => state.SpeciesFilter.propertyId)
  const organisationId = useAppSelector((state: RootState) => state.SpeciesFilter.organisationId)
  const activityId = useAppSelector((state: RootState) => state.SpeciesFilter.activityId)
  const provinceCounts = useAppSelector((state: RootState) => state.mapState.provinceCounts)
  const propertiesCounts = useAppSelector((state: RootState) => state.mapState.propertiesCounts)
  const dynamicMapSession = useAppSelector((state: RootState) => state.mapState.dynamicMapSession)
  const { data: userInfoData, isLoading, isSuccess } = useGetUserInfoQuery()
  // for properties legend API
  const axiosSource = useRef(null)
  const newCancelToken = useCallback(() => {
      axiosSource.current = axios.CancelToken.source();
      return axiosSource.current.token;
    }, [])

  const onMapMouseEnter = () => {
    if (!map.current) return;
    // Change the cursor style as a UI indicator.
    map.current.getCanvas().style.cursor = 'pointer';
  }

  const onMapMouseLeave = () => {
    if (!map.current) return;
    map.current.getCanvas().style.cursor = '';
  }

  /* Map Draw (Digitise) Mode  */
  const getBoundaryDigitiseStatus = (session: string) => {
    axios.get(`${UPLOAD_FILE_URL}${session}/status/`).then((response) => {
        if (response.data) {
            let _status = response.data['status']
            if (_status === 'DONE') {
                setSavingBoundaryDigitise(false)
                let _parcels = response.data['parcels'] as ParcelInterface[]
                dispatch(setSelectedParcels(_parcels))
                onDrawCancelled(true)
                // trigger map zoom to bbox
                let _bbox = response.data['bbox']
                if (_bbox && _bbox.length === 4) {
                    let _bbox_str = _bbox.map(String)
                    dispatch(triggerMapEvent({
                        'id': uuidv4(),
                        'name': MapEvents.BOUNDARY_FILES_UPLOADED,
                        'date': Date.now(),
                        'payload': _bbox_str
                    }))
                }
                removeDrawMapLoadingIndicator()
            } else if (_status === 'ERROR') {
                setSavingBoundaryDigitise(false)
                alert('There is unexpected error! Please try again!')
                removeDrawMapLoadingIndicator()
            }
        }
    }).catch((error) => {
        console.log(error)
        setSavingBoundaryDigitise(false)
        removeDrawMapLoadingIndicator()
        alert('There is unexpected error! Please try again!')
    })
  }

  const showDrawMapLoadingIndicator = () => {
    let _mapObj: MapLibreMap = map.current
    let _drawObj: CustomDrawControl = mapDraw.current
    let _loading = new LoadingIndicatorControl({
      label: 'Processing Geometries...'
    })
    mapDrawLoading.current = _loading
    _mapObj.addControl(_loading, 'top-left')
    _drawObj.disableButtons()
  }

  const removeDrawMapLoadingIndicator = () => {
    if (!mapDrawLoading.current) return;
    let _mapObj: MapLibreMap = map.current
    let _drawObj: CustomDrawControl = mapDraw.current
    _mapObj.removeControl(mapDrawLoading.current)
    if (_drawObj) {
      _drawObj.enableButtons()
    }
    mapDrawLoading.current = null
  }

  const onDrawSaved = () => {
    if (!mapDraw.current) return;
    let _mapObj: MapLibreMap = map.current
    let _drawObj: CustomDrawControl = mapDraw.current
    let _mapBoxDraw = _drawObj.getMapBoxDraw()
    // get the features from drawing
    let _geojson = JSON.stringify(_mapBoxDraw.getAll())
    // change to simple_select mode
    _mapBoxDraw.changeMode(MapboxDrawConstant.modes.SIMPLE_SELECT)
    // show backdrop processing
    showDrawMapLoadingIndicator()
    let _session = uuidv4()
    setBoundaryDigitiseSession(_session)
    // call API
    uploadGeoJsonFile(_geojson, _session, (isSuccess, error) => {
      if (isSuccess) {
        axios.get(`${UPLOAD_FILE_URL}${_session}/search/`).then((response) => {
            setSavingBoundaryDigitise(true)
            dispatch(setSelectedParcels([]))
        }).catch((error) => {
            console.log(error)
            removeDrawMapLoadingIndicator()
            alert('There is unexpected error! Please try again!')
        })
      } else {
        console.log(error)
        removeDrawMapLoadingIndicator()
        alert('There is unexpected error! Please try again!')
      }
    })
  }

  const onDrawCancelled = (success?: boolean) => {
    if (!mapDraw.current) return;
    let _mapObj: maplibregl.Map = map.current
    _mapObj.removeControl(mapDraw.current)
    mapDraw.current = null
    if (success) {
      dispatch(toggleParcelSelectionMode(uploadMode))
    } else {
      dispatch(toggleDigitiseSelectionMode())
    }
  }

  const createMapDrawTool = () => {
    // add mapbox draw
    let _draw = new MapboxDraw({
      displayControlsDefault: false,
      controls: {
        polygon: true,
        trash: true
      }
    })
    let _save_button = document.createElement('span')
    _save_button.className = 'mapboxgl-ctrl-icon'
    _save_button.title = 'Save'
    _save_button.ariaLabel = 'Save'

    let _cancel_button = document.createElement('span')
    _cancel_button.className = 'mapboxgl-ctrl-icon'
    _cancel_button.title = 'Cancel'
    _cancel_button.ariaLabel = 'Cancel'
    return new CustomDrawControl({
      draw: _draw,
      buttons: [{
        on: 'click',
        action: onDrawSaved,
        classes: ['maplibregl-ctrl-draw-save'],
        content: _save_button
      }, {
        on: 'click',
        action: onDrawCancelled,
        classes: ['maplibregl-ctrl-draw-cancel'],
        content: _cancel_button
      }]
    })
  }
  /* End of Map Draw (Digitise) Mode  */

  /* Map Legend functions */
  const updateMapLegends = (currentZoom: number, species: string, provinceCountData: PopulationCountLegend[], propertiesCountData: PopulationCountLegend[]) => {
    if (!mapLegendControlRef.current) return;
    let _legendObj: LegendControl<IControl> = mapLegendControlRef.current
    if (species) {
      if (currentZoom >= MIN_PROVINCE_ZOOM_LEVEL && currentZoom <= MAX_PROVINCE_ZOOM_LEVEL && provinceCountData) {
        _legendObj.onUpdateLegends(currentZoom, species, provinceCountData)
      } else if (currentZoom > MAX_PROVINCE_ZOOM_LEVEL && propertiesCountData) {
        _legendObj.onUpdateLegends(currentZoom, species, propertiesCountData)
      } else {
        _legendObj.onClearLegends()
      }
    } else {
      _legendObj.onClearLegends()
    }
  }
  /* End of Map Legend functions */


  /* Listen to context layers change (isSelected) */
  useEffect(() => {
    if (!isMapReady) return;
    if (contextLayers.length === 0) return;
    if (!map.current) return;
    const _mapObj: maplibregl.Map = map.current
    const _layers = _mapObj.getStyle().layers
    for (let i=0; i < _layers.length; ++i) {
      let _layer:any = _layers[i]
      // skip any layer that is not from sanbi and property sources
      if (!('source' in _layer) || !MAP_SOURCES.includes(_layer['source'])) continue
      // skip if no source-layer and not NGI aerial imagery
      if (!('source-layer' in _layer) && _layer['source'] !== AERIAL_SOURCE_ID) continue
      // skip if current selection mode is parcel selection and highlighted layer for selecting parcel
      if (selectionMode === MapSelectionMode.Parcel && _layer['id'].includes('-select-parcel')) continue
      let _source_layer = 'source-layer' in _layer ? _layer['source-layer'] : _layer['source']
      const _is_visible = checkLayerVisibility(_source_layer, contextLayers)
      _mapObj.setLayoutProperty(_layer['id'], 'visibility', _is_visible ? 'visible' : 'none')
    }

    let _parcelLayer = findParcelLayer(contextLayers)
    let _selectParcelLayers = getSelectParcelLayerNames(_parcelLayer.layer_names)
    for (let i=0; i < _selectParcelLayers.length; ++i) {
      _mapObj.on('mouseenter', _selectParcelLayers[i], onMapMouseEnter)
      _mapObj.on('mouseleave', _selectParcelLayers[i], onMapMouseLeave)
    }
    return () => {
      for (let i=0; i < _selectParcelLayers.length; ++i) {
        _mapObj.off('mouseenter', _selectParcelLayers[i], onMapMouseEnter)
        _mapObj.off('mouseleave', _selectParcelLayers[i], onMapMouseLeave)
      }
    }
  }, [contextLayers, isMapReady])

  /* Called when selectionMode is changed */
  useEffect(() => {
    if (!isMapReady) return;
    if (contextLayers.length === 0) return;
    if (!map.current) return;

    let _mapObj: maplibregl.Map = map.current
    let _parcelLayer = findParcelLayer(contextLayers)
    if (typeof _parcelLayer === 'undefined') return;
    if (selectionMode === MapSelectionMode.Parcel) {
      renderHighlightParcelLayers(_mapObj, _parcelLayer.layer_names)
    } else {
      removeHighlightParcelLayers(_mapObj, _parcelLayer.layer_names)
    }
    if (selectionMode === MapSelectionMode.Digitise) {
      // add Draw Control to the map
      if (!mapDraw.current) {
        mapDraw.current = createMapDrawTool()
        _mapObj.addControl(mapDraw.current, 'top-left')
      }
    } else {
      if (mapDraw.current) {
        _mapObj.removeControl(mapDraw.current)
        mapDraw.current = null
      }
    }
  }, [selectionMode])

  /* Called when mapTheme is changed */
  const mapStyleOnLoaded = useCallback(() => {
    if (map.current.style._loaded) {
      dispatch(setMapReady(true))
      setTimeout(() => {  
        if (selectedSpecies.length > 0) {
          drawPropertiesLayer(true, map.current, mapTheme, false, propertiesCounts, provinceCounts)
        } else {
          drawPropertiesLayer(false, map.current, mapTheme, false)
        }
      }, 300)
      let enableParcelLayers = true;
      if (userInfoData) {
        for (let userRole of userInfoData.user_roles) {
          if (userRole.toLowerCase().includes('decision maker')) {
            enableParcelLayers = false
          }
        }
      }
      if(enableParcelLayers)
        addParcelInvisibleFillLayers(map.current)
    }
  }, [mapTheme, selectedSpecies, provinceCounts, propertiesCounts])

  /* Called when zoom is changed */
  useEffect(() => {
    if (!map.current) return;
    if (!isMapReady) return;
    // update the legends if we need to show it
    if (mapLegendControlRef.current) {
      let _legendObj: LegendControl<IControl> = mapLegendControlRef.current
      if (_legendObj.getCurrentZoom() === zoom) return;
      updateMapLegends(zoom, selectedSpecies, provinceCounts, propertiesCounts)
    }
  }, [zoom])

  useEffect(() => {
    if (!selectedSpecies) return;
    if (show3dLayer) {
      showExtrudeLayer(map.current, provinceCounts, propertiesCounts)
    } else {
      removeExtrudeLayer(map.current)
    }
  }, [show3dLayer, selectedSpecies, provinceCounts, propertiesCounts])

  useEffect(() => {
    if (mapTheme === MapTheme.None) return;
    if (!isSuccess) return;
    let _styleURL = `${MAP_STYLE_URL}?theme=${mapTheme}`
    if (dynamicMapSession) {
      _styleURL = _styleURL + `&session=${dynamicMapSession}`
    }
    if (map.current) {
      dispatch(setMapReady(false))
      map.current.on('styledata', mapStyleOnLoaded)
      map.current.setStyle(_styleURL)
      if (mapNavControl.current) {
        mapNavControl.current.updateThemeSwitcherIcon(mapTheme)
      }
      if (mapLegendControlRef.current) {
        mapLegendControlRef.current.onThemeChanged(mapTheme)
      }
    } else {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: _styleURL,
        minZoom: 5
      })
      // add exporter dialog
      mapNavControl.current = new CustomNavControl({
        showZoom: true,
        visualizePitch: true
      }, {
        initialTheme: mapTheme,
        onThemeSwitched: () => { dispatch(toggleMapTheme()) }
      })
      mapLegendControlRef.current = new LegendControl()
      map.current.addControl(mapNavControl.current, 'bottom-left')
      map.current.addControl(mapNavControl.current.getExportControl(), 'bottom-left')
      map.current.addControl(mapLegendControlRef.current, 'bottom-left')
      map.current.on('load', () => {
        map.current.on('mouseenter', 'properties', onMapMouseEnter)
        map.current.on('mouseleave', 'properties', onMapMouseLeave)
      })
      map.current.on('styledata', mapStyleOnLoaded)
      map.current.on('zoom', () => {
        let _zoom = Math.trunc(map.current.getZoom())
        if (_zoom < MAX_PROVINCE_ZOOM_LEVEL && mapPopupRef.current) {
          // close popup
          mapPopupRef.current.remove()
          mapPopupRef.current = null
        }
        setZoom(_zoom)
      })
      map.current.on('pitchend', () => {
        setShow3dLayer(map.current.getPitch() > 0)
      })
    }
    return () => {
      if (map.current) {
        map.current.off('styledata', mapStyleOnLoaded)
      }
    }
  }, [mapTheme, isSuccess, dynamicMapSession]);

  /* Callback when map is on click. */
  const mapOnClick = useCallback((e: any) => {
    if (contextLayers.length === 0) return;
    if (selectionMode === MapSelectionMode.None) return;
    let _parcelLayer = findParcelLayer(contextLayers)
    if (typeof _parcelLayer === 'undefined') return;
    let _mapZoom = map.current.getZoom()
    if (selectionMode === MapSelectionMode.Parcel) {
      // skip search if not in the parcel zoom
      if (_mapZoom < MIN_SELECT_PARCEL_ZOOM_LEVEL) return;
      // find parcel
      searchParcel(e.lngLat, selectedProperty.id, (parcel: ParcelInterface) => {
        if (parcel) {
          dispatch(toggleParcelSelectedState(parcel))
        }
      })
    } else if (selectionMode === MapSelectionMode.Property && uploadMode === UploadMode.None) {
      // find layers for searching
      const _layers = map.current.getStyle().layers
      let _areaSourceLayers = findAreaLayers(contextLayers)
      if (_mapZoom >= MIN_SELECT_PROPERTY_ZOOM_LEVEL && isContextLayerSelected(contextLayers, 'properties')) {
        // skip search if not in the properties layer minZoom
        _areaSourceLayers.push('properties')
      }
      const _parcelLayer = findParcelLayer(contextLayers)
      let _fillParcelLayers:string[] = []
      if (_mapZoom >= MIN_SELECT_PARCEL_ZOOM_LEVEL && _parcelLayer && _parcelLayer.isSelected) {
        // need to use invisible parcel layers
        _fillParcelLayers = _parcelLayer.layer_names.map((layer_name) => layer_name !== 'parent_farm' ? `${layer_name}-invisible-fill` : '').filter((layer_name) => layer_name.length > 0)
      }
      let _searchLayers = _layers.filter((layer:any) => _areaSourceLayers.includes(layer['source-layer']) || _fillParcelLayers.includes(layer['id']) ).map((layer:any) => layer.id)
      let features = map.current.queryRenderedFeatures(e.point, { layers: _searchLayers })
      if (features.length) {
        const _resultLayers = features.map((e:any) => e.layer.id)
        if (_resultLayers.includes('properties')) {
          searchProperty(e.lngLat, (property: PropertyInterface) => {
            if (property) {
              dispatch(setSelectedProperty(property))
            } else {
              dispatch(resetSelectedProperty())
            }
          })
        } else {
          dispatch(resetSelectedProperty())
          // display popup
          let _description = getMapPopupDescription(features)
          localStorage.setItem('description',_description)
          if (_description) {
            mapPopupRef.current = new maplibregl.Popup()
              .setLngLat(e.lngLat)
              .setHTML(_description)
              .addTo(map.current)
          }
        }
      }
    }
  }, [isMapReady, contextLayers, selectionMode, uploadMode, selectedProperty])

  /* OnClick event */
  useEffect(() => {
    if (!map.current) return;
    if (!isSuccess) return;
    map.current.on('click', mapOnClick)
    return () => {
      map.current.off('click', mapOnClick)
    }
  }, [isMapReady, contextLayers, selectionMode, uploadMode, selectedProperty, isSuccess])

  /* render selected+unselected parcel */
  useEffect(() => {
    if (!isMapReady) return;
    let _mapObj: maplibregl.Map = map.current
    let _has_removed = false
    for (let i = 0; i < selectedParcels.length; ++i) {
      let parcel = selectedParcels[i]
      let _feature_id = { source: 'sanbi', sourceLayer: parcel.layer, id: parcel.id }
      let _selected = parcel.isRemoved ? false : true
      _mapObj.setFeatureState(
        _feature_id,
        { 'parcel-selected': _selected }
      )
      if (parcel.isRemoved) {
        _has_removed = true
      }
    }
    if (_has_removed) {
      dispatch(selectedParcelsOnRenderFinished())
    }
  }, [selectedParcels, isMapReady])

  /* Render/Respond to mapEvents */
  useEffect(() => {
    if (mapEvents.length === 0) return
    if (!isMapReady || !map.current) {
      return;
    }
    let _mapObj: maplibregl.Map = map.current
    for (let i=0; i < mapEvents.length; ++i) {
      let _event = mapEvents[i]
      if (_event.name === MapEvents.REFRESH_PROPERTIES_LAYER) {
        // add query param to properties layer to refresh it
        let _sanbiDynamicSource = _mapObj.getSource('sanbi-dynamic') as any;
        let _url = _sanbiDynamicSource['tiles'][0]
        if (!props.isDataUpload) {
          _url = _url.replace(TIME_QUERY_PARAM_REGEX, `?t=${Date.now()}&session=${dynamicMapSession}`)
        } else {
          _url = _url.replace(TIME_QUERY_PARAM_REGEX, `?t=${Date.now()}`)
        }
        // Set the tile url to a cache-busting url (to circumvent browser caching behaviour):
        _sanbiDynamicSource.tiles = [ _url ]

        // Remove the tiles for a particular source
        _mapObj.style.sourceCaches['sanbi-dynamic'].clearTiles()

        // Load the new tiles for the current viewport (map.transform -> viewport)
        _mapObj.style.sourceCaches['sanbi-dynamic'].update(_mapObj.transform)

        // Force a repaint, so that the map will be repainted without you having to touch the map
        _mapObj.triggerRepaint()
      } else if (_event.name === MapEvents.PROPERTY_SELECTED ||
          _event.name === MapEvents.BOUNDARY_FILES_UPLOADED ||
          _event.name === MapEvents.ZOOM_INTO_PROPERTY) {
        // parse bbox from payload
        if (_event.payload && _event.payload.length === 4) {
          let _bbox = _event.payload.map(Number)
          if (!_mapObj) return;
          _mapObj.fitBounds([[_bbox[0], _bbox[1]], [_bbox[2], _bbox[3]]], {
              padding: 50,
              maxZoom: 16
          })
        }
      } else if (_event.name === MapEvents.HIGHLIGHT_SELECTED_PARCEL) {
        if (_event.payload && _event.payload.length === 2) {
          if (highlightedParcel.id) {
            // remove current highlight
            _mapObj.setFeatureState(
              highlightedParcel,
              { 'parcel-selected-highlighted': false }
            )
          }
          let _feature_id:FeatureIdentifier = {
            id: _event.payload[0],
            source: 'sanbi',
            sourceLayer: _event.payload[1],
          }
          _mapObj.setFeatureState(
            _feature_id,
            { 'parcel-selected-highlighted': true }
          )
          setHighlightedParcel(_feature_id)
        } else if (highlightedParcel.id) {
          // remove highlight
          _mapObj.setFeatureState(
            highlightedParcel,
            { 'parcel-selected-highlighted': false }
          )
          setHighlightedParcel(getEmptyFeature())
        }
      }
    }
    dispatch(onMapEventProcessed([...mapEvents]))
  }, [mapEvents])

  /* Check Digitise Boundary Processing status every 3s */
  useEffect(() => {
    if (savingBoundaryDigitise && boundaryDigitiseSession) {
        const interval = setInterval(() => {
            getBoundaryDigitiseStatus(boundaryDigitiseSession)
        }, 3000);
        return () => clearInterval(interval);
    }
  }, [savingBoundaryDigitise, boundaryDigitiseSession])

  /* Called when filters are changed */
  useEffect(() => {
    let _data = {
      'start_year': startYear,
      'end_year': endYear,
      'species': selectedSpecies,
      'organisation': organisationId,
      'activity': activityId,
      'spatial_filter_values': spatialFilterValues,
      'property': propertyId 
    }
    if (!props.isDataUpload) {
      // rebuild query parameters to enable choropleth layers
      let _queryParams = ''
      if (dynamicMapSession) {
        _queryParams = `session=${dynamicMapSession}`
      }
      fetchPopulationCountsLegends(_queryParams, _data, selectedSpecies)
    }
  }, [props.isDataUpload, dynamicMapSession, startYear, endYear, selectedSpecies, organisationId, activityId, spatialFilterValues, propertyId])

  /* Use debounce+UseMemo to avoid updating filter (materialized view) frequently when filter is changed */
  /* useMemo is used to avoid the debounce function is recreated during each render (unless MapTheme is changed) */
  const fetchPopulationCountsLegends = React.useMemo(() => debounce((queryParams: string, bodyData: any, speciesFilters: string) => {
    if (axiosSource.current) axiosSource.current.cancel()
    let cancelPostToken = newCancelToken()
    axios.post(`${MAP_PROPERTIES_LEGENDS_URL}?${queryParams}`, bodyData, {cancelToken: cancelPostToken }).then((response) => {
      if (response.data) {
        let _session = response.data['session']
        if (map.current && _session !== dynamicMapSession) {
          let _provinceCounts = response.data['province'] as PopulationCountLegend[]
          let _propertiesCounts = response.data['properties'] as PopulationCountLegend[]
          let _zoom = Math.trunc(map.current.getZoom())
          dispatch(setPopulationCountLegends([_provinceCounts, _propertiesCounts]))
          dispatch(setDynamicMapSession(_session))
          updateMapLegends(_zoom, speciesFilters, _provinceCounts, _propertiesCounts)
        } else if (map.current) {
          let _zoom = Math.trunc(map.current.getZoom())
          let _provinceCounts:PopulationCountLegend[] = []
          let _propertiesCounts:PopulationCountLegend[] = []
          if (speciesFilters && speciesFilters.length > 0) {
            _provinceCounts = response.data['province'] as PopulationCountLegend[]
            _propertiesCounts = response.data['properties'] as PopulationCountLegend[]
            drawPropertiesLayer(true, map.current, mapTheme, true, _propertiesCounts, _provinceCounts)
          } else {
            drawPropertiesLayer(false, map.current, mapTheme, true)
          }
          dispatch(setPopulationCountLegends([_provinceCounts, _propertiesCounts]))
          if (isMapReady) {
            dispatch(triggerMapEvent({
              'id': uuidv4(),
              'name': MapEvents.REFRESH_PROPERTIES_LAYER,
              'date': Date.now()
            }))
          }
          updateMapLegends(_zoom, speciesFilters, _provinceCounts, _propertiesCounts)
        } else {
          // initial map state will not have DynamicMapSession, hence map initialization depends on filters/mapTheme changed
          dispatch(setDynamicMapSession(_session))
        }
      }
    }).catch((error) => {
      if (!axios.isCancel(error)) {
        console.log(error)
      }
    })
  }, 300), [mapTheme, dynamicMapSession, isMapReady])

  return (
      <div className="map-wrap">
        <div ref={mapContainer} className="map" />
      </div>
  );
}

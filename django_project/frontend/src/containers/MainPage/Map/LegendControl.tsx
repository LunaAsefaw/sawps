import React from 'react';
import ReactDOM from "react-dom/client";
import maplibregl, { IControl } from 'maplibre-gl';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import { MapTheme, PopulationCountLegend } from "../../../models/Map";


interface LegendPlaceholderInterface {
  species: string;
  data: PopulationCountLegend[];
}


function LegendPlaceholder(props: LegendPlaceholderInterface) {
    return (
      <div className='legend-placeholder'>
        <div className='legend-header'>
          {props.species} population
        </div>
        {props.data.map((item: PopulationCountLegend, index: number) => {
          return (
            <div className='legend-item' key={index}>
              <Grid container flexDirection={'row'} alignItems={'center'}>
                <Grid item className='legend-color'>
                  <Box className='color'  sx={{backgroundColor: `${item.color}`}}></Box>
                </Grid>
                <Grid item>
                  {`${item.minLabel} - ${item.maxLabel}`}
                </Grid>
              </Grid>
            </div>
          )
        })}
      </div>
    )
}
  
export default class LegendControl<IControl> {
    _map: maplibregl.Map;
    _container: HTMLElement;
    _divRoot: any;
    _currentZoom: number;
  
    constructor() {
  
    }
  
    onAdd(map: maplibregl.Map){
      this._map = map;
      this._currentZoom = -1;
      this._container = document.createElement('div');
      this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group mapboxgl-ctrl mapboxgl-ctrl-group';
      this._divRoot = ReactDOM.createRoot(this._container)
      return this._container;
    }
  
    onRemove() {
        this._container.parentNode.removeChild(this._container)
        this._map = undefined
    }

    onUpdateLegends(zoom: number, species: string, data: PopulationCountLegend[]) {
      this._currentZoom = zoom;
      if (data.length === 0) {
        this.onClearLegends();
      } else {
        this._divRoot.render(<LegendPlaceholder species={species} data={data}/>);
      }
    }

    onClearLegends() {
      this._currentZoom = -1;
      this._divRoot.render(<div></div>);
    }

    getCurrentZoom() {
      return this._currentZoom;
    }

    onThemeChanged(theme: MapTheme) {
      if (theme === MapTheme.Dark) {
        this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group mapboxgl-ctrl mapboxgl-ctrl-group legend-root-dark';
      } else {
        this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group mapboxgl-ctrl mapboxgl-ctrl-group';
      }
    }
}
  
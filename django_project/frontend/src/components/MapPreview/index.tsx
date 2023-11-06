import React, { useRef, useEffect, useState } from 'react';
import maplibregl, {} from 'maplibre-gl';
import PropertyInterface from '../../models/Property';
import { drawPropertiesLayer } from '../../containers/MainPage/Map/MapUtility';
import { MapTheme } from '../../models/Map';


const MAP_STYLE_URL = window.location.origin + '/api/map/styles/'

interface MapPreviewInterface {
    propertyItem: PropertyInterface;
}

export default function MapPreview(props: MapPreviewInterface) {
    const { propertyItem } = props
    const mapContainer = useRef(null);
    const map = useRef(null);
    const [isMapReady, setIsMapReady] = useState(false)
    
    useEffect(() => {
        if (propertyItem === null) return
        if (map.current === null) {
            let _center = new maplibregl.LngLat(25.03362151950985, -29.12771414496658)
            if (propertyItem.centroid) {
                _center = new maplibregl.LngLat(propertyItem.centroid[0], propertyItem.centroid[1])
            }
            map.current = new maplibregl.Map({
                container: mapContainer.current,
                style: `${MAP_STYLE_URL}`,
                minZoom: 12,
                center: _center
            })
            map.current.on('load', () => {
                setIsMapReady(true)
                if (propertyItem.bbox) {
                    map.current.fitBounds(
                        propertyItem.bbox,
                        {
                            padding: {top: 10, bottom:25, left: 20, right: 20}
                        }
                    )
                }
            })
        }
    }, [propertyItem])

    useEffect(() => {
        if (!isMapReady) return;
        if (!map.current) return;
        drawPropertiesLayer(false, map.current, MapTheme.Light, true)
    }, [isMapReady])

    return (
        <div className="map-wrap">
          <div ref={mapContainer} className="map" />
        </div>
    )
}

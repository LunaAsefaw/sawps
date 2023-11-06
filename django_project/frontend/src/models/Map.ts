
export enum MapSelectionMode {
    None = "none",
    Property = "property",
    Parcel = "parcel",
    Digitise = "digitise",
    ParcelJSON = "parcelJSON"
}

export interface MapEventInterface {
    id: string;
    name: string;
    date: number;
    payload?: string[];
}

export enum MapTheme {
    None = "none",
    Light = "light",
    Dark = "dark"
}

export enum MapEvents {
    REFRESH_PROPERTIES_LAYER = "REFRESH_PROPERTIES_LAYER",
    PROPERTY_SELECTED = "PROPERTY_SELECTED",
    BOUNDARY_FILES_UPLOADED = "BOUNDARY_FILES_UPLOADED",
    HIGHLIGHT_SELECTED_PARCEL = "HIGHLIGHT_SELECTED_PARCEL",
    ZOOM_INTO_PROPERTY = "ZOOM_INTO_PROPERTY",
}

export interface PopulationCountLegend {
    minLabel: number;
    maxLabel: number;
    value: number;
    color: string;
}

import ParcelInterface from "./Parcel"

export default interface PropertyInterface {
    id: number,
    name: string,
    owner: string,
    owner_email?: string,
    property_type: string,
    property_type_id?: number,
    open: string,
    open_id?: number,
    province: string,
    province_id?: number,
    size?: number,
    organisation?: string,
    organisation_id?: number,
    parcels?: ParcelInterface[],
    bbox?: number[],
    centroid?: number[],
    short_code?: string
}

export const createNewProperty = ():PropertyInterface => {
    let _result:PropertyInterface = {
        id: 0,
        name: '',
        owner: '',
        owner_email: '',
        property_type: '',
        province: '',
        size: 0,
        organisation: '',
        open: '',
        parcels: [],
        property_type_id: 0,
        province_id: 0,
        organisation_id: 0,
        open_id: 0,
    }
    return _result
}

export interface PropertyValidation {
    name?: boolean,
    email?: boolean,
    property_type?: boolean,
    province?: boolean,
    organisation?: boolean
}

export interface PropertyTypeInterface {
    id: number,
    name: string
}

export interface ProvinceInterface {
    id: number,
    name: string
}

export interface OpenCloseInterface {
    id: number,
    name: string
}
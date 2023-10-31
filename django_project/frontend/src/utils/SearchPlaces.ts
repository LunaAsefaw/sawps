import axios from "axios";

const SEARCH_PROPERTY_URL = '/api/property/search'

interface SearchPropertyResult {
    name: string;
    bbox: any;
    id: string;
    type: string;
    fclass?: string;
}

interface NominatimResult {
    display_name: string;
    place_id: string;
    boundingbox?: any;
}


export interface SeachPlaceResult {
    id: string;
    displayName: string;
    bbox?: any;
}

const searchProperty = (searchText: string):Promise<SeachPlaceResult[]> => {
    let _queryParam = `search_text=${searchText}`
    return new Promise<SeachPlaceResult[]>((resolve, reject) => {
        axios.get(`${SEARCH_PROPERTY_URL}?${_queryParam}`)
        .then(
            response => {
                if (response && response.data) {
                    let _data = response.data as SearchPropertyResult[]
                    resolve(_data.map((value:SearchPropertyResult) => {
                        let _name = value.name
                        let _id = ''
                        if (value.fclass) {
                            _name = `${value.name} (${value.fclass})`
                            _id = `fclass_${value.id}`
                        } else {
                            _id = `property_${value.id}`
                        }
                        return {
                            'id': _id,
                            'displayName': _name,
                            'bbox': value.bbox
                        }
                    }))
                } else {
                    resolve([])
                }
            }
        ).catch(error => {
            console.log('Failed search property ', error)
            reject(new Error('Failed to fetch searchProperty!'))
        })
    })
}

const searchAddressNominatim = (searchText: string):Promise<SeachPlaceResult[]> => {
    const encodedValue = encodeURIComponent(searchText)
    return new Promise<SeachPlaceResult[]>((resolve, reject) => {
        axios.get(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodedValue}&countrycodes=za`
        ).then(
            response => {
                if (response.data) {
                    let _data = response.data as NominatimResult[]
                    resolve(_data.map((value:NominatimResult) => {
                        let _bbox = null
                        if (value.boundingbox && value.boundingbox.length === 4) {
                            _bbox = [value.boundingbox[2], value.boundingbox[0], value.boundingbox[3], value.boundingbox[1]]
                        }
                        return {
                            'id': `address_${value.place_id}`,
                            'displayName': value.display_name,
                            'bbox': _bbox
                        }
                    }))
                } else {
                    resolve([])
                }
            }
        ).catch(error => {
            console.log('Failed search nominatim ', error)
            reject(new Error('Failed to fetch searchAddress!'))
        })
    })
}

export const searchPlaces = (searchText: string, callback: (results: SeachPlaceResult[]) => void) =>  {
    Promise.all([
        searchProperty(searchText),
        searchAddressNominatim(searchText)
    ]).then(([result1, result2]) => {
        callback([...result1, ...result2])
    }).catch((error) => {
        callback([])
    })
}

import React, {useEffect, useState} from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import SearchIcon from '@mui/icons-material/Search';
import InputAdornment from '@mui/material/InputAdornment';
import {debounce} from '@mui/material/utils';
import { SeachPlaceResult, searchPlaces } from '../../utils/SearchPlaces';
import './index.scss';


interface SearchPlaceInterface {
    onPlaceSelected: (place: SeachPlaceResult) => void;
}

export default function SearchPlace(props: SearchPlaceInterface) {
    const [searchOpen, setSearchOpen] = useState(false)
    const [searchInputValue, setSearchInputValue] = useState<string>('')
    const [searchResults, setSearchResults] = useState<SeachPlaceResult[]>([])

    const searchProperty = React.useMemo(
        () =>
            debounce(
                (
                    request: { input: string },
                    callback: (results: SeachPlaceResult[]) => void,
                ) => {
                    searchPlaces(request.input, callback)
                },
                400,
            ),
        [],
    )

    useEffect(() => {
        setSearchOpen(searchInputValue.length > 1)
        let active = true;
        if (searchInputValue.length <= 1) {
            setSearchResults([])
            return undefined;
        }
        searchProperty({ input: searchInputValue }, (results: SeachPlaceResult[]) => {
            if (active) {
                setSearchResults(results)
            }
        })
        return () => {
            active = false
        };
    }, [searchInputValue, searchProperty])

    return (
        <Autocomplete
            disablePortal={false}
            id="search-property-autocomplete"
            className='searchPlace'
            open={searchOpen}
            onOpen={() => setSearchOpen(searchInputValue.length > 1)}
            onClose={() => setSearchOpen(false)}
            options={searchResults}
            getOptionLabel={(option) => option.displayName}
            renderInput={(params) => (
                <TextField
                    variant="outlined"
                    placeholder="Search place"
                    {...params}
                    InputProps={{
                        ...params.InputProps,
                        endAdornment: (
                        <InputAdornment position="end">
                            <SearchIcon />
                        </InputAdornment>
                        ),
                    }}
                />
            )}
            clearOnBlur={true}
            blurOnSelect={true}
            onChange={(event, newValue, reason) => {
                // if (newValue && newValue.bbox && newValue.bbox.length === 4) {
                //     // trigger zoom to property
                //     let _bbox = newValue.bbox.map(String)
                //     dispatch(triggerMapEvent({
                //         'id': uuidv4(),
                //         'name': MapEvents.ZOOM_INTO_PROPERTY,
                //         'date': Date.now(),
                //         'payload': _bbox
                //     }))
                // }
                props.onPlaceSelected(newValue)
                setSearchInputValue('')
            }}
            onInputChange={(event, newInputValue, reason) => {
                if (reason === 'input') {
                    setSearchInputValue(newInputValue)
                } else {
                    setSearchInputValue('')
                }
            }}
            filterOptions={(x) => x}
            isOptionEqualToValue={(option, value) => option.id === value.id}
        />
    )

}


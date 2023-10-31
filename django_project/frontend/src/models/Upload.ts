export enum UploadMode {
    None = 'none',
    SelectProperty = 'SelectProperty',
    CreateNew = 'CreateNew',
    PropertySelected = 'PropertySelected'
}

export interface AnnualPopulationInterface {
    present: boolean;
    total: number;
    adult_male?: number;
    adult_female?: number;
    sub_adult_male?: number;
    sub_adult_female?: number;
    juvenile_male?: number;
    juvenile_female?: number;
    group?: number;
    area_available_to_species: number;
    survey_method_id: number;
    survey_method_name?: string;
    note?: string;
    population_estimate_certainty: number;
    upper_confidence_level?: number;
    lower_confidence_level?: number;
    certainty_of_bounds?: number;
    sampling_effort_coverage_id?: number;
    sampling_effort_coverage_name?: string;
    population_status_id?: number;
    population_status_name?: string;
    population_estimate_category_id: number;
    population_estimate_category_name?: string;
    population_estimate_category_other?: string;
    survey_method_other?: string;
    population_estimate_certainty_name?: string;
}


export interface AnnualPopulationPerActivityInterface {
    activity_type_id: number;
    activity_type_name?: string;
    total: number;
    adult_male?: number;
    adult_female?: number;
    juvenile_male?: number;
    juvenile_female?: number;
    founder_population?: boolean;
    reintroduction_source?: string;
    permit?: number;
    translocation_destination?: string;
    note?: string;
    id?: number;
}

export interface UploadSpeciesDetailInterface {
    taxon_id: number;
    taxon_name?: string;
    common_name?: string;
    year: number;
    property_id: number;
    month_name?: string;
    annual_population: AnnualPopulationInterface;
    intake_populations: AnnualPopulationPerActivityInterface[];
    offtake_populations: AnnualPopulationPerActivityInterface[];
}

export interface TaxonMetadata {
    id: number;
    common_name_varbatim: string;
    scientific_name: string
}

export interface CommonUploadMetadata {
    id: number;
    name: string;
}

export interface AnnualPopulationValidation {
    area_available_to_species?: boolean;
    survey_method_id?: boolean;
    population_estimate_certainty?: boolean;
    population_estimate_category_id?: boolean;
    population_estimate_category_other?: boolean;
    survey_method_other?: boolean;
}

export interface AnnualPopulationPerActivityValidation {
    activity_type_id?: boolean;
    permit?: boolean;
    reintroduction_source?: boolean;
    translocation_destination?: boolean;
}

export interface AnnualPopulationPerActivityErrorMessage {
    activity_type_id?: string;
}

export interface UploadSpeciesDetailValidation {
    taxon_id?: boolean;
    year?: boolean;
    annual_population?: AnnualPopulationValidation;
    intake_population?: AnnualPopulationPerActivityValidation;
    offtake_population?: AnnualPopulationPerActivityValidation;
}

export interface SubpopulationTotal {
    adult: number;
    sub_adult: number;
    juvenile: number;
}


/* Create Default Data Functions */
const getDefaultAnnualPopulation = ():AnnualPopulationInterface => {
    return {
        present: true,
        total: 0,
        adult_male: 0,
        adult_female: 0,
        sub_adult_male: 0,
        sub_adult_female: 0,
        juvenile_male: 0,
        juvenile_female: 0,
        area_available_to_species: 0,
        survey_method_id: 0,
        note: '',
        population_estimate_certainty: 0,
        population_estimate_category_id: 0,
        population_estimate_certainty_name: '',
        survey_method_other: ''
    }
}

export const getDefaultAnnualPopulationPerActivity = ():AnnualPopulationPerActivityInterface => {
    return {
        activity_type_id: 0,
        adult_male: 0,
        adult_female: 0,
        juvenile_male: 0,
        juvenile_female: 0,
        total: 0,
        founder_population: false,
        reintroduction_source: '',
        translocation_destination: '',
        note: '',
        permit: 0,
        id: -1
    }
}

export const getDefaultUploadSpeciesDetail = (propertyId: number):UploadSpeciesDetailInterface => {
    let _currentDate = new Date()
    return {
        taxon_id: 0,
        taxon_name: '',
        common_name: ' ',
        year: _currentDate.getFullYear(),
        property_id: propertyId,
        annual_population: getDefaultAnnualPopulation(),
        intake_populations: [],
        offtake_populations: []
    }
}

export const FIELD_COUNTER = [
    'adult_male', 'adult_female',
    'sub_adult_male', 'sub_adult_female',
    'juvenile_male', 'juvenile_female'
]

export const OTHER_NUMBER_FIELDS = [
    'group', 'sampling_effort', 'area_available_to_species',
    'area_covered', 'permit'
]


export const SUBPOPULATION_FIELD_MAP: { [key: string]: string } = {
    'adult_male': 'adult',
    'adult_female': 'adult',
    'sub_adult_male': 'sub_adult',
    'sub_adult_female': 'sub_adult',
    'juvenile_male': 'juvenile',
    'juvenile_female': 'juvenile'
}

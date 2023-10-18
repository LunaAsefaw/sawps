import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react";

const baseQuery = fetchBaseQuery({
    baseUrl: '/'  // Base URL for all API requests
})

export interface UserInfo {
    user_roles: string[],
    current_organisation_id: number,
    current_organisation: string
}

export interface Property {
  id: number
  name: string
  owner: string
  owner_email: string
  property_type: string
  property_type_id: number
  province: string
  province_id: number
  open: string
  open_id: number
  size: number
  organisation: string
  organisation_id: number
}

export interface Organisation {
  id: number
  name: string
  national: boolean
  use_of_data_by_sanbi_only: boolean
  hosting_through_sanbi_platforms: boolean
  allowing_sanbi_to_expose_data: boolean
  data_use_permission: number
  province: number
}

export interface Species {
  id: number
  scientific_name: string
  common_name_varbatim: string
}

export interface Activity {
  id: number
  name: string
  recruitment: boolean
  colour: string
  width: number
  export_fields: string[]
}


// Create an API slice using RTK Query's createApi.
// This defines a set of endpoints related to user operations.
export const userApi = createApi({
    baseQuery: baseQuery,
    tagTypes: ['User', 'Organisation', 'Activity', 'Property', 'Species'],
    endpoints: (build) => ({
        getUserInfo: build.query<UserInfo, void>({
            query: () => 'api/user-info/',
            transformResponse: (response: UserInfo) => {
                return response;
            },
            providesTags: ['User']
        }),
          getOrganisation: build.query<Organisation[], void>({
            query: () => 'api/organisation/',
            transformResponse: (response: Organisation[]) => {
                return response;
            },
            providesTags: ['Organisation']
        }),
        getActivity: build.query<Activity[], void>({
            query: () => 'api/activity-type/',
            transformResponse: (response: Activity[]) => {
                return response;
            },
            providesTags: ['Activity']
        }),
        getActivityAsObj: build.query<Activity[], void>({
            query: () => 'api/activity-type/',
            transformResponse: (response: Activity[]) => {
                return response;
            },
            providesTags: ['Activity']
        }),
        getProperty: build.query<Property[], string>({
            query: (organisationIds: string) => `api/property/list/?organisation=${organisationIds}`,
            transformResponse: (response: Property[]) => {
                return response;
            },
            providesTags: ['Property']
        }),
        getSpecies: build.query<Species[], string>({
            query: (organisationIds: string) => `species/?organisation=${organisationIds}`,
            transformResponse: (response: Species[]) => {
                return response;
            },
            providesTags: ['Species']
        }),
    })
})


export const {
    useGetUserInfoQuery,
    useGetOrganisationQuery,
    useGetActivityQuery,
    useGetActivityAsObjQuery,
    useGetPropertyQuery,
    useGetSpeciesQuery
} = userApi



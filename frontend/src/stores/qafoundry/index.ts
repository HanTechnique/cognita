import { createApi } from '@reduxjs/toolkit/query/react'

// import * as T from './types'
import { createBaseQuery } from '../utils'

export enum ModelType {
  chat = 'chat',
  embedding = 'embedding',
  reranking = 'reranking',
}

export interface QueryAnswer {
  answer: string
  docs: SourceDocs[]
}

export interface ModelConfig {
  name: string
  type?: ModelType
  parameters: {
    temperature?: number
    maximum_length?: number
    top_p?: number
    top_k?: number
    repetition_penalty?: number
    frequency_penalty?: number
    presence_penalty?: number
    stop_sequences?: string[]
  }
}


export interface DataSource {
  type: string
  uri?: string
  metadata?: object
  fqn: string
}

export interface Knowledge {
  name: string
}

export interface ParserConfig {
  name: string
  parameters?: {
    [key: string]: any
  }
}

export interface AssociatedDataSource {
  data_source_fqn: string
  parser_config: {
      [key: string]: ParserConfig
  }
  data_source: DataSource
}

export interface AssociatedKnowledge {
  knowledge: Knowledge
}


export interface EmbedderConfig {
  name: string
  parameters?: {
    [key: string]: any
  }
}



export interface AddDataSourcePayload {
  type: string
  uri: string
  metadata?: object
}

export interface DataIngestionRun {
  collection_name: string
  data_source_fqn: string
  parser_config?: {
    chunk_size?: number
    chunk_overlap?: number
    parser_map?: {
      [key: string]: string
    }
  }
  data_ingestion_mode: string
  raise_error_on_failure: boolean
  name: string
  status: string
}

export interface CollectionQueryDto {
  collection_name: string
  retriever_name?: string
  retriever_config: {
    search_type: string
    search_kwargs?: any
    k?: number
    fetch_k?: number
  }
  prompt_template?: string
  query: string
  model_configuration: ModelConfig
  stream?: boolean
  queryController?: string
}

export interface SourceDocs {
  page_content: string
  metadata: {
    _data_point_fqn: string
    _data_point_hash: string
    page_num?: number
    page_number?: number
    relevance_score?: number
    type: string
    _id: string
    _collection_name: string
  }
  type: string
}

export const baseQAFoundryPath = import.meta.env.VITE_QA_FOUNDRY_URL

export const qafoundryApi = createApi({
  reducerPath: 'qafoundry',
  baseQuery: createBaseQuery({
    baseUrl: baseQAFoundryPath,
  }),
  tagTypes: [
    'DataSources',
    'Applications',
  ],
  endpoints: (builder) => ({
    // * Queries
    getDataLoaders: builder.query<any, void>({
      query: () => ({
        url: '/v1/components/dataloaders',
        method: 'GET',
      }),
    }),
    getAllEnabledChatModels: builder.query<any, void>({
      query: () => ({
        url: '/v1/internal/models?model_type=chat',
        method: 'GET',
        responseHandler: (response) =>
          response.json().then((data: { models: object[] }) => data.models),
      }),
    }),
    getAllEnabledEmbeddingModels: builder.query<any, void>({
      query: () => ({
        url: '/v1/internal/models?model_type=embedding',
        method: 'GET',
        responseHandler: (response) =>
          response.json().then((data: { models: object[] }) => data.models),
      }),
    }),
    getDataSources: builder.query<DataSource[], void>({
      query: () => ({
        url: '/v1/data_source/list',
        method: 'GET',
        responseHandler: (response) =>
          response
            .json()
            .then((data: { data_sources: DataSource[] }) => data.data_sources),
      }),
      providesTags: ['DataSources'],
    }),
    getOpenapiSpecs: builder.query<any, void>({
      query: () => ({
        url: '/openapi.json',
        method: 'GET',
      }),
    }),
    getApplications: builder.query<string[], void>({
      query: () => ({
        url: '/v1/apps/list',
        method: 'GET',
        responseHandler: (response) =>
          response.json().then((data) => data.rag_apps),
      }),
      providesTags: ['Applications'],
    }),
    getApplicationDetailsByName: builder.query<any, string>({
      query: (appName) => ({
        url: `/v1/apps/${appName}`,
        method: 'GET',
        responseHandler: (response) =>
          response.json().then((data) => data.rag_app),
      }),
    }),

    // * Mutations
    uploadDataToDataDirectory: builder.mutation({
      query: (payload: { filepaths: string[]; upload_name: string }) => ({
        url: '/v1/internal/upload-to-data-directory',
        body: payload,
        method: 'POST',
      }),
    }),
    uploadDataToLocalDirectory: builder.mutation({
      query: (payload: { files: File[]; upload_name: string }) => {
        var bodyFormData = new FormData()
        bodyFormData.append('upload_name', payload.upload_name)
        payload.files.forEach((file) => {
          bodyFormData.append('files', file)
        })
        return {
          url: '/v1/internal/upload-to-local-directory',
          body: bodyFormData,
          method: 'POST',
          formData: true,
        }
      },
    }),
    deleteDataSource: builder.mutation({
      query: (payload: { data_source_fqn: string }) => ({
        url: `/v1/data_source/delete?data_source_fqn=${encodeURIComponent(
          payload.data_source_fqn
        )}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['DataSources'],
    }),
    addDataSource: builder.mutation({
      query: (payload: AddDataSourcePayload) => ({
        url: '/v1/data_source',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: (_result, _opts) => [{ type: 'DataSources' }],
    }),
    createApplication: builder.mutation({
      query: (payload: object) => ({
        url: '/v1/apps',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: ['Applications'],
    }),
    deleteApplication: builder.mutation({
      query: (payload: { app_name: string }) => ({
        url: `/v1/apps/${payload.app_name}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Applications'],
    }),
  }),
})

export const {
  // queries
  useGetAllEnabledChatModelsQuery,
  useGetAllEnabledEmbeddingModelsQuery,
  useGetDataLoadersQuery,
  useGetDataSourcesQuery,
  useGetOpenapiSpecsQuery,
  useGetApplicationsQuery,
  useGetApplicationDetailsByNameQuery,

  // mutations
  useUploadDataToDataDirectoryMutation,
  useUploadDataToLocalDirectoryMutation,
  useDeleteDataSourceMutation,
  useAddDataSourceMutation,
  useCreateApplicationMutation,
  useDeleteApplicationMutation,
} = qafoundryApi

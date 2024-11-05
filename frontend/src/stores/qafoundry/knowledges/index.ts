import { ModelConfig, EmbedderConfig, AssociatedDataSource, DataIngestionRun  } from '../index'
import { createApi } from '@reduxjs/toolkit/query/react'

// import * as T from './types'
import { createBaseQuery } from '../../utils'

export interface KnowledgeQueryDto {
    knowledge_name: string
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
  
  
export interface Knowledge {
    name: string
    description?: string
    embedder_config: EmbedderConfig
    associated_data_sources: {
      [key: string]: AssociatedDataSource
    }
  }

  export const baseQAFoundryPath = import.meta.env.VITE_QA_FOUNDRY_URL

export const qafoundryKnowledgesApi = createApi({
  reducerPath: 'qafoundryknowledges',
  baseQuery: createBaseQuery({
    baseUrl: baseQAFoundryPath,
  }),
  tagTypes: [
    'Knowledges',
    'KnowledgeNames',
    'KnowledgeDetails',
  ],
  endpoints: (builder) => ({
    // * Queries
    getKnowledges: builder.query<Knowledge[], void>({
      query: () => ({
        url: '/v1/knowledges',
        responseHandler: (response) =>
          response
            .json()
            .then((data: { knowledges: Knowledge[] }) => data.knowledges),
      }),
      providesTags: ['Knowledges'],
    }),
    getKnowledgeNames: builder.query<string[], void>({
      query: () => ({
        url: '/v1/knowledges/list',
        method: 'GET',
        responseHandler: (response) =>
          response
            .json()
            .then((data: { knowledges: string[] }) => data.knowledges),
      }),
      providesTags: ['KnowledgeNames'],
    }),
    getKnowledgeDetails: builder.query<Knowledge, string>({
      query: (knowledgeName) => ({
        url: `/v1/knowledges/${knowledgeName}`,
        method: 'GET',
        responseHandler: (response) =>
          response
            .json()
            .then((data: { knowledge: Knowledge }) => data.knowledge),
      }),
      providesTags: ['KnowledgeDetails'],
    }),
    getKnowledgeStatus: builder.query({
      query: (payload: { knowledgeName: string }) => ({
        url: `/v1/knowledges/data_ingestion_run/${payload.knowledgeName}/status`,
        method: 'GET',
      }),
    }),
    getDataIngestionRuns: builder.query<DataIngestionRun[], any>({
      query: (payload: {
        knowledge_name: string
        data_source_fqn: string
      }) => ({
        url: '/v1/knowledges/data_ingestion_runs/list',
        body: payload,
        method: 'POST',
        responseHandler: (response) =>
          response
            .json()
            .then(
              (data: { data_ingestion_runs: DataIngestionRun[] }) =>
                data.data_ingestion_runs
            ),
      }),
    }),

    // * Mutations
    createKnowledge: builder.mutation({
      query: (payload: object) => ({
        url: '/v1/knowledges',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: ['Knowledges', 'KnowledgeNames'],
    }),
    addDocsToKnowledge: builder.mutation({
      query: (payload: object) => ({
        url: '/v1/knowledges/associate_data_source',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: ['Knowledges', 'KnowledgeDetails'],
    }),
    unassociateDataSource: builder.mutation({
      query: (payload: object) => ({
        url: '/v1/knowledges/unassociate_data_source',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: ['Knowledges', 'KnowledgeDetails'],
    }),
    deleteKnowledge: builder.mutation({
      query: (payload: { knowledgeName: string }) => ({
        url: `/v1/knowledges/${payload.knowledgeName}`,
        body: payload,
        method: 'DELETE',
      }),
      invalidatesTags: ['Knowledges', 'KnowledgeNames', 'KnowledgeDetails'],
    }),
    ingestDataSource: builder.mutation({
      query: (payload: {
        knowledge_name: string
        data_source_fqn: string
        data_ingestion_mode: string
        raise_error_on_failure: boolean
        run_as_job: boolean
      }) => ({
        url: '/v1/knowledges/ingest',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: ['KnowledgeDetails'],
    }),
  }),
})

export const {
  // queries
  useGetKnowledgesQuery,
  useGetKnowledgeNamesQuery,
  useGetKnowledgeDetailsQuery,
  useGetKnowledgeStatusQuery,
  useGetDataIngestionRunsQuery,

  // mutations
  useCreateKnowledgeMutation,
  useAddDocsToKnowledgeMutation,
  useUnassociateDataSourceMutation,
  useDeleteKnowledgeMutation,
  useIngestDataSourceMutation,
} = qafoundryKnowledgesApi

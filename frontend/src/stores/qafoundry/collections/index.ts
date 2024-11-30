import { ModelConfig, EmbedderConfig, AssociatedDataSource, DataIngestionRun, SourceDocs, AssociatedKnowledge } from '../index'
import { createApi } from '@reduxjs/toolkit/query/react'

// import * as T from './types'
import { createBaseQuery } from '../../utils'


export interface QueryAnswer {
  answer: string
  docs: SourceDocs[]
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
  
export interface Collection {
    name: string
    description?: string
    embedder_config: EmbedderConfig
    associated_data_sources: {
        [key: string]: AssociatedDataSource
    }
    knowledges: {
      [key: string]: AssociatedKnowledge
  }
}

export const baseQAFoundryPath = import.meta.env.VITE_QA_FOUNDRY_URL

export const qafoundryCollectionsApi = createApi({
  reducerPath: 'qafoundrycollections',
  baseQuery: createBaseQuery({
    baseUrl: baseQAFoundryPath,
  }),
  tagTypes: [
    'Collections',
    'CollectionNames',
    'CollectionDetails',
  ],
  endpoints: (builder) => ({
    // * Queries
    getCollections: builder.query<Collection[], void>({
      query: () => ({
        url: '/v1/collections',
        responseHandler: (response) =>
          response
            .json()
            .then((data: { collections: Collection[] }) => data.collections),
      }),
      providesTags: ['Collections'],
    }),
    getCollectionNames: builder.query<string[], void>({
      query: () => ({
        url: '/v1/collections/list',
        method: 'GET',
        responseHandler: (response) =>
          response
            .json()
            .then((data: { collections: string[] }) => data.collections),
      }),
      providesTags: ['CollectionNames'],
    }),
    getCollectionDetails: builder.query<Collection, string>({
      query: (collectionName) => ({
        url: `/v1/collections/${collectionName}`,
        method: 'GET',
        responseHandler: (response) =>
          response
            .json()
            .then((data: { collection: Collection }) => data.collection),
      }),
      providesTags: ['CollectionDetails'],
    }),
    getCollectionStatus: builder.query({
      query: (payload: { collectionName: string }) => ({
        url: `/v1/collections/data_ingestion_run/${payload.collectionName}/status`,
        method: 'GET',
      }),
    }),
    
    getDataIngestionRuns: builder.query<DataIngestionRun[], any>({
        query: (payload: {
          knowledge_name: string
          data_source_fqn: string
        }) => ({
          url: '/v1/collections/data_ingestion_runs/list',
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
    
    queryCollection: builder.mutation<
      QueryAnswer,
      CollectionQueryDto & { queryController: string }
    >({
      query: (payload) => {
        const token = localStorage.getItem('idToken'); // Retrieve JWT from localStorage

        return {
          url: `/retrievers/${payload.queryController}/answer`,
          body: payload,
          method: 'POST',
          headers: {
            Authorization: token ? `Bearer ${token}` : undefined, // Conditional header
          },
        };
      },
    }),

    createCollection: builder.mutation({
      query: (payload: object) => ({
        url: '/v1/collections',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: ['Collections', 'CollectionNames'],
    }),
    addDocsToCollection: builder.mutation({
      query: (payload: object) => ({
        url: '/v1/collections/associate_data_source',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: ['Collections', 'CollectionDetails'],
    }),
    unassociateDataSource: builder.mutation({
      query: (payload: object) => ({
        url: '/v1/collections/unassociate_data_source',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: ['Collections', 'CollectionDetails'],
    }),
    deleteCollection: builder.mutation({
      query: (payload: { collectionName: string }) => ({
        url: `/v1/collections/${payload.collectionName}`,
        body: payload,
        method: 'DELETE',
      }),
      invalidatesTags: ['Collections', 'CollectionNames', 'CollectionDetails'],
    }),
    ingestDataSource: builder.mutation({
      query: (payload: {
        collection_name: string
        data_source_fqn: string
        data_ingestion_mode: string
        raise_error_on_failure: boolean
        run_as_job: boolean
      }) => ({
        url: '/v1/collections/ingest',
        body: payload,
        method: 'POST',
      }),
      invalidatesTags: ['CollectionDetails'],
    }),
    // Add Knowledge to Collection
    associateKnowledge: builder.mutation({
      query: (payload: { collection_name: string; knowledge_name: string }) => ({
        url: `/v1/collections/${payload.collection_name}/knowledges/${payload.knowledge_name}`,
        method: 'POST',
      }),
      invalidatesTags: ['CollectionDetails'],
    }),
    getKnowledgeIngestionRuns: builder.query<DataIngestionRun[], { knowledge_name: string }>({
      query: (payload) => ({
        url: '/v1/collections/data_ingestion_runs/list',
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
  }),
})

export const {
  // queries
  useGetCollectionsQuery,
  useGetCollectionNamesQuery,
  useGetCollectionDetailsQuery,
  useGetCollectionStatusQuery,
  useGetDataIngestionRunsQuery,
  useGetKnowledgeIngestionRunsQuery,

  // mutations
  useQueryCollectionMutation,
  useCreateCollectionMutation,
  useAddDocsToCollectionMutation,
  useUnassociateDataSourceMutation,
  useDeleteCollectionMutation,
  useIngestDataSourceMutation,
  useAssociateKnowledgeMutation,  
} = qafoundryCollectionsApi

import IconProvider from '@/components/assets/IconProvider'
import Button from '@/components/base/atoms/Button'
import CustomDrawer from '@/components/base/atoms/CustomDrawer'
import Spinner from '@/components/base/atoms/Spinner/Spinner'
import notify from '@/components/base/molecules/Notify'
import {
  useGetAllEnabledEmbeddingModelsQuery,
  useGetDataSourcesQuery,
} from '@/stores/qafoundry'
import {
  useCreateKnowledgeMutation,
  useIngestDataSourceMutation,
} from '@/stores/qafoundry/knowledges'
import { MenuItem, Select } from '@mui/material'
import classNames from 'classnames'
import React, { useEffect, useState } from 'react'
import { defaultParserConfigs } from './AddDataSourceToKnowledge'
import SimpleCodeEditor from '@/components/base/molecules/SimpleCodeEditor'

interface NewKnowledgeProps {
  open: boolean
  onClose: () => void
  onSuccess?: () => void
}

const NewKnowledge = ({ open, onClose, onSuccess }: NewKnowledgeProps) => {
  const [isSaving, setIsSaving] = useState(false)
  const [knowledgeName, setKnowledgeName] = useState('')
  const [selectedEmbeddingModel, setSelectedEmbeddingModel] = React.useState('')
  const [chunkSize, setChunkSize] = React.useState(1000)
  const [selectedDataSource, setSelectedDataSource] = useState('none')
  const [parserConfigs, setParserConfigs] = useState(defaultParserConfigs)

  const { data: dataSources } = useGetDataSourcesQuery()
  const { data: allEmbeddingModels } = useGetAllEnabledEmbeddingModelsQuery()

  const [createKnowledge] = useCreateKnowledgeMutation()
  const [ingestDataSource] = useIngestDataSourceMutation()

  const pattern = /^[a-z][a-z0-9-]*$/
  const isValidKnowledgeName = pattern.test(knowledgeName)

  useEffect(() => {
    if (allEmbeddingModels && allEmbeddingModels.length) {
      setSelectedEmbeddingModel(allEmbeddingModels[0].name)
    }
  }, [allEmbeddingModels])

  const resetForm = () => {
    setKnowledgeName('')
    if (allEmbeddingModels && allEmbeddingModels.length) {
      setSelectedEmbeddingModel(allEmbeddingModels[0].name)
    }
    setChunkSize(1000)
    setSelectedDataSource('none')
    setIsSaving(false)
  }

  const handleSubmit = async () => {
    setIsSaving(true)
    try {
      if (!knowledgeName) {
        setIsSaving(false)
        return notify(
          'error',
          'Knowledge Name is Required!',
          'Please provide a knowledge name'
        )
      }
      const embeddingModel = allEmbeddingModels.find(
        (model: any) => model.name == selectedEmbeddingModel
      )

      const params = {
        name: knowledgeName,
        embedder_config: {
          name: embeddingModel.name,
        },
        associated_data_sources: [
          {
            data_source_fqn: selectedDataSource,
            parser_config: JSON.parse(parserConfigs),
          },
        ],
      }

      const res = await createKnowledge(params).unwrap()

      await ingestDataSource({
        knowledge_name: knowledgeName,
        data_source_fqn: selectedDataSource,
        data_ingestion_mode: 'INCREMENTAL',
        raise_error_on_failure: true,
        run_as_job: true,
      })

      const allKnowledgeToJobNames = JSON.parse(
        localStorage.getItem('knowledgeToJob') || '{}'
      )
      localStorage.setItem(
        'knowledgeToJob',
        JSON.stringify({
          ...allKnowledgeToJobNames,
          [knowledgeName]: res,
        })
      )

      onClose()
      resetForm()
      onSuccess?.()
      notify(
        'success',
        'Knowledge is successfully added!',
        'Knowledge will be available to use after 3-5 minutes.'
      )
    } catch (err: any) {
      notify(
        'error',
        'Failed to create the knowledge',
        err?.error ||
          err?.details?.msg ||
          err?.message ||
          'There was an error while creating the new knowledge'
      )
    }
    setIsSaving(false)
  }

  return (
    <CustomDrawer
      anchor={'right'}
      open={open}
      onClose={onClose}
      bodyClassName="p-0"
      width="w-[65vw]"
    >
      <div className="relative w-full">
        {isSaving && (
          <div className="absolute w-full h-full bg-gray-50 z-10 flex flex-col justify-center items-center">
            <div>
              <Spinner center big />
            </div>
            <p className="mt-4">Knowledge is being submitted</p>
          </div>
        )}
        <div className="font-bold font-inter text-2xl py-2 border-b border-gray-200 px-4">
          Create a new document knowledge
        </div>
        <div className="h-[calc(100vh-124px)] overflow-y-auto p-4">
          <div className="bg-yellow-100 p-2 mb-2 text-xs rounded">
            Knowledges that are uploaded will be accessible to the public.
            Please do not upload any confidential or sensitive data.
          </div>
          <div className="mb-4">
            <label htmlFor="knowledge-name-input">
              <span className="label-text font-inter mb-1">
                Knowledge name
              </span>
              <small>
                {' '}
                * Should only contain lowercase alphanumeric character
              </small>
            </label>
            <input
              className={classNames(
                'block w-full border border-gray-250 outline-none text-md p-2 rounded',
                { 'field-error': knowledgeName && !isValidKnowledgeName }
              )}
              id="knowledge-name-input"
              placeholder="Enter your knowledge name"
              value={knowledgeName}
              onChange={(e) => setKnowledgeName(e.target.value)}
            />
            {knowledgeName && !isValidKnowledgeName && (
              <div className="text-error text-xs mt-1 flex gap-1 items-center">
                <IconProvider
                  icon="exclamation-triangle"
                  className={'w-4 leading-5'}
                />
                <div className="font-medium">
                  Knowledge name should only contain lowercase alphanumeric
                  character!
                </div>
              </div>
            )}
          </div>
          <div className="flex gap-7 w-full mb-4">
            <div className="w-full">
              <span className="label-text font-inter mb-1">
                Embedding Model <small>*</small>
              </span>
              <Select
                id="datasets"
                value={selectedEmbeddingModel}
                onChange={(e) => {
                  setSelectedEmbeddingModel(e.target.value)
                }}
                placeholder="Select Embedding Model..."
                sx={{
                  background: 'white',
                  height: '2.6rem',
                  width: '100%',
                  border: '1px solid #CEE0F8 !important',
                  outline: 'none !important',
                  '& fieldset': {
                    border: 'none !important',
                  },
                }}
              >
                {allEmbeddingModels?.map((model: any) => (
                  <MenuItem value={model.name} key={model.name}>
                    {model.name}
                  </MenuItem>
                ))}
              </Select>
            </div>
          </div>
          <div className="mb-3">
            <label>
              <div className="label-text font-inter mb-1">
                Select Data Source <small>*</small>
              </div>
              <Select
                id="data_sources"
                value={selectedDataSource}
                onChange={(e) => {
                  setSelectedDataSource(e.target.value)
                }}
                placeholder="Select Data Source FQN"
                sx={{
                  background: 'white',
                  height: '42px',
                  width: '100%',
                  border: '1px solid #CEE0F8 !important',
                  outline: 'none !important',
                  '& fieldset': {
                    border: 'none !important',
                  },
                }}
                MenuProps={{
                  PaperProps: {
                    sx: { maxWidth: 'calc(65vw - 4rem)' },
                  },
                }}
              >
                <MenuItem value={'none'} disabled>
                  Select a Data Source FQN
                </MenuItem>
                {dataSources?.map((source: any) => (
                  <MenuItem value={source.fqn} key={source.fqn}>
                    <span className="truncate w-full">{source.fqn}</span>
                  </MenuItem>
                ))}
              </Select>
            </label>
          </div>
          {selectedDataSource !== 'none' && (
            <div className="mb-5">
              <div className="flex text-xs mb-1">
                <div>Type :</div>
                &nbsp;
                <div>
                  {
                    dataSources?.filter(
                      (source) => source.fqn === selectedDataSource
                    )[0].type
                  }
                </div>
              </div>
              <div className="flex text-xs">
                <div>Source :</div>
                &nbsp;
                <div>
                  {
                    dataSources?.filter(
                      (source) => source.fqn === selectedDataSource
                    )[0].uri
                  }
                </div>
              </div>
            </div>
          )}
          <div className="mb-4">
            <div className="label-text font-inter mb-1">Parser Configs</div>
            <SimpleCodeEditor
              language="json"
              height={200}
              value={parserConfigs}
              onChange={(value) => setParserConfigs(value ?? '')}
            />
          </div>
        </div>
        <div className="flex justify-end items-center gap-2 h-[58px] border-t border-gray-200 px-4">
          <Button
            outline
            text="Cancel"
            onClick={() => {
              onClose()
              resetForm()
            }}
            className="border-gray-500 gap-1 btn-sm font-normal"
            type="button"
          />
          <Button
            text="Process"
            onClick={handleSubmit}
            className="gap-1 btn-sm font-normal"
            type="button"
            disabled={
              !knowledgeName ||
              !isValidKnowledgeName ||
              selectedDataSource === 'none'
            }
          />
        </div>
      </div>
    </CustomDrawer>
  )
}

export default NewKnowledge
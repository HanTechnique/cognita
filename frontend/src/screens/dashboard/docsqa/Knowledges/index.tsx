import Badge from '@/components/base/atoms/Badge'
import Button from '@/components/base/atoms/Button'
import LinkButton from '@/components/base/atoms/Link'
import Spinner from '@/components/base/atoms/Spinner/Spinner'
import {
  useGetKnowledgeDetailsQuery,
  useGetKnowledgeNamesQuery,
} from '@/stores/qafoundry/knowledges'
import React, { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import AddDataSourceToKnowledge from './AddDataSourceToKnowledge'
import KnowledgeCard from './KnowledgeCard'
import NewKnowledge from './NewKnowledge'
import NoKnowledges from './NoKnowledges'
import RunsHistoryDrawer from '../Knowledges/RunsHistoryDrawer'
import DataSourcesTable from './DataSourcesTable'

const Knowledges = () => {
  const [searchParams, setSearchParams] = useSearchParams()
  const [newKnowledgeModalOpen, setNewKnowledgeModalOpen] = useState(
    searchParams.get('newKnowledgeOpen') === 'true'
  )
  const [selectedKnowledge, setSelectedKnowledge] = useState<
    string | undefined
  >()
  const [openDataSourceLinkForm, setOpenDataSourceLinkForm] = useState(false)
  const [runsHistoryDrawerOpen, setRunsHistoryDrawerOpen] = useState(false)
  const [selectedDataSourceFqn, setSelectedDataSourceFqn] = useState('')

  const { data: knowledgesNames, isLoading: isKnowledgesLoading } =
    useGetKnowledgeNamesQuery()
  const {
    data: knowledgeDetails,
    isLoading: isKnowledgeDetailsLoading,
    isFetching: isKnowledgeDetailsFetching,
  } = useGetKnowledgeDetailsQuery(selectedKnowledge ?? '', {
    skip: !selectedKnowledge,
  })

  const associatedDataSourcesRows = useMemo(() => {
    const rows = []
    if (knowledgeDetails) {
      for (const [key, value] of Object.entries(
        knowledgeDetails.associated_data_sources ?? {}
      )) {
        const dataSourceType = key.split(':')[0]
        if (dataSourceType === 'data-dir') {
          rows.push({
            id: key,
            type: 'local',
            source: '-',
            fqn: key,
          })
        } else if (!value?.data_source?.uri) {
          rows.push({
            id: key,
            type: dataSourceType,
            source: '-',
            fqn: key,
          })
        } else {
          rows.push({
            id: key,
            type: dataSourceType,
            source: value.data_source.uri,
            fqn: key,
          })
        }
      }
    }

    return rows
  }, [knowledgeDetails])

  useEffect(() => {
    if (knowledgesNames?.length) {
      if (
        !selectedKnowledge ||
        !knowledgesNames.includes(selectedKnowledge)
      ) {
        setSelectedKnowledge(knowledgesNames[0])
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [knowledgesNames])

  const openRunsHistoryDrawer = (fqn: string) => {
    setSelectedDataSourceFqn(fqn)
    setRunsHistoryDrawerOpen(true)
  }

  useEffect(() => {
    setNewKnowledgeModalOpen(searchParams.get('newKnowledgeOpen') === 'true')
  }, [searchParams])

  return (
    <>
      <div className='flex justify-between'>
        <div className='text-[24px] font-bold font-inter'>Knowledges</div>
        <a href={`/dashboard?knowledge=${selectedKnowledge}`}>
                    <Button
                      white
                      icon={'plus'}
                      iconClasses="text-gray-400"
                      text={'Add Application for this knowledge'}
                      className="btn-sm text-sm bg-white mr-2" // Add margin-right
                    />
                  </a>
        <LinkButton
          icon="plus"
          iconClasses="fa-xs text-slate-400"
          text={<span className="whitespace-nowrap">New Knowledge</span>}
          rounded
          className="bg-black btn-sm flex-nowrap mb-4 px-5"
          onClick={() => setNewKnowledgeModalOpen(true)}
        />
      </div>
      <div className="flex gap-5 flex-1 w-full">
        <div className="h-full bg-[#f0f7ff] rounded-lg py-5 w-[17.5rem] border border-gray-250 pt-3">
          <div
            className="h-[calc(100vh-202px)] overflow-y-auto custom-scrollbar px-3"
            style={{
              paddingRight: '0.75rem',
            }}
          >
            {isKnowledgesLoading && <Spinner center />}
            {knowledgesNames?.map((knowledge, index) => (
              <KnowledgeCard
                key={index}
                knowledgeName={knowledge}
                isSelectedKnowledge={selectedKnowledge === knowledge}
                enableErrorSelection
                onClick={() => {
                  setSelectedKnowledge(knowledge)
                }}
              />
            ))}
          </div>
        </div>
        {selectedKnowledge ? (
          <div className="flex-1 border rounded-lg border-[#CEE0F8] w-[calc(100%-300px)] bg-white p-4">
            {isKnowledgeDetailsFetching || isKnowledgeDetailsLoading ? (
              <div className="flex justify-center items-center h-full w-full">
                <Spinner center medium />
              </div>
            ) : (
              <>
                <div className="flex justify-between mb-3">
                  <div>
                    <div className="text-base font-medium mb-1">
                      Data Sources for{' '}
                      <Badge
                        text={selectedKnowledge}
                        type="white"
                        textClasses="text-base"
                      />{' '}
                      knowledge
                    </div>
                    {knowledgeDetails && (
                      <div className="text-sm">
                        Embedder Used :{' '}
                        {knowledgeDetails?.embedder_config?.name}
                      </div>
                    )}
                  </div>
                  <Button
                    white
                    icon={'plus'}
                    iconClasses="text-gray-400"
                    text={'Link Data Source'}
                    className="btn-sm text-sm bg-white"
                    onClick={() => setOpenDataSourceLinkForm(true)}
                  />
                </div>
                <div className="h-[calc(100%-4.125rem)]">
                  <DataSourcesTable
                    knowledgeName={selectedKnowledge}
                    rows={associatedDataSourcesRows}
                    openRunsHistoryDrawer={openRunsHistoryDrawer}
                  />
                </div>
              </>
            )}
          </div>
        ) : isKnowledgesLoading ? (
          <Spinner center medium />
        ) : (
          <NoKnowledges />
        )}
      </div>
      {newKnowledgeModalOpen && (
        <NewKnowledge
          open={newKnowledgeModalOpen}
          onClose={() => {
            if (searchParams.has('newKnowledgeOpen')) {
              searchParams.delete('newKnowledgeOpen')
              setSearchParams(searchParams)
            }
            setNewKnowledgeModalOpen(false)
          }}
        />
      )}
      {selectedKnowledge && openDataSourceLinkForm && (
        <AddDataSourceToKnowledge
          open={openDataSourceLinkForm}
          onClose={() => {
            setOpenDataSourceLinkForm(false)
          }}
          knowledgeName={selectedKnowledge}
        />
      )}
      {runsHistoryDrawerOpen && selectedKnowledge && selectedDataSourceFqn && (
        <RunsHistoryDrawer
          open={runsHistoryDrawerOpen}
          onClose={() => setRunsHistoryDrawerOpen(false)}
          knowledgeName={selectedKnowledge}
          selectedDataSource={selectedDataSourceFqn}
        />
      )}
    </>
  )
}

export default Knowledges

import React, { useState, useEffect, useMemo } from 'react'
import IconProvider from '@/components/assets/IconProvider'
import Button from '@/components/base/atoms/Button'
import { LightTooltip } from '@/components/base/atoms/Tooltip'
import { useDeleteKnowledgeMutation } from '@/stores/qafoundry/knowledges'

interface KnowledgeCardProps {
  isSelectedKnowledge: boolean
  knowledgeName: string
  hideInfo?: boolean
  enableErrorSelection?: boolean
  onClick: () => void
}

const KnowledgeCard = ({
  isSelectedKnowledge,
  knowledgeName,
  hideInfo,
  enableErrorSelection,
  onClick,
}: KnowledgeCardProps) => {
  const [isReady, setIsReady] = useState(true)
  const [isInfoIconVisible, setIsInfoIconVisible] = useState(false)
  const isDeleteOptionEnabled = import.meta.env.VITE_DOCS_QA_DELETE_KNOWLEDGES

  const [deleteKnowledge, deleteKnowledgeRes] = useDeleteKnowledgeMutation()

  return (
    <div
      className={`cursor-pointer mb-1 px-3 hover:bg-gray-150 py-[10px] rounded ${
        !isReady && !enableErrorSelection && 'cursor-not-allowed'
      } ${isSelectedKnowledge ? 'bg-gray-200 border border-[#818cf8]' : ''}`}
      onClick={() => {
        if (!isReady && !enableErrorSelection) return
        onClick()
      }}
      onMouseEnter={() => setIsInfoIconVisible(true)}
      onMouseLeave={() => setIsInfoIconVisible(false)}
    >
      <div className="flex justify-between items-center">
        <div className="flex gap-2.5 items-center max-w-[calc(100%-24px)]">
          <div className="text-gray-950 font-[500] text-base truncate">
            {knowledgeName}
          </div>
        </div>
        {isDeleteOptionEnabled === 'true' && (
          <LightTooltip
            title={
              <div className="p-2 bg-white text-black cursor-default">
                <div className="flex justify-center">
                  <Button
                    text="Delete Knowledge"
                    outline
                    disabled={deleteKnowledgeRes.isLoading}
                    className="border-gray-200 shadow bg-base-100 btn-sm font-normal px-2.5"
                    onClick={() =>
                      deleteKnowledge({ knowledgeName: knowledgeName })
                    }
                  />
                </div>
              </div>
            }
          >
            {
              <div
                className={`flex items-center gap-1 ${
                  !isInfoIconVisible && !isSelectedKnowledge && 'hidden'
                }`}
              >
                <IconProvider
                  icon="circle-info"
                  className="text-gray-500 p-1 text-sm"
                  size={1}
                />
              </div>
            }
          </LightTooltip>
        )}
      </div>
    </div>
  )
}

export default KnowledgeCard

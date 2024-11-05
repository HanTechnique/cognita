import Button from '@/components/base/atoms/Button';
import { DarkTooltip } from '@/components/base/atoms/Tooltip';
import notify from '@/components/base/molecules/Notify';
import Table from '@/components/base/molecules/Table';
import {
  useUnassociateKnowledgeMutation,
} from '@/stores/qafoundry/collections';
import { GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import React from 'react';

const KnowledgeDeleteButton = ({
  collectionName,
  knowledgeName,
}: {
  collectionName: string;
  knowledgeName: string;
}) => {
  const [unassociateKnowledge, { isLoading }] =
    useUnassociateKnowledgeMutation();

  const handleSubmit = async () => {
    await unassociateKnowledge({
      collection_name: collectionName,
      knowledge_name: knowledgeName,
    });
    notify(
      'success',
      'Knowledge is successfully detached from the collection!',
      'Updated collection will be available to use after 3-5 minutes.'
    );
  };

  return (
    <DarkTooltip title="Delete Knowledge">
      <Button
        outline
        icon="trash-can"
        iconClasses="text-xs text-red-400"
        className="border-red-200 shadow bg-base-100 btn-sm font-normal px-2.5 mr-1"
        loading={isLoading}
        onClick={handleSubmit}
      />
    </DarkTooltip>
  );
};

interface KnowledgesTableProps {
  collectionName: string;
  rows: {
    id: string;
    name: string;
  }[];
  openRunsHistoryDrawer: (knowledgeName: string) => void;
}

const KnowledgesTable = ({
  collectionName,
  rows,
  openRunsHistoryDrawer,
}: KnowledgesTableProps) => {
  const [skipPolling, setSkipPolling] = React.useState<{
    [key: string]: boolean;
  }>({});

  const columns: GridColDef[] = [
    { field: 'name', headerName: 'Name', flex: 1 },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 100,
      renderCell: (params: GridRenderCellParams) => {
        const key = collectionName + ':' + params?.row?.name;
        return (
          <div className="flex gap-1">
            <KnowledgeDeleteButton
              collectionName={collectionName}
              knowledgeName={params?.row?.name}
            />
          </div>
        );
      },
    },
  ];

  return (
    <div className="bg-white h-full">
      <Table rows={rows} columns={columns} />
    </div>
  );
};

export default KnowledgesTable;


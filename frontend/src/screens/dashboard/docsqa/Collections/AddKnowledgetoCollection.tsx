import React, { useState, useEffect } from 'react';
import {
  useAssociateKnowledgeMutation,
} from '@/stores/qafoundry/collections';
import {
  useGetKnowledgeNamesQuery,
} from '@/stores/qafoundry/knowledges';
import { MenuItem, Select } from '@mui/material';
import Button from '@/components/base/atoms/Button';
import notify from '@/components/base/molecules/Notify';
import CustomDrawer from '@/components/base/atoms/CustomDrawer'


interface AddKnowledgeToCollectionProps {
  collectionName: string;
  open: boolean;

  onClose: () => void;
}

const AddKnowledgeToCollection: React.FC<AddKnowledgeToCollectionProps> = ({
  collectionName,
  open,
  onClose,
}) => {
  const [selectedKnowledge, setSelectedKnowledge] = useState('');

  const [isSaving, setIsSaving] = useState(false)
  const [selectedDataSource, setSelectedDataSource] = useState('none')
  
  const resetForm = () => {
    setSelectedDataSource('none')
    setIsSaving(false)  
  }

  const { data: knowledges, isLoading: isKnowledgesLoading } =
    useGetKnowledgeNamesQuery(undefined, {
      refetchOnMountOrArgChange: true,
    });

  const [associateKnowledge, { isLoading }] =
    useAssociateKnowledgeMutation();

  const handleSubmit = async () => {
    if (!selectedKnowledge) {
      return notify('error', 'Please select a knowledge');
    }

    try {
      await associateKnowledge({
        collection_name: collectionName,
        knowledge_name: selectedKnowledge,
      }).unwrap();
      notify(
        'success',
        'Knowledge associated with the collection!',
        'Updated collection will be available to use after 3-5 minutes.'
      );
      onClose();
    } catch (err) {
      notify('error', 'Failed to associate knowledge', err?.data?.detail);
    }
  };

  useEffect(() => {
    if (knowledges && knowledges.length) {
      setSelectedKnowledge(knowledges[0]);
    }
  }, [knowledges]);

  return (
    <CustomDrawer
      anchor={'right'}
      open={open}
      onClose={() => {
        onClose()
        resetForm()
      }}
      bodyClassName="p-0"
      width="w-[65vw]"
    >
      <div className="modal-box">
        <div className="text-center font-medium text-xl mb-2">
          Add Knowledge to Collection
        </div>
        <div>
          <div className="text-sm">Select Knowledge:</div>
          <Select
            value={selectedKnowledge}
            onChange={(e) => setSelectedKnowledge(e.target.value)}
            placeholder="Select Knowledge..."
            sx={{
              background: 'white',
              height: '2rem',
              width: '100%',
              border: '1px solid #CEE0F8 !important',
              outline: 'none !important',
              '& fieldset': {
                border: 'none !important',
              },
            }}
          >
            {knowledges?.map((knowledge: string) => (
              <MenuItem value={knowledge} key={knowledge}>
                {knowledge}
              </MenuItem>
            ))}
          </Select>
        </div>
        <div className="flex justify-end w-full mt-4 gap-2">
          <Button
            text="Add"
            className="btn-sm"
            loading={isLoading || isKnowledgesLoading}
            onClick={handleSubmit}
          />
          <Button
            text="Cancel"
            className="btn-sm bg-red-600 hover:bg-red-700 border-0"
            onClick={onClose}
          />
        </div>
      </div>
    </CustomDrawer>
  );
};

export default AddKnowledgeToCollection;


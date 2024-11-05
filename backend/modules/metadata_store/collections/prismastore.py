from backend.types.collection import (
    CreateCollectionDataIngestionRun,
    CollectionDataIngestionRun,
)
from backend.types.core import (
    DataIngestionRunStatus,Collection
)

from backend.types.collection import (
    AssociateDataSourceWithCollection,
    CreateCollection,
)
import json
from typing import List, Optional, Any, Dict
from backend.modules.metadata_store.prismastore import PrismaStore
from backend.logger import logger
from fastapi import HTTPException
from backend.types.core import AssociatedDataSources

import random
import string


class CollectionPrismaStore(PrismaStore):
    def __init__(self, client: PrismaStore) -> None:
        self.db = client.db

    async def aget_data_collection_ingestion_runs(
        self, collection_name: str, data_source_fqn: str = None
    ) -> List[CollectionDataIngestionRun]:
        """Get all data ingestion runs for a collection"""
        try:
            data_collection_ingestion_runs: List[
                "PrismaCollectionDataIngestionRun"
            ] = await self.db.collectioningestionruns.find_many(
                where={"collection_name": collection_name}, order={"id": "desc"}
            )
            return [
                CollectionDataIngestionRun.model_validate(data_ir.model_dump())
                for data_ir in data_collection_ingestion_runs
            ]
        except Exception as e:
            logger.exception(f"Failed to get data ingestion runs: {e}")
            raise HTTPException(status_code=500, detail=f"{e}")
    
    async def aget_collection_by_name(
        self, collection_name: str, no_cache: bool = True
    ) -> Optional[Collection]:
        try:
            collection: Optional[
                "PrismaCollection"
            ] = await self.db.collection.find_first(where={"name": collection_name},
                                                    include={"knowledges": {"include": {"knowledge": True,"collection": True}}}
            )

            if collection:
                print(str(collection))
                return Collection.model_validate(collection.model_dump())
            return None
        except Exception as e:
            logger.exception(f"Failed to get collection by name: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get collection by name"
            )

    async def acreate_collection(self, collection: CreateCollection) -> Collection:
        try:
            existing_collection = await self.aget_collection_by_name(collection.name)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=e)

        if existing_collection:
            logger.error(f"Collection with name {collection.name} already exists")
            raise HTTPException(
                status_code=400,
                detail=f"Collection with name {collection.name} already exists",
            )

        try:
            logger.info(f"Creating collection: {collection.model_dump()}")
            collection_data = collection.model_dump()
            collection_data["embedder_config"] = json.dumps(
                collection_data["embedder_config"]
            )
            collection: "PrismaCollection" = await self.db.collection.create(
                data=collection_data
            )
            return Collection.model_validate(collection.model_dump())
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

    async def aget_retrieve_collection_by_name(
        self, collection_name: str, no_cache: bool = True
    ) -> Optional[Collection]:
        collection: "PrismaCollection" = await self.aget_collection_by_name(
            collection_name, no_cache
        )
        return Collection.model_validate(collection.model_dump())

    async def aget_collections(self) -> List[Collection]:
        try:
            collections: List["PrismaCollection"] = await self.db.collection.find_many(
                order={"id": "desc"}
            )
            return [Collection.model_validate(c.model_dump()) for c in collections]
        except Exception as e:
            logger.exception(f"Failed to get collections: {e}")
            raise HTTPException(status_code=500, detail="Failed to get collections")

    async def alist_collections(self) -> List[str]:
        try:
            collections = await self.aget_collections()
            return [collection.name for collection in collections]
        except Exception as e:
            logger.exception(f"Failed to list collections: {e}")
            raise HTTPException(status_code=500, detail="Failed to list collections")

    async def adelete_collection(self, collection_name: str, include_runs=False):
        try:
            deleted_collection: Optional[
                "PrismaCollection"
            ] = await self.db.collection.delete(where={"name": collection_name})
            if not deleted_collection:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to delete collection {collection_name!r}. No such record found",
                )
            if include_runs:
                try:
                    _deleted_count = await self.db.collectioningestionruns.delete_many(
                        where={"collection_name": collection_name}
                    )
                except Exception as e:
                    logger.exception(f"Failed to delete data ingestion runs: {e}")
        except Exception as e:
            logger.exception(f"Failed to delete collection: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete collection")
    async def aassociate_data_source_with_collection(
        self,
        collection_name: str,
        data_source_association: AssociateDataSourceWithCollection,
    ) -> Collection:
        try:
            existing_collection = await self.aget_collection_by_name(collection_name)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

        if not existing_collection:
            logger.error(f"Collection with name {collection_name} does not exist")
            raise HTTPException(
                status_code=400,
                detail=f"Collection with name {collection_name} does not exist",
            )

        try:
            data_source = await self.aget_data_source_from_fqn(
                data_source_association.data_source_fqn
            )
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

        if not data_source:
            logger.error(
                f"Data source with fqn {data_source_association.data_source_fqn} does not exist"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Data source with fqn {data_source_association.data_source_fqn} does not exist",
            )

        logger.info(f"Data source to associate: {data_source}")
        try:
            # Append datasource to existing collection
            existing_collection_associated_data_sources = (
                existing_collection.associated_data_sources
            )
            logger.info(
                f"Existing associated data sources: {existing_collection_associated_data_sources}"
            )

            data_src_to_associate = AssociatedDataSources(
                data_source_fqn=data_source_association.data_source_fqn,
                parser_config=data_source_association.parser_config,
                data_source=data_source,
            )

            if existing_collection_associated_data_sources:
                existing_collection_associated_data_sources[
                    data_src_to_associate.data_source_fqn
                ] = data_src_to_associate
            else:
                existing_collection_associated_data_sources = {
                    data_src_to_associate.data_source_fqn: data_src_to_associate
                }

            logger.info(existing_collection_associated_data_sources)
            associated_data_sources: Dict[str, Dict[str, Any]] = {}
            for (
                data_source_fqn,
                data_source,
            ) in existing_collection_associated_data_sources.items():
                associated_data_sources[data_source_fqn] = data_source.model_dump()

            updated_collection: Optional[
                "PrismaCollection"
            ] = await self.db.collection.update(
                where={"name": collection_name},
                data={"associated_data_sources": json.dumps(associated_data_sources)},
            )
            if not updated_collection:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to associate data source with collection {collection_name!r}. "
                    f"No such record found",
                )
            return Collection.model_validate(updated_collection.model_dump())

        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error: {e}",
            )
    async def aunassociate_data_source_with_collection(
        self, collection_name: str, data_source_fqn: str
    ) -> Collection:
        try:
            collection: Collection = await self.aget_collection_by_name(collection_name)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

        if not collection:
            logger.error(f"Collection with name {collection_name} does not exist")
            raise HTTPException(
                status_code=400,
                detail=f"Collection with name {collection_name} does not exist",
            )

        try:
            data_source = await self.aget_data_source_from_fqn(data_source_fqn)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

        if not data_source:
            logger.error(f"Data source with fqn {data_source_fqn} does not exist")
            raise HTTPException(
                status_code=400,
                detail=f"Data source with fqn {data_source_fqn} does not exist",
            )

        associated_data_sources = collection.associated_data_sources
        if not associated_data_sources:
            logger.error(
                f"No associated data sources found for collection {collection_name}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"No associated data sources found for collection {collection_name}",
            )
        if data_source_fqn not in associated_data_sources:
            logger.error(
                f"Data source with fqn {data_source_fqn} not associated with collection {collection_name}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Data source with fqn {data_source_fqn} not associated with collection {collection_name}",
            )
        associated_data_sources.pop(data_source_fqn, None)

        try:
            # Convert associated_data_sources of type [dict, AssociatedDataSources] to [dict, dict]
            updated_associated_data_sources: Dict[str, Dict[str, Any]] = {}
            for (
                data_source_fqn,
                data_source,
            ) in associated_data_sources.items():
                updated_associated_data_sources[
                    data_source_fqn
                ] = data_source.model_dump()

            updated_collection: Optional[
                "PrismaCollection"
            ] = await self.db.collection.update(
                where={"name": collection_name},
                data={
                    "associated_data_sources": json.dumps(
                        updated_associated_data_sources
                    )
                },
            )
            if not updated_collection:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to unassociate data source from collection. "
                    f"No collection found with name {collection_name}",
                )
            logger.info(f"Updated collection: {updated_collection}")
            return Collection.model_validate(updated_collection.model_dump())
        except Exception as e:
            logger.exception(f"Failed to unassociate data source with collection: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to unassociate data source with collection",
            )


    ######
    # DATA INGESTION RUN APIS
    ######
    async def acreate_data_ingestion_run(
        self, data_ingestion_run: CreateCollectionDataIngestionRun
    ) -> CollectionDataIngestionRun:
        """Create a data ingestion run in the metadata store"""

        run_name = (
            data_ingestion_run.collection_name
            + "-"
            + "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
        )
        created_data_ingestion_run = CollectionDataIngestionRun(
            name=run_name,
            collection_name=data_ingestion_run.collection_name,
            data_source_fqn=data_ingestion_run.data_source_fqn,
            parser_config=data_ingestion_run.parser_config,
            data_ingestion_mode=data_ingestion_run.data_ingestion_mode,
            status=DataIngestionRunStatus.INITIALIZED,
            raise_error_on_failure=data_ingestion_run.raise_error_on_failure,
        )

        try:
            run_data = created_data_ingestion_run.model_dump()
            run_data["parser_config"] = json.dumps(run_data["parser_config"])
            data_ingestion_run: "PrismaCollectionDataIngestionRun" = (
                await self.db.collectioningestionruns.create(data=run_data)
            )
            return CollectionDataIngestionRun.model_validate(data_ingestion_run.model_dump())
        except Exception as e:
            logger.exception(f"Failed to create data ingestion run: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to create data ingestion run: {e}"
            )

    async def aget_data_ingestion_run(
        self, data_ingestion_run_name: str, no_cache: bool = False
    ) -> Optional[CollectionDataIngestionRun]:
        try:
            data_ingestion_run: Optional[
                "PrismaCollectionDataIngestionRun"
            ] = await self.db.collectioningestionruns.find_first(
                where={"name": data_ingestion_run_name}
            )
            logger.info(f"Data ingestion run: {data_ingestion_run}")
            if data_ingestion_run:
                return CollectionDataIngestionRun.model_validate(data_ingestion_run.model_dump())
            return None
        except Exception as e:
            logger.exception(f"Failed to get data ingestion run: {e}")
            raise HTTPException(status_code=500, detail=f"{e}")


    
    async def aupdate_data_ingestion_run_status(
        self, data_ingestion_run_name: str, status: CollectionDataIngestionRun
    ) -> CollectionDataIngestionRun:
        """Update the status of a data ingestion run"""
        try:
            updated_data_ingestion_run: Optional[
                "PrismaCollectionDataIngestionRun"
            ] = await self.db.collectioningestionruns.update(
                where={"name": data_ingestion_run_name}, data={"status": status}
            )
            if not updated_data_ingestion_run:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to update ingestion run {data_ingestion_run_name!r}. No such record found",
                )

            return CollectionDataIngestionRun.model_validate(
                updated_data_ingestion_run.model_dump()
            )
        except Exception as e:
            logger.exception(f"Failed to update data ingestion run status: {e}")
            raise HTTPException(status_code=500, detail=f"{e}")

    async def alog_errors_for_data_ingestion_run(
        self, data_ingestion_run_name: str, errors: Dict[str, Any]
    ) -> None:
        """Log errors for the given data ingestion run"""
        try:
            updated_data_ingestion_run: Optional[
                "PrismaCollectionDataIngestionRun"
            ] = await self.db.collectioningestionruns.update(
                where={"name": data_ingestion_run_name},
                data={"errors": json.dumps(errors)},
            )
            if not updated_data_ingestion_run:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to update ingestion run {data_ingestion_run_name!r}. No such record found",
                )
        except Exception as e:
            logger.exception(
                f"Failed to log errors data ingestion run {data_ingestion_run_name}: {e}"
            )
            raise HTTPException(status_code=500, detail=f"{e}")
    
    async def aget_data_ingestion_runs(
        self, collection_name: str, data_source_fqn: str = None
    ) -> List[CollectionDataIngestionRun]:
        """Get all data ingestion runs for a collection"""
        try:
            data_ingestion_runs: List[
                "PrismaCollectionDataIngestionRun"
            ] = await self.db.collectioningestionruns.find_many(
                where={"collection_name": collection_name}, order={"id": "desc"}
            )
            return [
                CollectionDataIngestionRun.model_validate(data_ir.model_dump())
                for data_ir in data_ingestion_runs
            ]
        except Exception as e:
            logger.exception(f"Failed to get data ingestion runs: {e}")
            raise HTTPException(status_code=500, detail=f"{e}")

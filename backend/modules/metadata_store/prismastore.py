import asyncio
import json
import os
import shutil
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from fastapi import HTTPException
from prisma import Prisma
from backend.types.core import (
    Knowledge
)
from backend.logger import logger
from backend.modules.metadata_store.base import BaseMetadataStore
from backend.settings import settings
from backend.types.core import (
    CreateDataSource,
    DataSource,
    RagApplication,
)
if TYPE_CHECKING:
    # TODO (chiragjn): Can we import these safely even if the prisma client might not be generated yet?
    from prisma.models import DataSource as PrismaDataSource
    from prisma.models import RagApps as PrismaRagApplication

# TODO (chiragjn):
#   - Use transactions!
#   - Some methods are using json.dumps - not sure if this is the right way to send data via prisma client
#   - primsa generates its own DB entity classes - ideally we should be using those instead of call
#       .model_dump() on the pydantic objects. See prisma.models and prisma.actions
#


class PrismaStore(BaseMetadataStore):
    def __init__(self, *args, db, **kwargs) -> None:
        self.db = db
        super().__init__(*args, **kwargs)

    @classmethod
    async def aconnect(cls, **kwargs):
        try:
            db = Prisma()
            await db.connect()
            logger.info(f"Connected to Prisma")
            return cls(db=db, **kwargs)
        except Exception as e:
            logger.exception(f"Failed to connect to Prisma: {e}")
            raise HTTPException(status_code=500, detail="Failed to connect to Prisma")

    async def aget_knowledge_by_name(
        self, knowledge_name: str, no_cache: bool = True
    ) -> Optional[Knowledge]:
        try:
            knowledge: Optional[
                "PrismaKnowledge"
            ] = await self.db.knowledge.find_first(where={"name": knowledge_name})
            if knowledge:
                return Knowledge.model_validate(knowledge.model_dump())
            return None
        except Exception as e:
            logger.exception(f"Failed to get knowledge by name: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get knowledge by name"
            )

    

    ######
    # DATA SOURCE APIS
    ######
    async def aget_data_source_from_fqn(self, fqn: str) -> Optional[DataSource]:
        try:
            data_source: Optional[
                "PrismaDataSource"
            ] = await self.db.datasource.find_first(where={"fqn": fqn})
            if data_source:
                return DataSource.model_validate(data_source.model_dump())
            return None
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

    async def acreate_data_source(self, data_source: CreateDataSource) -> DataSource:
        try:
            existing_data_source = await self.aget_data_source_from_fqn(data_source.fqn)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

        if existing_data_source:
            logger.exception(f"Data source with fqn {data_source.fqn} already exists")
            raise HTTPException(
                status_code=400,
                detail=f"Data source with fqn {data_source.fqn} already exists",
            )

        try:
            data = data_source.model_dump()
            data["metadata"] = json.dumps(data["metadata"])
            data_source: "PrismaDataSource" = await self.db.datasource.create(data)
            logger.info(f"Created data source: {data_source}")
            return DataSource.model_validate(data_source.model_dump())
        except Exception as e:
            logger.exception(f"Failed to create data source: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

    async def aget_data_sources(self) -> List[DataSource]:
        try:
            data_sources: List["PrismaDataSource"] = await self.db.datasource.find_many(
                order={"id": "desc"}
            )
            return [DataSource.model_validate(ds.model_dump()) for ds in data_sources]
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")


        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error: {e}",
            )

    
    async def alist_data_sources(
        self,
    ) -> List[Dict[str, str]]:
        try:
            data_sources = await self.aget_data_sources()
            return [data_source.model_dump() for data_source in data_sources]
        except Exception as e:
            logger.exception(f"Failed to list data sources: {e}")
            raise HTTPException(status_code=500, detail="Failed to list data sources")

    async def adelete_data_source_by_user(self, user: dict, data_source_fqn: str) -> None:
        # Check if data source exists if not raise an error
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

        # Check if data source is associated with any collection
        try:
            collections = await self.aget_collections_by_user(user)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

        for collection in collections:
            associated_data_sources = collection.associated_data_sources
            if associated_data_sources and data_source_fqn in associated_data_sources:
                logger.error(
                    f"Data source with fqn {data_source_fqn} is already associated with "
                    f"collection {collection.name}"
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Data source with fqn {data_source_fqn} is associated "
                    f"with collection {collection.name}. Delete the necessary collections "
                    f"or unassociate them from the collection(s) before deleting the data source",
                )

        # Delete the data source
        try:
            logger.info(f"Data source to delete: {data_source}")
            deleted_datasource: Optional[
                PrismaDataSource
            ] = await self.db.datasource.delete(where={"fqn": data_source.fqn})
            if not deleted_datasource:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to delete data source {data_source.fqn!r}. No such record found",
                )
            # Delete the data from `/users_data` directory if data source is of type `localdir`
            if data_source.type == "localdir":
                data_source_uri = data_source.uri
                # data_source_uri is of the form: `/app/users_data/folder_name`
                folder_name = data_source_uri.split("/")[-1]
                folder_path = os.path.join(settings.LOCAL_DATA_DIRECTORY, folder_name)
                logger.info(
                    f"Deleting folder: {folder_path}, path exists: {os.path.exists(folder_path)}"
                )
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                else:
                    logger.error(f"Folder does not exist: {folder_path}")

        except Exception as e:
            logger.exception(f"Failed to delete data source: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete data source")

    

    ######
    # RAG APPLICATION APIS
    ######
    async def aget_rag_app(self, app_name: str) -> Optional[RagApplication]:
        """Get a RAG application from the metadata store"""
        try:
            rag_app: Optional[
                "PrismaRagApplication"
            ] = await self.db.ragapps.find_first(where={"name": app_name})
            if rag_app:
                return RagApplication.model_validate(rag_app.model_dump())
            return None
        except Exception as e:
            logger.exception(f"Failed to get RAG application by name: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to get RAG application by name"
            )

    async def acreate_rag_app(self, app: RagApplication) -> RagApplication:
        """Create a RAG application in the metadata store"""
        try:
            existing_app = await self.aget_rag_app(app.name)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=e)

        if existing_app:
            logger.error(f"RAG application with name {app.name} already exists")
            raise HTTPException(
                status_code=400,
                detail=f"RAG application with name {app.name} already exists",
            )

        try:
            logger.info(f"Creating RAG application: {app.model_dump()}")
            rag_app_data = app.model_dump()
            rag_app_data["config"] = json.dumps(rag_app_data["config"])
            rag_app: "PrismaRagApplication" = await self.db.ragapps.create(
                data=rag_app_data
            )
            return RagApplication.model_validate(rag_app.model_dump())
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

    async def alist_rag_apps(self) -> List[str]:
        """List all RAG applications from the metadata store"""
        try:
            rag_apps: List["PrismaRagApplication"] = await self.db.ragapps.find_many()
            return [rag_app.name for rag_app in rag_apps]
        except Exception as e:
            logger.exception(f"Failed to list RAG applications: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to list RAG applications"
            )

    async def adelete_rag_app(self, app_name: str):
        """Delete a RAG application from the metadata store"""
        try:
            deleted_rag_app: Optional[
                "PrismaRagApplication"
            ] = await self.db.ragapps.delete(where={"name": app_name})
            if not deleted_rag_app:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to delete RAG application {app_name!r}. No such record found",
                )
        except Exception as e:
            logger.exception(f"Failed to delete RAG application: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to delete RAG application"
            )


if __name__ == "__main__":
    # initialize the PrismaStore
    prisma_store = PrismaStore.aconnect()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(prisma_store)

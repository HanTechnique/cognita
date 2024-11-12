from backend.types.knowledge import (
    CreateKnowledgeDataIngestionRun,
    KnowledgeDataIngestionRun,
)
from backend.types.core import (
    DataIngestionRunStatus,Knowledge
)
from backend.types.knowledge import (
    AssociateDataSourceWithKnowledge,
    CreateKnowledge,
)
import json
import random
import string
from typing import List, Optional, Any, Dict
from backend.modules.metadata_store.prismastore import PrismaStore
from backend.logger import logger
from fastapi import HTTPException
from backend.types.core import AssociatedDataSources


class KnowledgePrismaStore(PrismaStore):
    def __init__(self, client: PrismaStore) -> None:
        self.db = client.db

    async def aget_data_knowledge_ingestion_runs(
        self, knowledge_name: str, data_source_fqn: str = None
    ) -> List[KnowledgeDataIngestionRun]:
        """Get all data ingestion runs for a knowledge"""
        try:
            data_knowledge_ingestion_runs: List[
                "PrismaKnowledgeDataIngestionRun"
            ] = await self.db.knowledgeingestionruns.find_many(
                where={"knowledge_name": knowledge_name}, order={"id": "desc"}
            )
            return [
                KnowledgeDataIngestionRun.model_validate(data_ir.model_dump())
                for data_ir in data_knowledge_ingestion_runs
            ]
        except Exception as e:
            logger.exception(f"Failed to get data ingestion runs: {e}")
            raise HTTPException(status_code=500, detail=f"{e}")
    

    async def acreate_knowledge_by_user(self, user: dict, knowledge: CreateKnowledge) -> Knowledge:
        try:
            existing_knowledge = await self.aget_knowledge_by_name_and_user(knowledge.name, user)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=e)

        if existing_knowledge:
            logger.error(f"Knowledge with name {knowledge.name} already exists")
            raise HTTPException(
                status_code=400,
                detail=f"Knowledge with name {knowledge.name} already exists",
            )

        try:
            logger.info(f"Creating knowledge: {knowledge.model_dump()}")
            knowledge_data = knowledge.model_dump()
            knowledge: "PrismaKnowledge" = await self.db.knowledge.create(
                data=knowledge_data
            )
            return Knowledge.model_validate(knowledge.model_dump())
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

    async def aget_retrieve_knowledge_by_name(
        self, knowledge_name: str, no_cache: bool = True
    ) -> Optional[Knowledge]:
        knowledge: "PrismaKnowledge" = await self.aget_knowledge_by_name(
            knowledge_name, no_cache
        )
        return Knowledge.model_validate(knowledge.model_dump())

    async def aget_knowledges_by_user(self, user: dict) -> List[Knowledge]:
        try:
            user_id = user['sub']  # Implement user authentication
            knowledges: List["PrismaKnowledge"] = await self.db.knowledge.find_many(
                where={"owner_id": user_id},
                order={"id": "desc"}
            )
            return [Knowledge.model_validate(c.model_dump()) for c in knowledges]
        except Exception as e:
            logger.exception(f"Failed to get knowledges: {e}")
            raise HTTPException(status_code=500, detail="Failed to get knowledges")

    async def alist_knowledges_by_user(self, user: dict) -> List[str]:
        try:
            knowledges = await self.aget_knowledges_by_user(user)
            return [knowledge.name for knowledge in knowledges]
        except Exception as e:
            logger.exception(f"Failed to list knowledges: {e}")
            raise HTTPException(status_code=500, detail="Failed to list knowledges")

    async def adelete_knowledge(self, knowledge_name: str, include_runs=False):
        try:
            deleted_knowledge: Optional[
                "PrismaKnowledge"
            ] = await self.db.knowledge.delete(where={"name": knowledge_name})
            if not deleted_knowledge:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to delete knowledge {knowledge_name!r}. No such record found",
                )
            if include_runs:
                try:
                    _deleted_count = await self.db.knowledgeingestionruns.delete_many(
                        where={"knowledge_name": knowledge_name}
                    )
                except Exception as e:
                    logger.exception(f"Failed to delete data ingestion runs: {e}")
        except Exception as e:
            logger.exception(f"Failed to delete knowledge: {e}")
            raise HTTPException(status_code=500, detail="Failed to delete knowledge")
    async def aassociate_data_source_with_knowledge(
        self,
        user: dict,
        knowledge_name: str,
        data_source_association: AssociateDataSourceWithKnowledge,
    ) -> Knowledge:
        try:
            existing_knowledge = await self.aget_knowledge_by_name_and_user(knowledge_name, user)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

        if not existing_knowledge:
            logger.error(f"Knowledge with name {knowledge_name} does not exist")
            raise HTTPException(
                status_code=400,
                detail=f"Knowledge with name {knowledge_name} does not exist",
            )

        try:
            data_source = await self.aget_data_source_from_fqn_and_user(
                user,
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
            # Append datasource to existing knowledge
            existing_knowledge_associated_data_sources = (
                existing_knowledge.associated_data_sources
            )
            logger.info(
                f"Existing associated data sources: {existing_knowledge_associated_data_sources}"
            )

            data_src_to_associate = AssociatedDataSources(
                data_source_fqn=data_source_association.data_source_fqn,
                parser_config=data_source_association.parser_config,
                data_source=data_source,
            )

            if existing_knowledge_associated_data_sources:
                existing_knowledge_associated_data_sources[
                    data_src_to_associate.data_source_fqn
                ] = data_src_to_associate
            else:
                existing_knowledge_associated_data_sources = {
                    data_src_to_associate.data_source_fqn: data_src_to_associate
                }

            logger.info(existing_knowledge_associated_data_sources)
            associated_data_sources: Dict[str, Dict[str, Any]] = {}
            for (
                data_source_fqn,
                data_source,
            ) in existing_knowledge_associated_data_sources.items():
                associated_data_sources[data_source_fqn] = data_source.model_dump()

            updated_knowledge: Optional[
                "PrismaKnowledge"
            ] = await self.db.knowledge.update(
                where={"name": knowledge_name},
                data={"associated_data_sources": json.dumps(associated_data_sources)},
            )
            if not updated_knowledge:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to associate data source with knowledge {knowledge_name!r}. "
                    f"No such record found",
                )
            return Knowledge.model_validate(updated_knowledge.model_dump())

        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Error: {e}",
            )
    async def aunassociate_data_source_with_knowledge(
        self, user: dict, knowledge_name: str, data_source_fqn: str
    ) -> Knowledge:
        try:
            knowledge: Knowledge = await self.aget_knowledge_by_name_and_user(knowledge_name, user)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

        if not knowledge:
            logger.error(f"Knowledge with name {knowledge_name} does not exist")
            raise HTTPException(
                status_code=400,
                detail=f"Knowledge with name {knowledge_name} does not exist",
            )

        try:
            data_source = await self.aget_data_source_from_fqn_and_user(user, data_source_fqn)
        except Exception as e:
            logger.exception(f"Error: {e}")
            raise HTTPException(status_code=500, detail=f"Error: {e}")

        if not data_source:
            logger.error(f"Data source with fqn {data_source_fqn} does not exist")
            raise HTTPException(
                status_code=400,
                detail=f"Data source with fqn {data_source_fqn} does not exist",
            )

        associated_data_sources = knowledge.associated_data_sources
        if not associated_data_sources:
            logger.error(
                f"No associated data sources found for knowledge {knowledge_name}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"No associated data sources found for knowledge {knowledge_name}",
            )
        if data_source_fqn not in associated_data_sources:
            logger.error(
                f"Data source with fqn {data_source_fqn} not associated with knowledge {knowledge_name}"
            )
            raise HTTPException(
                status_code=400,
                detail=f"Data source with fqn {data_source_fqn} not associated with knowledge {knowledge_name}",
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

            updated_knowledge: Optional[
                "PrismaKnowledge"
            ] = await self.db.knowledge.update(
                where={"name": knowledge_name},
                data={
                    "associated_data_sources": json.dumps(
                        updated_associated_data_sources
                    )
                },
            )
            if not updated_knowledge:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to unassociate data source from knowledge. "
                    f"No knowledge found with name {knowledge_name}",
                )
            logger.info(f"Updated knowledge: {updated_knowledge}")
            return Knowledge.model_validate(updated_knowledge.model_dump())
        except Exception as e:
            logger.exception(f"Failed to unassociate data source with knowledge: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to unassociate data source with knowledge",
            )


    ######
    # DATA INGESTION RUN APIS
    ######
    async def acreate_data_ingestion_run(
        self, data_ingestion_run: CreateKnowledgeDataIngestionRun
    ) -> KnowledgeDataIngestionRun:
        """Create a data ingestion run in the metadata store"""

        run_name = (
            data_ingestion_run.knowledge_name
            + "-"
            + "".join(random.choices(string.ascii_lowercase + string.digits, k=5))
        )
        created_data_ingestion_run = KnowledgeDataIngestionRun(
            name=run_name,
            knowledge_name=data_ingestion_run.knowledge_name,
            data_source_fqn=data_ingestion_run.data_source_fqn,
            parser_config=data_ingestion_run.parser_config,
            data_ingestion_mode=data_ingestion_run.data_ingestion_mode,
            status=DataIngestionRunStatus.INITIALIZED,
            raise_error_on_failure=data_ingestion_run.raise_error_on_failure,
        )

        try:
            run_data = created_data_ingestion_run.model_dump()
            run_data["parser_config"] = json.dumps(run_data["parser_config"])
            data_ingestion_run: "PrismaKnowledgeDataIngestionRun" = (
                await self.db.knowledgeingestionruns.create(data=run_data)
            )
            return KnowledgeDataIngestionRun.model_validate(data_ingestion_run.model_dump())
        except Exception as e:
            logger.exception(f"Failed to create data ingestion run: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to create data ingestion run: {e}"
            )

    async def aget_data_ingestion_run(
        self, data_ingestion_run_name: str, no_cache: bool = False
    ) -> Optional[KnowledgeDataIngestionRun]:
        try:
            data_ingestion_run: Optional[
                "PrismaKnowledgeDataIngestionRun"
            ] = await self.db.knowledgeingestionruns.find_first(
                where={"name": data_ingestion_run_name}
            )
            logger.info(f"Data ingestion run: {data_ingestion_run}")
            if data_ingestion_run:
                return KnowledgeDataIngestionRun.model_validate(data_ingestion_run.model_dump())
            return None
        except Exception as e:
            logger.exception(f"Failed to get data ingestion run: {e}")
            raise HTTPException(status_code=500, detail=f"{e}")


    
    async def aupdate_data_ingestion_run_status(
        self, data_ingestion_run_name: str, status: DataIngestionRunStatus
    ) -> KnowledgeDataIngestionRun:
        """Update the status of a data ingestion run"""
        try:
            updated_data_ingestion_run: Optional[
                "PrismaKnowledgeDataIngestionRun"
            ] = await self.db.knowledgeingestionruns.update(
                where={"name": data_ingestion_run_name}, data={"status": status}
            )
            if not updated_data_ingestion_run:
                raise HTTPException(
                    status_code=404,
                    detail=f"Failed to update ingestion run {data_ingestion_run_name!r}. No such record found",
                )

            return KnowledgeDataIngestionRun.model_validate(
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
                "PrismaKnowledgeDataIngestionRun"
            ] = await self.db.knowledgeingestionruns.update(
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
        self, knowledge_name: str, data_source_fqn: str = None
    ) -> List[KnowledgeDataIngestionRun]:
        """Get all data ingestion runs for a collection"""
        try:
            data_ingestion_runs: List[
                "PrismaKnowledgeDataIngestionRun"
            ] = await self.db.knowledgeingestionruns.find_many(
                where={"knowledge_name": knowledge_name}, order={"id": "desc"}
            )
            return [
                KnowledgeDataIngestionRun.model_validate(data_ir.model_dump())
                for data_ir in data_ingestion_runs
            ]
        except Exception as e:
            logger.exception(f"Failed to get data ingestion runs: {e}")
            raise HTTPException(status_code=500, detail=f"{e}")

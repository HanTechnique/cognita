from fastapi import APIRouter, HTTPException, Path, Request
from fastapi.responses import JSONResponse
from backend.modules.metadata_store.knowledges.prismastore import KnowledgePrismaStore
from backend.indexer.knowledges.indexer import ingest_data as ingest_data_to_knowledge
from backend.logger import logger
from backend.modules.metadata_store.client import get_client
from backend.modules.model_gateway.model_gateway import model_gateway
from backend.modules.graph.client import GRAPHRAG_STORE_CLIENT
from backend.types.knowledge import (
    AssociateDataSourceWithKnowledge,
    AssociateDataSourceWithKnowledgeDto,
    CreateKnowledge,
    CreateKnowledgeDto,
    ListKnowledgeDataIngestionRunsDto,
    IngestDataToKnowledgeDto,
    UnassociateDataSourceWithKnowledgeDto,
)
router = APIRouter(prefix="/v1/knowledges", tags=["knowledges"])


@router.get("")
async def get_knowledges():
    """API to list all knowledges with details"""
    try:
        logger.debug("Listing all the knowledges...")
        client = await get_client()
        client = KnowledgePrismaStore(client)
        knowledges = await client.aget_knowledges()
        if knowledges is None:
            return JSONResponse(content={"knowledges": []})
        return JSONResponse(
            content={"knowledges": [obj.model_dump() for obj in knowledges]}
        )
    except Exception as exp:
        logger.exception("Failed to get knowledge")
        raise HTTPException(status_code=500, detail=str(exp))


@router.get("/list")
async def list_knowledges():
    try:
        client = await get_client()
        client = KnowledgePrismaStore(client)
        knowledges = await client.alist_knowledges()
        return JSONResponse(content={"knowledges": knowledges})
    except Exception as exp:
        logger.exception("Failed to list knowledges")
        raise HTTPException(status_code=500, detail=str(exp))


@router.get("/{knowledge_name}")
async def get_knowledge_by_name(knowledge_name: str = Path(title="Knowledge name")):
    """Get the knowledge config given its name"""
    try:
        client = await get_client()
        client = KnowledgePrismaStore(client)
        knowledge = await client.aget_knowledge_by_name(knowledge_name)
        if knowledge is None:
            return JSONResponse(content={"knowledge": []})
        return JSONResponse(content={"knowledge": knowledge.model_dump()})
    except HTTPException as exp:
        raise exp
    except Exception as exp:
        logger.exception("Failed to get knowledge by name")
        raise HTTPException(status_code=500, detail=str(exp))


@router.post("")
async def create_knowledge(knowledge: CreateKnowledgeDto):
    """API to create a knowledge"""
    try:
        logger.info(f"Creating knowledge {knowledge.name}...")
        client = await get_client()
        client = KnowledgePrismaStore(client)
        created_knowledge = await client.acreate_knowledge(
            knowledge=CreateKnowledge(
                name=knowledge.name,
                description=knowledge.description,
                embedder_config=knowledge.embedder_config,
            )
        )
        logger.info(f"Creating knowledge {knowledge.name} on vector db...")
        GRAPHRAG_STORE_CLIENT.create_knowledge(
            knowledge_name=knowledge.name,
        )
        logger.info(f"Created knowledge... {created_knowledge}")

        if knowledge.associated_data_sources:
            for data_source in knowledge.associated_data_sources:
                await client.aassociate_data_source_with_knowledge(
                    knowledge_name=created_knowledge.name,
                    data_source_association=AssociateDataSourceWithKnowledge(
                        data_source_fqn=data_source.data_source_fqn,
                        parser_config=data_source.parser_config,
                    ),
                )
            created_knowledge = await client.aget_knowledge_by_name(
                knowledge_name=created_knowledge.name
            )
        return JSONResponse(
            content={"knowledge": created_knowledge.model_dump()}, status_code=201
        )
    except HTTPException as exp:
        raise exp
    except Exception as exp:
        logger.exception(f"Failed to create knowledge")
        raise HTTPException(status_code=500, detail=str(exp))


@router.post("/associate_data_source")
async def associate_data_source_to_knowledge(
    request: AssociateDataSourceWithKnowledgeDto,
):
    """Add a data source to the knowledge"""
    try:
        client = await get_client()
        client = KnowledgePrismaStore(client)
        knowledge = await client.aassociate_data_source_with_knowledge(
            knowledge_name=request.knowledge_name,
            data_source_association=AssociateDataSourceWithKnowledge(
                data_source_fqn=request.data_source_fqn,
                parser_config=request.parser_config,
            ),
        )
        return JSONResponse(content={"knowledge": knowledge.model_dump()})
    except HTTPException as exp:
        raise exp
    except Exception as exp:
        logger.exception("Failed to associate data source")
        raise HTTPException(status_code=500, detail=str(exp))


@router.post("/unassociate_data_source")
async def unassociate_data_source_from_knowledge(
    request: UnassociateDataSourceWithKnowledgeDto,
):
    """Remove a data source to the knowledge"""
    try:
        client = await get_client()
        client = KnowledgePrismaStore(client)
        knowledge = await client.aunassociate_data_source_with_knowledge(
            knowledge_name=request.knowledge_name,
            data_source_fqn=request.data_source_fqn,
        )
        return JSONResponse(content={"knowledge": knowledge.model_dump()})
    except HTTPException as exp:
        raise exp
    except Exception as exp:
        logger.exception("Failed to unassociate data source from knowledge")
        raise HTTPException(status_code=500, detail=str(exp))


@router.post("/ingest")
async def ingest_data(
    ingest_data_to_knowledge_dto: IngestDataToKnowledgeDto, request: Request
):
    """Ingest data into the knowledge"""
    try:
        process_pool = request.app.state.process_pool
    except AttributeError:
        process_pool = None
    try:
        return await ingest_data_to_knowledge(
            ingest_data_to_knowledge_dto, pool=process_pool
        )
    except HTTPException as exp:
        raise exp
    except Exception as exp:
        logger.exception("Failed to ingest data")
        raise HTTPException(status_code=500, detail=str(exp))


@router.delete("/{knowledge_name}")
async def delete_knowledge(knowledge_name: str = Path(title="Knowledge name")):
    """Delete knowledge given its name"""
    try:
        client = await get_client()
        client = KnowledgePrismaStore(client)
        await client.adelete_knowledge(knowledge_name, include_runs=True)
        GRAPHRAG_STORE_CLIENT.delete_knowledge(knowledge_name=knowledge_name)
        return JSONResponse(content={"deleted": True})
    except HTTPException as exp:
        raise exp
    except Exception as exp:
        logger.exception("Failed to delete knowledge")
        raise HTTPException(status_code=500, detail=str(exp))


@router.post("/data_ingestion_runs/list")
async def list_data_ingestion_runs(request: ListKnowledgeDataIngestionRunsDto):
    client = await get_client()
    client = KnowledgePrismaStore(client)
    data_ingestion_runs = await client.aget_data_ingestion_runs(
        request.knowledge_name, request.data_source_fqn
    )
    return JSONResponse(
        content={
            "data_ingestion_runs": [obj.model_dump() for obj in data_ingestion_runs]
        }
    )


@router.get("/data_ingestion_runs/{data_ingestion_run_name}/status")
async def get_knowledge_status(
    data_ingestion_run_name: str = Path(title="Data Ingestion Run name"),
):
    """Get status for given data ingestion run"""
    client = await get_client()
    client = KnowledgePrismaStore(client)
    data_ingestion_run = await client.aget_data_ingestion_run(
        data_ingestion_run_name=data_ingestion_run_name, no_cache=True
    )
    if data_ingestion_run is None:
        raise HTTPException(
            status_code=404,
            detail=f"Data ingestion run {data_ingestion_run_name} not found",
        )

    return JSONResponse(
        content={
            "status": data_ingestion_run.status.value,
            "message": f"Data ingestion job run {data_ingestion_run.name} in {data_ingestion_run.status.value}. Check logs for more details.",
        }
    )

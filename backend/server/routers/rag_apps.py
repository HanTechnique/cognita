from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse

from fastapi import Depends
from backend.server.auth import get_current_user
from backend.logger import logger
from backend.modules.metadata_store.client import get_client
from backend.types.core import CreateRagApplication

router = APIRouter(prefix="/v1/apps", tags=["apps"])


@router.post("")
async def register_rag_app_by_user(
    rag_app: CreateRagApplication,
    user: dict = Depends(get_current_user)
):
    """Create a rag app"""
    try:
        logger.info(f"Creating rag app: {rag_app}")
        client = await get_client()
        created_rag_app = await client.acreate_rag_app_by_user(rag_app,user)
        return JSONResponse(
            content={"rag_app": created_rag_app.model_dump()}, status_code=201
        )
    except HTTPException as exp:
        raise exp
    except Exception as exp:
        logger.exception("Failed to add rag app")
        raise HTTPException(status_code=500, detail=str(exp))


@router.get("/list")
async def list_rag_apps_by_user(user: dict = Depends(get_current_user)):
    """Get rag apps"""
    try:
        client = await get_client()
        rag_apps = await client.alist_rag_apps_by_user(user)
        return JSONResponse(content={"rag_apps": rag_apps})
    except Exception as exp:
        logger.exception("Failed to get rag apps")
        raise HTTPException(status_code=500, detail=str(exp))


@router.get("/{app_name}")
async def get_rag_app_by_name_and_user(
    app_name: str = Path(title="App name"), 
    user: dict = Depends(get_current_user)):
    """Get the rag app config given its name"""
    try:
        client = await get_client()
        rag_app = await client.aget_rag_app_by_user(app_name, user)
        if rag_app is None:
            return JSONResponse(content={"rag_app": []})
        return JSONResponse(content={"rag_app": rag_app.model_dump()})
    except HTTPException as exp:
        raise exp


@router.delete("/{app_name}")
async def delete_rag_app_by_user(
    app_name: str = Path(title="App name"), 
    user: dict = Depends(get_current_user)):
    """Delete the rag app config given its name"""
    try:
        client = await get_client()
        await client.adelete_rag_app(app_name, user)
        return JSONResponse(content={"deleted": True})
    except HTTPException as exp:
        raise exp
    except Exception as exp:
        logger.exception("Failed to delete rag app")
        raise HTTPException(status_code=500, detail=str(exp))

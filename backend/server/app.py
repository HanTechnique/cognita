import multiprocessing as mp
from contextlib import asynccontextmanager
from backend.server.auth import get_current_user
from fastapi import FastAPI, Depends
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.modules.query_controllers.query_controller import QUERY_CONTROLLER_REGISTRY
from backend.server.routers.collection import router as collection_router
from backend.server.routers.knowledge import router as knowledge_router
from backend.server.routers.users import router as users_router
from backend.server.routers.teams import router as teams_router
from backend.server.routers.plans import router as plans_router

from backend.server.routers.components import router as components_router
from backend.server.routers.data_source import router as datasource_router
from backend.server.routers.internal import router as internal_router
from backend.server.routers.rag_apps import router as rag_apps_router
from backend.settings import settings
from backend.utils import AsyncProcessPoolExecutor

@asynccontextmanager
async def _process_pool_lifespan_manager(app: FastAPI):
    app.state.process_pool = None
    if settings.PROCESS_POOL_WORKERS > 0:
        app.state.process_pool = AsyncProcessPoolExecutor(
            max_workers=settings.PROCESS_POOL_WORKERS,
            # Setting to spawn because we don't want to fork - it can cause issues with the event loop
            mp_context=mp.get_context("spawn"),
        )
    yield  # FastAPI runs here
    if app.state.process_pool is not None:
        app.state.process_pool.shutdown(wait=True)

# FastAPI Initialization
app = FastAPI(
    title="Backend for RAG",
    root_path=settings.TFY_SERVICE_ROOT_PATH,
    docs_url="/",
    lifespan=_process_pool_lifespan_manager,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health-check")
def health_check():
    return JSONResponse(content={"status": "OK"})


app.include_router(components_router)
app.include_router(datasource_router)
app.include_router(rag_apps_router)
app.include_router(collection_router)
app.include_router(knowledge_router)
app.include_router(internal_router)
app.include_router(users_router)
app.include_router(teams_router)
app.include_router(plans_router)


# Register Query Controllers dynamically as FastAPI routers
for cls in QUERY_CONTROLLER_REGISTRY.values():
    router: APIRouter = cls.get_router()
    app.include_router(router)


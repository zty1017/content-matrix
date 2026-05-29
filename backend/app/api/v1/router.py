from fastapi import APIRouter

from backend.app.api.v1 import assets, demo_contexts, source, tasks


api_router = APIRouter()
api_router.add_api_route("", lambda: {"status": "ok"}, include_in_schema=False)
api_router.include_router(source.router)
api_router.include_router(demo_contexts.router)
api_router.include_router(assets.router)
api_router.include_router(tasks.router)

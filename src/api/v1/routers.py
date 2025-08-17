from fastapi import APIRouter
from api.v1.endpoints.asr import router as asr_router
from api.v1.endpoints.llm import router as llm_router
from api.v1.endpoints.response import router as response_router

routers = APIRouter()
routers.include_router(asr_router, prefix="/api/v1/asr")
routers.include_router(llm_router, prefix="/api/v1/llm")
routers.include_router(response_router, prefix="/api/v1/response")
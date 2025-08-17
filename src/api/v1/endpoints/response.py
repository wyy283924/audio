from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

from api.v1.endpoints.asr import get_asr_response
from api.v1.endpoints.llm import get_llm_response

router = APIRouter()

class Message(BaseModel):
    method: str
    data: List[str]


@router.post("/")
async def root(message: Message):
    if message.method == "audio":
        return await get_asr_response(message.data)
    elif message.method == "text":
        return await get_llm_response(message.data[0])
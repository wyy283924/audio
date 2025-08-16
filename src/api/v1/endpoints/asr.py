import base64
from typing import List

from fastapi import APIRouter

from src.api.v1.endpoints.llm import get_llm_response
from src.services.asr_service import decode_opus, speech_to_text, init_asr

router = APIRouter()

@router.get("/response")
async def get_asr_response(data: List[str]):
    opus_data = [base64.b64decode(item) for item in data]
    pcm_data = decode_opus(opus_data)
    model = init_asr()
    # 调用ASR服务
    result = speech_to_text(model, pcm_data, audio_format="pcm")

    return await get_llm_response(result)
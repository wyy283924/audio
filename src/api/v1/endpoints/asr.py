import base64
from typing import List

from fastapi import APIRouter, Body

from api.v1.endpoints.llm import get_llm_response
from services.asr_service import decode_opus, speech_to_text, init_asr

router = APIRouter()

@router.post("/response")
async def get_asr_response(data: List[str] = Body(..., embed=True)):
    try:
        opus_data = [base64.b64decode(item) for item in data]
        model =  init_asr()
        # 调用ASR服务
        result = await speech_to_text(model, opus_data, audio_format="opus")
        # 获取LLM响应
        return await get_llm_response(result)
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
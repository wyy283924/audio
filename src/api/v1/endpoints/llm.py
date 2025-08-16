from fastapi import APIRouter

from src.services.llm_service import response_no_stream, init_llm
from src.services.tts_service import text_to_speak
from src.utils.util import audio_bytes_to_data

router = APIRouter()

@router.get("/response")
async def get_llm_response(result):
    client = init_llm()
    response = response_no_stream(
        system_prompt="You are a helpful assistant.",
        user_prompt=result,
        client=client)
    # 调用TTS服务将文本转换为语音
    audio_bytes = await text_to_speak(response)
    if audio_bytes:
        audio_datas, _ = audio_bytes_to_data(
            audio_bytes, file_type="mp3", is_opus=True
        )
    return {
        "asr_result": result[0],
        "llm_response": response,
        "tts_result": audio_datas  # 如果需要TTS结果，可以在这里添加逻辑
    }
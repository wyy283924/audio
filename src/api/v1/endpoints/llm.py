from fastapi import APIRouter
from fastapi import Body
from services.llm_service import response_no_stream, init_llm
from services.tts_service import text_to_speak
from utils.util import audio_bytes_to_data
import base64

router = APIRouter()

@router.post("/response")
async def get_llm_response(result:str = Body(..., embed=True)):
    client =  init_llm()
    response = await response_no_stream(
        system_prompt="You are a helpful assistant.",
        user_prompt=result,
        client=client)
    # 调用TTS服务将文本转换为语音
    audio_bytes = await text_to_speak(response)
    if audio_bytes:
        # 将音频字节数据转换为数据列表
        audio_datas, _ = audio_bytes_to_data(
            audio_bytes, file_type="mp3", is_opus=True
        )
    
    return {
        "asr_result": result[0],
        "llm_response": response,
        "tts_result": [base64.b64encode(item).decode("utf-8") for item in audio_datas]   # 如果需要TTS结果，可以在这里添加逻辑
    }
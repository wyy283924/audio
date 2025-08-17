import edge_tts
from fastapi import Depends

from core.config import get_tts_config


async def text_to_speak(text):
    try:
        config = get_tts_config()
        voice = config.get("voice")
        communicate = edge_tts.Communicate(text, voice=voice)
        # 返回音频二进制数据
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return audio_bytes
    except Exception as e:
        error_msg = f"Edge TTS请求失败: {e}"
        raise Exception(error_msg)  # 抛出异常，让调用方捕获
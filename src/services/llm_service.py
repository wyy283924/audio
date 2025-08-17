from functools import lru_cache

import httpx
import openai

from fastapi import Depends

from core.config import get_llm_config
from core.logger import setup_logging
from utils.util import check_model_key

TAG = __name__
logger = setup_logging()

@lru_cache(maxsize=1)
def init_llm():
    config = get_llm_config()
    api_key = config.get("api_key")
    base_url = config.get("url")
    timeout = config.get("timeout", 300)
    timeout = int(timeout) if timeout else 300

    model_key_msg = check_model_key("LLM", api_key)
    if model_key_msg:
        logger.bind(tag=TAG).error(model_key_msg)
    client = openai.OpenAI(api_key=api_key, base_url=base_url, timeout=httpx.Timeout(timeout))
    return client


async def response_no_stream(system_prompt, user_prompt, client):
    try:
        config = get_llm_config()
        # 构造对话格式
        dialogue = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        result = ""
        async for part in response(dialogue, client, config):
            result += part
        return result

    except Exception as e:
        logger.bind(tag=TAG).error(f"Error in Ollama response generation: {e}")
        return "【LLM服务响应异常】"


async def response(dialogue, client, config: dict):
    try:
        logger.bind(tag=TAG).debug(f"Sending request to LLM with dialogue: {dialogue},{client}")

        responses = client.chat.completions.create(
            model=config.get("model_name"),
            messages=dialogue,
            stream=True,
            max_tokens=config.get("max_tokens"),
            temperature=config.get("temperature"),
            top_p=config.get("top_p"),
            frequency_penalty=config.get(
                "frequency_penalty"
            ),
        )
        logger.bind(tag=TAG).debug(f"LLM response: {responses}")
        is_active = True
        for chunk in responses:
            logger.bind(tag=TAG).debug(f"LLM response chunk: {chunk}")
            try:
                # 检查是否存在有效的choice且content不为空
                delta = (
                    chunk.choices[0].delta
                    if getattr(chunk, "choices", None)
                    else None
                )
                content = delta.content if hasattr(delta, "content") else ""
                logger.bind(tag=TAG).debug(f"LLM response chunk: {content}")
            except IndexError:
                content = ""
            if content:
                # 处理标签跨多个chunk的情况
                if "<think>" in content:
                    is_active = False
                    content = content.split("<think>")[0]
                if "</think>" in content:
                    is_active = True
                    content = content.split("</think>")[-1]
                if is_active:
                    yield content

    except Exception as e:
        logger.bind(tag=TAG).error(f"Error in response generation: {e}")

import logging
import base64
from typing import List

import gradio as gr
import numpy as np
import requests

from src.utils.util import decode_opus, pcm_to_data


async def send_to_http(message, type):
    try:
        response = requests.post(  # 使用POST方法
            "http://localhost:8002/api/v1/response",
            json={
                "type": type,
                "data": message
            }
        )
        print("请求已发送，请等待")
        logging.info("请求已发送，请等待")
        result = response.json()  # 获取JSON响应
        asr_result = result["asr_result"]
        llm_response = result["llm_response"]
        tts_result = [base64.b64decode(item) for item in result["tts_result"]]
        audio = decode_opus(tts_result)
        tts_audio = b""
        for item in audio:
            tts_audio += item
        audio_array = np.frombuffer(tts_audio, dtype=np.int16)
        return state, llm_response, (16000, audio_array)

    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败: {e}")


async def generate_audio_response(audio_in):
    chunkList = pcm_to_data(audio_in)
    return await send_to_http(chunkList, "audio")


async def generate_text_response(text):
    return await send_to_http([text], "text")


with gr.Blocks() as block:
    with gr.Group():
        with gr.Row():
            audio_out = gr.Audio(label="Spoken Answer", streaming=True, autoplay=True)
            answer = gr.Textbox(label="Answer")
            state = gr.State()
        with gr.Row():
            with gr.Column():
                audio_in = gr.Audio(label="Speak your question", sources="microphone", type="numpy")
            with gr.Column():
                text = gr.Textbox(label="write your question", lines=2, placeholder="Type your question here...")
                greet_btn = gr.Button("Greet")
        greet_btn.click(generate_text_response, text, [state, answer, audio_out])
        audio_in.stop_recording(generate_audio_response, audio_in, [state, answer, audio_out])

block.launch()

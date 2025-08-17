import logging
import base64
import opuslib_next
from typing import List

import gradio as gr
import numpy as np
import requests

async def decode_opus(opus_data: List[bytes]) -> List[bytes]:
    """将Opus音频数据解码为PCM数据"""
    try:
        decoder = opuslib_next.Decoder(16000, 1)
        pcm_data = []
        buffer_size = 960  # 每次处理960个采样点 (60ms at 16kHz)

        for i, opus_packet in enumerate(opus_data):
            try:
                if not opus_packet or len(opus_packet) == 0:
                    continue

                pcm_frame = decoder.decode(opus_packet, buffer_size)
                if pcm_frame and len(pcm_frame) > 0:
                    pcm_data.append(pcm_frame)

            except opuslib_next.OpusError as e:
                logging.warning(f"Opus解码错误，跳过数据包 {i}: {e}")
            except Exception as e:
                logging.error(f"音频处理错误，数据包 {i}: {e}")
        return pcm_data

    except Exception as e:
        logging.error(f"音频解码过程发生错误: {e}")
        return []


import numpy as np
import opuslib_next  # 确保只在需要时使用

def pcm_to_data(raw_data, is_opus=True):
    # 参数验证

    # 动态初始化编码器（仅在需要时）
    encoder = None
    if is_opus:
        encoder = opuslib_next.Encoder(16000, 1, opuslib_next.APPLICATION_AUDIO)
    
    # 常量设置
    SAMPLE_RATE = 16000
    FRAME_DURATION_MS = 60
    SAMPLES_PER_FRAME = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
    BYTES_PER_FRAME = SAMPLES_PER_FRAME * 2  # 16-bit = 2 bytes
    
    # 将整个数组转换为字节一次（提高效率）
    frame_bytes = raw_data.tobytes()
    total_bytes = len(frame_bytes)
    
    datas = []
    # 按帧处理音频数据
    for start in range(0, total_bytes, BYTES_PER_FRAME):
        end = start + BYTES_PER_FRAME
        chunk = frame_bytes[start:end]
        
        # 处理最后一帧填充
        if len(chunk) < BYTES_PER_FRAME:
            chunk = chunk.ljust(BYTES_PER_FRAME, b'\x00')
        
        if is_opus:
            frame_data = encoder.encode(chunk, SAMPLES_PER_FRAME)
        else:
            frame_data = chunk  # 已经是bytes类型
        
        datas.append(frame_data)
    
    return datas



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

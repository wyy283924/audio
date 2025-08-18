import logging
import base64
import opuslib_next
from typing import List

import gradio as gr
import numpy as np
import requests


def decode_opus(opus_data: List[bytes]) -> List[bytes]:
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


def pcm_to_data(raw_data: np.ndarray):
    raw_bytes = raw_data.tobytes()
    # 初始化编码器
    encoder = opuslib_next.Encoder(16000, 1, opuslib_next.APPLICATION_AUDIO)

    # 编码参数
    frame_duration = 60  # 60ms per frame
    frame_size = int(16000 * frame_duration / 1000)  # 960 samples/frame

    datas = []
    # 按帧处理所有音频数据（包括最后一帧可能补零）
    for i in range(0, len(raw_bytes), frame_size * 2):  # 16bit=2bytes/sample
        # 获取当前帧的二进制数据
        chunk = raw_bytes[i: i + frame_size * 2]

        # 如果最后一帧不足，补零
        if len(chunk) < frame_size * 2:
            chunk += b"\x00" * (frame_size * 2 - len(chunk))

        # 转换为numpy数组处理
        np_frame = np.frombuffer(chunk, dtype=np.int16)
        # 编码Opus数据
        frame_data = encoder.encode(np_frame.tobytes(), frame_size)


        datas.append(frame_data)

    return datas


async def send_to_http(message, type):
    try:
        print(message)
        response = requests.post(  # 使用POST方法
            "http://localhost:8002/api/v1/response",
            json={
                "method": type,
                "data": message
            }
        )
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
    chunkList = pcm_to_data(audio_in[1])
    chunkList = [base64.b64encode(item).decode("utf-8") for item in chunkList]

    return await send_to_http(chunkList, "audio")


async def generate_text_response(text):
    return await send_to_http([text], "text")


with gr.Blocks() as block:
    with gr.Group():
        with gr.Row():
            audio_out = gr.Audio(label="Spoken Answer",autoplay=True)
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

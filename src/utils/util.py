from typing import List

import opuslib_next
import numpy as np
from pydub import AudioSegment
from io import BytesIO
import os


def check_model_key(modelType, modelKey):
    if "你" in modelKey:
        return f"配置错误: {modelType} 的 API key 未设置,当前值为: {modelKey}"
    return None


def remove_punctuation_and_length(text):
    # 全角符号和半角符号的Unicode范围
    full_width_punctuations = (
        "！＂＃＄％＆＇（）＊＋，－。／：；＜＝＞？＠［＼］＾＿｀｛｜｝～"
    )
    half_width_punctuations = r'!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'
    space = " "  # 半角空格
    full_width_space = "　"  # 全角空格

    # 去除全角和半角符号以及空格
    result = "".join(
        [
            char
            for char in text
            if char not in full_width_punctuations
               and char not in half_width_punctuations
               and char not in space
               and char not in full_width_space
        ]
    )

    if result == "Yeah":
        return 0, ""
    return len(result), result


def pcm_to_data(raw_data, is_opus=True):
    # 初始化Opus编码器
    encoder = opuslib_next.Encoder(16000, 1, opuslib_next.APPLICATION_AUDIO)

    # 编码参数
    frame_duration = 60  # 60ms per frame
    frame_size = int(16000 * frame_duration / 1000)  # 960 samples/frame

    datas = []
    # 按帧处理所有音频数据（包括最后一帧可能补零）
    for i in range(0, len(raw_data), frame_size * 2):  # 16bit=2bytes/sample
        # 获取当前帧的二进制数据
        chunk = raw_data[i: i + frame_size * 2]

        # 如果最后一帧不足，补零
        if len(chunk) < frame_size * 2:
            chunk += b"\x00" * (frame_size * 2 - len(chunk))

        if is_opus:
            # 转换为numpy数组处理
            np_frame = np.frombuffer(chunk, dtype=np.int16)
            # 编码Opus数据
            frame_data = encoder.encode(np_frame.tobytes(), frame_size)
        else:
            frame_data = chunk if isinstance(chunk, bytes) else bytes(chunk)

        datas.append(frame_data)

    return datas


def audio_to_data(audio_file_path, is_opus=True):
    # 获取文件后缀名
    file_type = os.path.splitext(audio_file_path)[1]
    if file_type:
        file_type = file_type.lstrip(".")
    # 读取音频文件，-nostdin 参数：不要从标准输入读取数据，否则FFmpeg会阻塞
    audio = AudioSegment.from_file(
        audio_file_path, format=file_type, parameters=["-nostdin"]
    )

    # 转换为单声道/16kHz采样率/16位小端编码（确保与编码器匹配）
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)

    # 音频时长(秒)
    duration = len(audio) / 1000.0

    # 获取原始PCM数据（16位小端）
    raw_data = audio.raw_data
    return pcm_to_data(raw_data, is_opus), duration


def audio_bytes_to_data(audio_bytes, file_type, is_opus=True):
    """
    直接用音频二进制数据转为opus/pcm数据，支持wav、mp3、p3
    """

    # 其他格式用pydub
    audio = AudioSegment.from_file(
        BytesIO(audio_bytes), format=file_type, parameters=["-nostdin"]
    )
    audio = audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    duration = len(audio) / 1000.0
    raw_data = audio.raw_data
    return pcm_to_data(raw_data, is_opus), duration

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
                logger.bind(tag=TAG).warning(f"Opus解码错误，跳过数据包 {i}: {e}")
            except Exception as e:
                logger.bind(tag=TAG).error(f"音频处理错误，数据包 {i}: {e}")
        return pcm_data

    except Exception as e:
        logger.bind(tag=TAG).error(f"音频解码过程发生错误: {e}")
        return []

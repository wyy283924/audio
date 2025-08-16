from functools import lru_cache
from typing import Tuple, Optional, List
import opuslib_next
from fastapi import Depends

from src.core.config import load_config
from src.core.logger import setup_logging
from src.core.config import get_project_dir

from funasr.utils.postprocess_utils import rich_transcription_postprocess
from funasr import AutoModel

import psutil
import os
import io
import sys
import time

from src.utils.util import decode_opus

TAG = __name__
logger = setup_logging()

MAX_RETRIES = 2
RETRY_DELAY = 1  # 重试延迟（秒）


# 捕获标准输出
class CaptureOutput:
    def __enter__(self):
        self._output = io.StringIO()
        self._original_stdout = sys.stdout
        sys.stdout = self._output

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self._original_stdout
        self.output = self._output.getvalue()
        self._output.close()

        # 将捕获到的内容通过 logger 输出
        if self.output:
            logger.bind(tag=TAG).info(self.output.strip())


@lru_cache(maxsize=1)
async def init_asr(config: dict = Depends(load_config)):
    # 内存检测，要求大于2G
    min_mem_bytes = 2 * 1024 * 1024 * 1024
    total_mem = psutil.virtual_memory().total
    if total_mem < min_mem_bytes:
        logger.bind(tag=TAG).error(f"可用内存不足2G，当前仅有 {total_mem / (1024 * 1024):.2f} MB，可能无法启动FunASR")
    model_dir = get_project_dir()
    model_dir = model_dir + config.get("model_dir")
    output_dir = model_dir + config.get("output_dir")  # 修正配置键名

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    with CaptureOutput():
        model = AutoModel(
            model=model_dir,
            vad_kwargs={"max_single_segment_time": 30000},
            disable_update=True,
            # device="cuda:0",  # 启用GPU加速
        )
    logger.bind(tag=TAG).info("ASR初始化完成")
    return model



async def speech_to_text(
        model, opus_data: List[bytes], audio_format="opus"
) -> Optional[str]:
    logger.bind(tag=TAG).info("stt开始")
    """语音转文本主处理逻辑"""
    retry_count = 0
    while retry_count < MAX_RETRIES:
        try:
            # 合并所有opus数据包
            if audio_format == "pcm":
                pcm_data = opus_data
            else:
                pcm_data = decode_opus(opus_data)
            combined_pcm_data = b''.join(pcm_data)
            logger.bind(tag=TAG).info("stt开始", combined_pcm_data)

            # 语音识别
            start_time = time.time()
            result = model.generate(
                input=combined_pcm_data,
                cache={},
                language="auto",
                use_itn=True,
                batch_size_s=60,
            )
            text = rich_transcription_postprocess(result[0]["text"])
            logger.bind(tag=TAG).debug(
                f"语音识别耗时: {time.time() - start_time:.3f}s | 结果: {text}"
            )

            return text

        except OSError as e:
            retry_count += 1
            if retry_count >= MAX_RETRIES:
                logger.bind(tag=TAG).error(
                    f"语音识别失败（已重试{retry_count}次）: {e}", exc_info=True
                )
                return ""
            logger.bind(tag=TAG).warning(
                f"语音识别失败，正在重试（{retry_count}/{MAX_RETRIES}）: {e}"
            )
            time.sleep(RETRY_DELAY)

        except Exception as e:
            logger.bind(tag=TAG).error(f"语音识别失败: {e}", exc_info=True)
            return ""

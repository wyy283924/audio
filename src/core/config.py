import os
from functools import lru_cache

import yaml
from fastapi import Depends

default_config_file = "config.yaml"


def get_project_dir():
    """获取项目根目录"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/"


@lru_cache(maxsize=1)
def load_config():
    config_path = get_project_dir() + "data/." + default_config_file
    print(config_path)
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            "找不到data/.config.yaml文件，请按教程确认该配置文件是否存在"
        )
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
    return config


@lru_cache(maxsize=1)
def get_asr_config(config: dict = Depends(load_config)):
    return config.get("FunASR")


@lru_cache(maxsize=1)
def get_llm_config(config: dict = Depends(load_config)):
    return config.get("ChatGLMLLM")


@lru_cache(maxsize=1)
def get_tts_config(config: dict = Depends(load_config)):
    return config.get("EdgeTTS")

# VoiceQA API Server
VoiceQA API Server 是一个专注于语音问答（Voice Q&A）核心功能的高性能 REST API 服务，支持独立部署。本项目由 xiaozhi 项目演进而来，在保留核心能力的同时，剥离了原有的 UI 界面与复杂逻辑，致力于提供稳定、低延迟的文本与语音问答接口。

## 🎯 适用场景
适用于快速集成语音对话能力的多种应用场景，包括但不限于：

+ 智能客服系统

+ 语音助手应用

+ AI 教学辅导（Tutor）

+ 内容交互型应用

仅需简单调用 API，即可为您的产品注入强大的语音交互功能。

## 📦 部署指南
我们提供两种部署方式，请根据实际需求选择：

+ [Docker部署](./部署指南.md#源码部署)

+ [源码部署](./部署指南.md#Docker部署)

## ❓ 常见问题
1. 出现“TTS 任务出错 文件不存在”错误？ 📁
建议检查是否已通过 conda 正确安装 libopus 和 ffmpeg 库。若未安装，请执行以下命令：

```bash
conda install conda-forge::libopus
conda install conda-forge::ffmpeg
```
2. TTS 合成频繁失败或超时？ ⏰
若遇到此问题，请优先检查是否启用了网络代理。若正在使用，建议关闭代理后重试。

## ⚙️ 配置说明
| 模块名称      | 配置         |
| ------------- | ------------ |
| ASR(语音识别) | FunASR(本地) |
| LLM(大模型)   | ChatGLMLLM   |
| TTS(语音合成) | EdgeTTS      |
## 接口文档
+ [/api/v1/response/](./接口文档.md)

## 🧪 测试工具
| 工具名称         | 位置                   | 使用方法            | 功能说明                                             |
| ---------------- | ---------------------- | ------------------- | ---------------------------------------------------- |
| 音频交互测试工具 | audio->static->demo.py | 执行 python demo.py | 测试音频播放和接收功能，验证Python端音频处理是否正常 |
## ✨ 功能清单
| 功能模块 | 描述                                 |
| -------- | ------------------------------------ |
| 语音交互 | 支持ASR（语音识别）、TTS（语音合成） |
| 智能对话 | 支持LLM（大语言模型），实现智能对话  |对话
## 📁 项目结构
```text
src/                            # 主应用目录
├── main.py                     # FastAPI 应用入口
├── core/                       # 核心配置与工具
│   ├── __init__.py
│   ├── config.py               # 应用配置
│   └── logger.py               # 日志配置
├── api/
│   └── v1/
│       ├── endpoints/          # API 端点实现
│       │   ├── asr.py          # ASR 接口
│       │   ├── llm.py          # LLM 接口
│       │   └── response.py     # 响应接口
│       └── routers.py          # 路由聚合
├── models/
│   └── SenseVoiceSmall/        # ASR 模型目录
├── services/                   # 服务实现
│   ├── asr_service.py          # ASR 服务
│   ├── llm_service.py          # LLM 服务
│   └── tts_service.py          # TTS 服务
└── utils/                      # 工具库
    ├── util.py
    └── opus_encoder_utils.py   # Opus 编码工具
static/                         # 静态文件目录
└── demo.py                     # Gradio 测试工具
```
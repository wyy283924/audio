# 阶段1：构建依赖
FROM python:3.10-slim AS builder

WORKDIR /code

# 安装构建依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 安装Python依赖
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 阶段2：最终运行时镜像
FROM python:3.10-slim

# 安装运行时系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends libopus0 ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


WORKDIR /code/app
COPY ./src .

# 优化运行参数
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--no-access-log"]
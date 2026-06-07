# 2048 RL 训练实验平台 — 容器镜像
# 基于 arm64 兼容的官方 Python 3.10 slim 镜像（适配 Apple M2）。
# 注意：容器内 PyTorch 使用 CPU（MPS 仅在宿主 macOS 可用，容器内不可用）。

FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 先装依赖以利用构建缓存
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# 拷贝项目代码
COPY pyproject.toml ./
COPY src ./src
COPY configs ./configs
COPY tests ./tests

# 容器内无 MPS/CUDA：configs 中 device=auto 会自动解析为 cpu。
# 默认入口：跑 quick 训练验证管线
CMD ["python", "-m", "src.train.train", "--config", "configs/quick.yaml"]

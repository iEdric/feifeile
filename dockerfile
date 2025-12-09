# 第一阶段：构建环境
FROM python:3.10-slim as builder

# 设置工作目录
WORKDIR /app

# 设置构建参数和镜像源
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONPYCACHEPREFIX=/tmp/pycache

# 安装编译依赖并清理缓存（单层减少镜像大小）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# 先单独复制依赖文件，利用Docker缓存层
COPY requirements.txt .

# 安装用户级依赖
RUN pip install --user --no-warn-script-location -r requirements.txt

# 第二阶段：运行时环境
FROM python:3.10-slim

# 设置基础环境变量
ENV TZ=Asia/Shanghai \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPYCACHEPREFIX=/tmp/pycache \
    PATH=/home/appuser/.local/bin:$PATH \
    # 设置临时目录避免Gradio错误
    TMPDIR=/tmp \
    TEMP=/tmp \
    TMP=/tmp

# 安装最小化运行时依赖并清理
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /var/lib/apt/lists/*

# 创建应用目录和临时目录
RUN mkdir -p /app /app/tmp /tmp /var/tmp /usr/tmp && \
    # 创建非root用户
    useradd --create-home --shell /bin/bash appuser && \
    # 设置目录权限
    chown -R appuser:appuser /app && \
    chown -R appuser:appuser /tmp && \
    chown -R appuser:appuser /var/tmp && \
    chown -R appuser:appuser /usr/tmp

WORKDIR /app

# 从构建阶段复制依赖
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# 复制应用代码（使用.dockerignore过滤不需要的文件）
COPY --chown=appuser:appuser . .

# 健康检查（确保应用已启动并监听端口）
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7171/ || exit 1

# 切换到非root用户
USER appuser

# 暴露端口
EXPOSE 7171

# 使用exec形式启动应用
ENTRYPOINT ["python", "app.py"]
# app/Dockerfile
FROM python:3.10

RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
# 复制代码到镜像仓库
COPY . /app

# 指定工作目录
WORKDIR /app

RUN pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com



EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "webui.py", "--server.port=8501", "--server.address=0.0.0.0"]
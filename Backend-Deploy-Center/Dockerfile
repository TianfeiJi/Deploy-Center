# 使用 Python 3.9 作为基础镜像
FROM python:3.9-slim

# 设置时区
RUN apt-get update && \
    apt-get install -y tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get clean

# 设置工作目录为 /app/src
WORKDIR /app/src

# 将项目的依赖文件复制到容器内
COPY requirements.txt /app/

# 安装依赖
RUN pip install --no-cache-dir -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 将项目文件复制到容器内
COPY . /app/

# 暴露 FastAPI 默认端口 1333
EXPOSE 1333

# 启动 FastAPI 应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1333"]
# 使用 Python 3.9 作为基础镜像
FROM python:3.9-slim

# 设置容器的时区为上海，确保日志时间与中国本地时间一致
ENV TZ=Asia/Shanghai

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
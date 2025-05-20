# Backend - Deploy Agent

部署代理服务（Deploy Agent），基于 FastAPI 实现，负责在业务服务器上完成具体的部署任务，如执行docker build命令、docker run命令等等操作。该服务由部署中心（Deploy Center）统一调度，支持多语言项目的部署调度（如 Java、Python、前端等）。

## 项目结构
```bash
Backend-Deploy-Agent/
├── Dockerfile
├── data
├── example
│   ├── README.md
│   ├── data_example
│   └── template_example
│       ├── dockercommand
│       └── dockerfile
├── requirements.txt
├── src
│   ├── config
│   ├── deployers
│   ├── main.py
│   ├── manager
│   ├── middleware
│   ├── models
│   │   ├── common
│   │   ├── dto
│   │   ├── entity
│   │   ├── enum
│   │   └── vo
│   ├── routes
│   └── utils
└── template
    ├── dockercommand
    └── dockerfile
```

## 快速启动

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
python src/main.py
```

### 或使用 Uvicorn 启动（推荐）
```bash
uvicorn src.main:app --host 0.0.0.0 --port 2333 --reload
```

## Docker 构建与运行
请确保您已经安装了 Docker 环境。

### 第一步：准备项目目录
在部署服务器上创建项目目录结构（可根据实际情况调整路径）：

```bash
mkdir -p /data/docker/infrastructure/deploy-agent
cd /data/docker/infrastructure/deploy-agent
```

将项目中的以下两个文件夹上传至上述目录：
- 将 data/ 文件夹上传至 /data/docker/infrastructure/deploy-agent/data
- 将 src/ 文件夹上传至 /data/docker/infrastructure/deploy-agent/src

期望的目录结构如下所示：

```
/data/docker/infrastructure/deploy-agent
├── data
├── template
├── Dockerfile
├── requirements.txt
└── src
```

请确保 Dockerfile 和 requirements.txt 文件位于项目根目录中（即与 data 和 src 同级）。

### 第二步：构建 Docker 镜像

在项目根目录下执行以下命令构建镜像：

```bash
docker build -t deploy-agent:v1.0 .
```

构建成功后，可以通过 docker images 查看镜像是否创建成功。

### 第三步：运行 Docker 容器
运行容器时，请根据自身部署环境修改挂载路径（-v 参数）。以下为默认示例：

```bash
docker run -d \
  -p 2333:2333 \
  --name deploy-agent \
  -v /data/docker/infrastructure/deploy-agent/data:/app/data \
  -v /data/docker/infrastructure/deploy-agent/logs:/app/logs \
  -v /data/docker/projects/java:/app/projects/java \
  -v /data/docker/projects/webs:/app/projects/webs \
  deploy-agent:v1.0
```

> 注意：上述挂载路径仅供参考。**您应根据实际服务器目录结构设置容器卷挂载路径。**

### 容器卷示例挂载说明

1. **数据与日志目录挂载**

   为实现Deploy Agent自身数据持久化和日志可追踪：

   - `-v /data/docker/infrastructure/deploy-agent/data:/app/data`：挂载项目运行数据目录。
   - `-v /data/docker/infrastructure/deploy-agent/logs:/app/logs`：挂载日志输出目录。

2. **部署项目目录挂载**

   用于容器访问和部署实际的业务项目源代码或构建产物：

   - `-v /data/docker/projects/java:/app/projects/java`：映射Java项目路径。
   - `-v /data/docker/projects/webs:/app/projects/webs`：映射前端项目路径。

>  **注意：上述挂载路径仅供参考，请根据实际部署环境合理配置容器卷挂载路径，否则系统可能无法访问关键数据目录或项目源文件，导致部署任务失败。**
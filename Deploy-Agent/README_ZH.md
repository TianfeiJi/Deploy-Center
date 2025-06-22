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

## 🚀 快速开始

```bash
pip install -r requirements.txt
python src/main.py
```

或使用 Uvicorn：

```bash
uvicorn src.main:app --host 0.0.0.0 --port 2333 --reload
```

## 🐳 使用 Docker 部署

请确保您已经安装了 Docker 环境。

## 方式一：使用官方镜像

**1. 拉取镜像**
```bash
docker pull tianfeiji/deploy-agent:v1.0
```

**2. 运行**
```bash
docker run -d \
  -p 2333:2333 \
  --name deploy-agent \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker \
  -v /data/docker/infrastructure/deploy-agent/template:/app/template \
  -v /data/docker/infrastructure/deploy-agent/data:/app/data \
  -v /data/docker/infrastructure/deploy-agent/logs:/app/logs \
  -v /data/docker/projects/java:/app/projects/java \
  -v /data/docker/projects/webs:/app/projects/webs \
  tianfeiji/deploy-agent:latest
```

> **挂载说明：**  
> - `/var/run/docker.sock`：**必须挂载**，容器访问宿主机 Docker 守护进程的关键通道，否则无法执行容器相关操作。
> - `/usr/bin/docker`: **必须挂载**，将宿主机 Docker CLI 映射进容器，Agent 内部依赖该命令执行部署流程。
> - `/app/template`：Agent 模板目录
> - `/app/data`：Agent 数据目录
> - `/app/logs`：Agent 日志输出目录
> - `/app/projects/java`：你的Java项目部署路径
> - `/app/projects/webs`：你的前端项目部署路径


## 方式二：自行构建镜像

**1. 准备项目目录**
```bash
mkdir -p /data/docker/infrastructure/deploy-agent
cd /data/docker/infrastructure/deploy-agent
```

**2. 拷贝项目源码至该目录**

期望目录结构如下：

```
/data/docker/infrastructure/deploy-agent
├── data
├── template
├── Dockerfile
├── requirements.txt
└── src
```

**3. 构建镜像**
```bash
docker build -t deploy-agent:v1.0 .
```

**4. 运行容器**
```bash
docker run -d \
  -p 2333:2333 \
  --name deploy-agent \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker \
  -v /data/docker/infrastructure/deploy-agent/template:/app/template \
  -v /data/docker/infrastructure/deploy-agent/data:/app/data \
  -v /data/docker/infrastructure/deploy-agent/logs:/app/logs \
  -v /data/docker/projects/java:/app/projects/java \
  -v /data/docker/projects/webs:/app/projects/webs \
  deploy-agent:v1.0
```

**挂载说明：**
> - `/var/run/docker.sock`：**必须挂载**，容器访问宿主机 Docker 守护进程的关键通道，否则无法执行容器相关操作。
> - `/usr/bin/docker`: **必须挂载**，将宿主机 Docker CLI 映射进容器，Agent 内部依赖该命令执行部署流程。
> - `/app/template`：Agent 模板目录
> - `/app/data`：Agent 数据目录
> - `/app/logs`：Agent 日志输出目录
> - `/app/projects/java`：你的Java项目部署路径
> - `/app/projects/webs`：你的前端项目部署路径

> 请根据实际部署环境合理调整宿主路径，避免路径错误导致部署失败。

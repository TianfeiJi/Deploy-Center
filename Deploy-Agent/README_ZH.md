# Deploy Agent

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

请确保您已安装 Docker。

---

## 方式一：使用官方镜像部署

**1. 拉取镜像**
```bash
docker pull tianfeiji/deploy-agent:latest
```

**2. 运行容器**
```bash
docker run -d \
  -p 2333:2333 \
  --name deploy-agent \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker \
  -v /data/docker/infrastructure/deploy-agent/template:/app/template \
  -v /data/docker/infrastructure/deploy-agent/data:/app/data \
  -v /data/docker/infrastructure/deploy-agent/logs:/app/logs \
  -v /data/docker/projects:/app/projects \
  tianfeiji/deploy-agent:latest
```

---

### 容器券挂载路径说明

| 宿主路径 | 容器路径 | 说明 |
|----------|-----------|------|
| `/var/run/docker.sock` | `/var/run/docker.sock` | **必须挂载**。容器访问宿主机 Docker 守护进程的关键通道，否则无法执行容器相关操作。 |
| `/usr/bin/docker` | `/usr/bin/docker` | **必须挂载**。将宿主机 Docker CLI 映射进容器，Agent 内部依赖该命令执行部署流程。 |
| `/data/docker/infrastructure/deploy-agent/template` | `/app/template` | Agent 模板目录，存放部署模版文件（如 Dockerfile、启动脚本等）。 |
| `/data/docker/infrastructure/deploy-agent/data` | `/app/data` | Agent 数据目录，记录部署配置、状态缓存、项目元数据等。 |
| `/data/docker/infrastructure/deploy-agent/logs` | `/app/logs` | Agent 日志目录，建议挂载到宿主机以便持久保存日志内容。 |
| `/data/docker/projects` | `/app/projects` | 项目部署路径挂载点。容器内部统一使用 `/app/projects/{类型}/{项目名}` 访问部署产物。该路径仅为示例，你可以根据实际情况进行调整。 |

> `/data/docker/infrastructure/deploy-agent` 是你部署 deploy-agent 的宿主机目录，**即源码所在位置**。只需确保其子目录正确挂载到容器 `/app` 内部对应路径即可。

### 项目目录结构示例

```
# 宿主机目录结构示例
/data/docker/projects/
├── java/
├── webs/
├── python/
└── ...
```

```
# 容器内对应路径
/app/projects/java/...
/app/projects/webs/...
/app/projects/python/...
```

> 上述路径仅为示例，你可以自由组织宿主机目录结构，通过 `-v` 参数挂载到 `/app/projects` 即可，无需完全一致。
 
---

## 方式二：自行构建镜像部署

**1. 准备项目目录**
```bash
mkdir -p /data/docker/infrastructure/deploy-agent
cd /data/docker/infrastructure/deploy-agent
```

**2. 将项目源码拷贝或 clone 到该目录**

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
docker build -t deploy-agent:latest .
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
  -v /data/docker/projects:/app/projects \
  deploy-agent:latest
```

> 容器券挂载路径说明请参考上文
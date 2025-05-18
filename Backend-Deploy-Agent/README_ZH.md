# Backend - Deploy Agent

部署代理服务（Deploy Agent），基于 FastAPI 实现，负责在业务服务器上完成具体的部署任务，如执行docker build命令、docker run命令等等操作。该服务由部署中心（Deploy Center）统一调度，支持多语言项目的部署调度（如 Java、Python、前端等）。

## 项目结构
```bash
Backend-Deploy-Agent/
├── Dockerfile                     # 构建部署代理镜像
├── README.md                      # 本说明文件
├── logs/                          # 运行日志目录（建议挂载）
├── requirements.txt               # Python 依赖列表
└── src/                           # 主程序目录
    ├── config/                    # 日志与基础配置
    │   └── log_config.py
    ├── data/                      # 系统运行数据
    │   ├── cached_data.json
    │   ├── deploy_history.json
    │   ├── project_data.json
    │   └── user.json
    ├── deployers/                 # 不同类型项目的部署实现类
    │   ├── java_project_deployer.py
    │   ├── python_project_deploy.py
    │   └── web_project_deploy.py
    ├── main.py                    # FastAPI 启动入口
    ├── manager/                   # 核心数据管理器
    │   ├── project_data_manager.py
    │   └── user_manager.py
    ├── middleware/                # 中间件（如权限验证）
    │   └── verify_token_middleware.py
    ├── models/                    # 数据模型
    │   ├── dto/
    │   │   ├── add_java_project_request_dto.py
    │   │   ├── add_web_project_request_dto.py
    │   │   └── user_login_request_dto.py
    │   └── entity/
    │       ├── http_result.py
    │       ├── java_project.py
    │       ├── log.py
    │       ├── user.py
    │       └── web_project.py
    ├── routes/                    # 接口路由
    │   ├── auth_routes.py
    │   ├── docker_routes.py
    │   ├── log_routes.py
    │   ├── project_routes.py
    │   └── server_routes.py
    ├── security/                  # 安全机制（Token 验证等）
    │   └── verify_token.py
    └── utils/                     # 工具类
        └── jwt_util.py
```bash

## 快速启动

# 安装依赖
```bash
pip install -r requirements.txt
```

# 启动服务
```bash
python src/main.py
```

# 或使用 Uvicorn 启动（推荐）
```bash
uvicorn src.main:app --host 0.0.0.0 --port 2333 --reload
```

## Docker 构建与运行

构建镜像：

```bash
docker build -t deploy-agent:v1.0 .
```

运行容器（请务必根据自身部署环境调整挂载路径）：

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
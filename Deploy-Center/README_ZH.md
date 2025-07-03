# Backend - Deploy Center

部署中心后端服务，负责接收前端请求，处理认证、配置管理、用户信息、部署目标维护等操作，协调部署代理（Deploy Agent）完成具体部署行为。

## 项目结构

```bash
Backend-Deploy-Center/
├── Dockerfile                     # 构建部署中心后端镜像
├── README.md                      # 本说明文件
├── data/                          # 系统运行数据存储
│   ├── agent_data.json
│   ├── system_config_data.json
│   └── user_data.json
├── example/data_example/          # 示例数据
│   ├── agent_data.json
│   ├── system_config_data.json
│   └── user_data.json
├── requirements.txt               # 依赖列表
└── src/                           # 主程序目录
    ├── config/                    # 配置项
    │   └── log_config.py
    ├── main.py                    # FastAPI 启动入口
    ├── manager/                   # 各类核心数据管理器
    │   ├── agent_data_manager.py
    │   ├── cached_data_manager.py
    │   ├── system_config_data_manager.py
    │   └── user_data_manager.py
    ├── middleware/                # 中间件
    │   └── verify_token_middleware.py
    ├── models/                    # 数据模型
    │   ├── common/
    │   │   ├── cached_data.py
    │   │   └── http_result.py
    │   ├── dto/
    │   │   └── user_login_request_dto.py
    │   └── entity/
    │       ├── agent.py
    │       ├── system_config.py
    │       └── user.py
    ├── routes/                    # 接口路由
    │   ├── agent_routes.py
    │   ├── auth_routes.py
    │   ├── system_config_routes.py
    │   ├── two_factor_routes.py
    │   └── user_routes.py
    ├── security/                  # 安全机制
    │   ├── two_factor_auth.py
    │   └── verify_token.py
    └── utils/                     # 工具类
        ├── decorators/
        │   └── skip_auth.py
        └── jwt_util.py
```

## 🚀 快速开始

```bash
pip install -r requirements.txt
python src/main.py
```

或使用 Uvicorn：

```bash
uvicorn src.main:app --host 0.0.0.0 --port 1333 --reload
```

## 🐳 使用 Docker 部署

请确保您已经安装了 Docker 环境。

## 方式一：使用官方镜像

无需构建镜像，直接拉取并运行：

**1. 拉取镜像**
```bash
docker pull tianfeiji/deploy-center:latest
```

**2. 运行**
```bash
docker run -d \
  -p 1333:1333 \
  --name deploy-center \
  -v /data/docker/infrastructure/deploy-center/data:/app/data \
  -v /data/docker/infrastructure/deploy-center/logs:/app/logs \
  tianfeiji/deploy-center:latest
```

> **挂载说明:** 为了实现数据持久化和日志记录，建议挂载以下目录（宿主路径可根据实际情况调整）：
> - /app/data：部署中心的数据目录
> - /app/logs：日志输出目录

例如，宿主机路径可设为 /data/docker/infrastructure/deploy-center/，也可以自定义为其他位置，只要确保具备读写权限即可。。

## 方式二：自行构建镜像

**1. 准备项目目录**
在部署服务器上创建项目目录结构（可根据实际情况调整路径）：

```bash
mkdir -p /data/docker/infrastructure/deploy-center
cd /data/docker/infrastructure/deploy-center
```

**2. 拷贝项目源码至该目录**

期望的目录结构如下所示：

```
/data/docker/infrastructure/deploy-center
├── data
├── Dockerfile
├── requirements.txt
└── src
```

> `Dockerfile` 与 `requirements.txt` 应位于根目录，与 `data`、`src` 同级。

**3. 构建 Docker 镜像**

```bash
docker build -t deploy-center:latest .
```

> 或自行指定版本号

**4：运行 Docker 容器**
```bash
docker run -d \
  -p 1333:1333 \
  --name deploy-center \
  -v /data/docker/infrastructure/deploy-center/data:/app/data \
  -v /data/docker/infrastructure/deploy-center/logs:/app/logs \
  deploy-center:v1.0
```

> **挂载说明:** 为了实现数据持久化和日志记录，建议挂载以下目录（宿主路径可根据实际情况调整）：
> - /app/data：部署中心的数据目录
> - /app/logs：日志输出目录
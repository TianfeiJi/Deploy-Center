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

## 快速启动

```bash
pip install -r requirements.txt
python src/main.py
```

或使用 Uvicorn：

```bash
uvicorn src.main:app --host 0.0.0.0 --port 1333 --reload
```

## Docker 构建与运行

构建镜像：

```bash
docker build -t deploy-center:v1.0 .
```

运行容器（请务必根据自身部署环境调整挂载路径）：

```bash
docker run -d \
  -p 1333:1333 \
  --name deploy-center \
  -v /data/docker/infrastructure/deploy-center/data:/app/data \
  -v /data/docker/infrastructure/deploy-center/logs:/app/logs \
  deploy-center:v1.0
```

### 容器卷挂载说明

**数据与日志目录挂载**

   为实现Deploy Center自身数据持久化和日志可追踪：

   - `-v /data/docker/infrastructure/deploy-center/data:/app/data`：挂载项目运行数据目录。
   - `-v /data/docker/infrastructure/deploy-center/logs:/app/logs`：挂载日志输出目录。

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

## 本地快速启动

```bash
pip install -r requirements.txt
python src/main.py
```

或使用 Uvicorn：

```bash
uvicorn src.main:app --host 0.0.0.0 --port 1333 --reload
```

## Docker 构建与运行
请确保您已经安装了 Docker 环境。

### 第一步：准备项目目录
在部署服务器上创建项目目录结构（可根据实际情况调整路径）：

```bash
mkdir -p /data/docker/infrastructure/deploy-center
cd /data/docker/infrastructure/deploy-center
```

将项目中的以下两个文件夹上传至上述目录：
- 将 data/ 文件夹上传至 /data/docker/infrastructure/deploy-center/data
- 将 src/ 文件夹上传至 /data/docker/infrastructure/deploy-center/src

期望的目录结构如下所示：

```
/data/docker/infrastructure/deploy-center
├── data
├── Dockerfile
├── requirements.txt
└── src
```

请确保 Dockerfile 和 requirements.txt 文件位于项目根目录中（即与 data 和 src 同级）。

### 第二步：构建 Docker 镜像

在项目根目录下执行以下命令构建镜像：

```bash
docker build -t deploy-center:v1.0 .
```

构建成功后，可以通过 docker images 查看镜像是否创建成功。

### 第三步：运行 Docker 容器
运行容器时，请根据自身部署环境修改挂载路径（-v 参数）。以下为默认示例：

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

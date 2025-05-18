# Backend - Deploy Center

The Deploy Center backend service handles frontend requests, managing authentication, configuration, user information, and deployment targets. It coordinates with Deploy Agents to execute actual deployment tasks.

## Project Structure

```bash
Backend-Deploy-Center/
├── Dockerfile                     # Build image for the Deploy Center backend
├── README.md                      # This documentation file
├── data/                          # Runtime data storage
│   ├── agent_data.json
│   ├── system_config_data.json
│   └── user_data.json
├── example/data_example/          # Example data
│   ├── agent_data.json
│   ├── system_config_data.json
│   └── user_data.json
├── requirements.txt               # Python dependencies list
└── src/                           # Main source directory
    ├── config/                    # Configuration files
    │   └── log_config.py
    ├── main.py                    # FastAPI application entry point
    ├── manager/                   # Core data managers
    │   ├── agent_data_manager.py
    │   ├── cached_data_manager.py
    │   ├── system_config_data_manager.py
    │   └── user_data_manager.py
    ├── middleware/                # Middleware components
    │   └── verify_token_middleware.py
    ├── models/                    # Data models
    │   ├── common/
    │   │   ├── cached_data.py
    │   │   └── http_result.py
    │   ├── dto/
    │   │   └── user_login_request_dto.py
    │   └── entity/
    │       ├── agent.py
    │       ├── system_config.py
    │       └── user.py
    ├── routes/                    # API route definitions
    │   ├── agent_routes.py
    │   ├── auth_routes.py
    │   ├── system_config_routes.py
    │   ├── two_factor_routes.py
    │   └── user_routes.py
    ├── security/                  # Security mechanisms
    │   ├── two_factor_auth.py
    │   └── verify_token.py
    └── utils/                     # Utility classes
        ├── decorators/
        │   └── skip_auth.py
        └── jwt_util.py
```

## Quick Start

```bash
pip install -r requirements.txt
python src/main.py
```

Or run with Uvicorn:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 1333 --reload
```

## Docker Build and Run

Build image:

```bash
docker build -t deploy-center:v1.0 .
```

Run container (please adjust volume mounts according to your deployment environment):

```bash
docker run -d \
  -p 1333:1333 \
  --name deploy-center \
  -v /data/docker/infrastructure/deploy-center/data:/app/data \
  -v /data/docker/infrastructure/deploy-center/logs:/app/logs \
  deploy-center:v1.0
```

### Container Volume Mount Explanation

**Data and Log Directory Mounting**

To ensure persistence of Deploy Center’s own data and traceability of logs:

- `-v /data/docker/infrastructure/deploy-center/data:/app/data` : Mount runtime data directory.
- `-v /data/docker/infrastructure/deploy-center/logs:/app/logs` : Mount log output directory.
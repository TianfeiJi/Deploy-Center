# Deploy Center

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

## 🚀 Quick Start

Run locally (development mode)
```bash
pip install -r requirements.txt
python src/main.py
```

Or use Uvicorn:

```bash
uvicorn src.main:app --host 0.0.0.0 --port 1333 --reload
```

## 🐳 Docker Deployment

Please make sure you have Docker installed.

## Method 1: Use Official Image

No need to build the image, just pull and run:

**1. Pull the image**
```bash
docker pull tianfeiji/deploy-center:v1.0
```

> Or tag it with your own version.

**2. Run the container**
```bash
docker run -d \
  -p 1333:1333 \
  --name deploy-center \
  -v /data/docker/infrastructure/deploy-center/data:/app/data \
  -v /data/docker/infrastructure/deploy-center/logs:/app/logs \
  tianfeiji/deploy-center:v1.0
```

> **Volume Mounting Note:**  
> To enable data persistence and log tracking, it is recommended to mount the following directories (host paths can be adjusted as needed):  
> - `/app/data`: data directory inside the container  
> - `/app/logs`: logs directory inside the container  
>
> For example, the host path can be `/data/docker/infrastructure/deploy-center/`, or customized to any location with proper read/write permissions.

## Method 2: Build Image Locally

**1. Prepare project directory**  
Create the project directory structure on the deployment server (adjust paths as needed):

```bash
mkdir -p /data/docker/infrastructure/deploy-center
cd /data/docker/infrastructure/deploy-center
```

**2. Copy the project source code to this directory**

Expected directory structure:

```
/data/docker/infrastructure/deploy-center
├── data
├── Dockerfile
├── requirements.txt
└── src
```

> `Dockerfile` and `requirements.txt` should be in the root directory alongside `data` and `src`.

**3. Build the Docker image**

```bash
docker build -t deploy-center:v1.0 .
```

**4. Run the Docker container**

```bash
docker run -d \
  -p 1333:1333 \
  --name deploy-center \
  -v /data/docker/infrastructure/deploy-center/data:/app/data \
  -v /data/docker/infrastructure/deploy-center/logs:/app/logs \
  deploy-center:v1.0
```

> **Volume Mounting Note:**  
> To enable data persistence and log tracking, it is recommended to mount the following directories (host paths can be adjusted as needed):  
> - `/app/data`: data directory inside the container  
> - `/app/logs`: logs directory inside the container  
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

## Docker Build and Run Guide

Please make sure Docker is installed on your system.

### Step 1: Prepare Project Directory

Create the project directory structure on your deployment server (adjust the path as needed):

```bash
mkdir -p /data/docker/infrastructure/deploy-center
cd /data/docker/infrastructure/deploy-center
```

Upload the following folders from your project to the directory above:
- Upload the `data/` folder to `/data/docker/infrastructure/deploy-center/data`
- Upload the `src/` folder to `/data/docker/infrastructure/deploy-center/src`

Expected directory structure:

```
/data/docker/infrastructure/deploy-center
├── data
├── Dockerfile
├── requirements.txt
└── src
```

Make sure that the `Dockerfile` and `requirements.txt` are located in the root of the project (i.e., at the same level as `data` and `src`).

### Step 2: Build Docker Image

Run the following command in the project root directory to build the Docker image:

```bash
docker build -t deploy-center:v1.0 .
```

Once the build is complete, you can verify the image with:

```bash
docker images
```

### Step 3: Run Docker Container

When running the container, adjust the mounted paths (`-v` options) according to your environment. Example:

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
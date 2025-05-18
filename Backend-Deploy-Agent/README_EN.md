# Backend - Deploy Agent

The Deploy Agent is a backend service built with FastAPI. It is responsible for executing deployment tasks on business servers, such as running `docker build`, `docker run`, and other commands. The service is orchestrated by the Deploy Center and supports multi-language project deployments (e.g., Java, Python, frontend).

## Project Structure
```bash
Backend-Deploy-Agent/
├── Dockerfile                     # Build the deploy agent image
├── README.md                      # This documentation file
├── logs/                          # Runtime log directory (recommended to mount)
├── requirements.txt               # Python dependencies list
└── src/                           # Main source directory
    ├── config/                    # Logging and base configuration
    │   └── log_config.py
    ├── data/                      # Runtime data
    │   ├── cached_data.json
    │   ├── deploy_history.json
    │   ├── project_data.json
    │   └── user.json
    ├── deployers/                 # Deployment logic for different project types
    │   ├── java_project_deployer.py
    │   ├── python_project_deploy.py
    │   └── web_project_deploy.py
    ├── main.py                    # FastAPI entry point
    ├── manager/                   # Core data managers
    │   ├── project_data_manager.py
    │   └── user_manager.py
    ├── middleware/                # Middleware (e.g., auth verification)
    │   └── verify_token_middleware.py
    ├── models/                    # Data models
    │   ├── dto/
    │   │   ├── add_java_project_request_dto.py
    │   │   ├── add_web_project_request_dto.py
    │   │   └── user_login_request_dto.py
    │   └── entity/
    │       ├── http_result.py
    │       ├── java_project.py
    │       ├── log.py
    │       ├── project_base.py
    │       └── user.py
    ├── routes/                    # API routes
    │   ├── deploy_route.py
    │   └── user_route.py
    └── services/                  # Business logic services
        ├── deploy_service.py
        └── user_service.py
```

## Key Features

- **Multi-language Support**: Supports deployment of Java, Python, and frontend projects.
- **Token-Based Authentication**: Secured using token verification middleware.
- **Centralized Orchestration**: Designed to be controlled and scheduled by a central Deploy Center.
- **Modular Architecture**: Clear separation of concerns between config, data, deployers, routes, and services.
- **Logging and History Tracking**: Logs and deployment history are persistently recorded for auditing and troubleshooting.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python src/main.py
```

> Note: For production deployment, it's recommended to use a proper ASGI server such as Uvicorn or Gunicorn.
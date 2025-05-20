# Backend - Deploy Agent

The Deploy Agent is a backend service built with FastAPI. It is responsible for executing concrete deployment tasks on business servers, such as running `docker build`, `docker run`, and other related commands. This service is centrally orchestrated by the Deploy Center and supports deployment scheduling for multi-language projects (e.g., Java, Python, frontend, etc.).

## Project Structure
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

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Start the Service
```bash
python src/main.py
```

### Or Start with Uvicorn (Recommended)
```bash
uvicorn src.main:app --host 0.0.0.0 --port 2333 --reload
```

## Docker Build and Run Guide

Please make sure Docker is installed on your system.

### Step 1: Prepare Project Directory

Create the project directory structure on your deployment server (adjust the path as needed):

```bash
mkdir -p /data/docker/infrastructure/deploy-agent
cd /data/docker/infrastructure/deploy-agent
```

Upload the following folders from your project to the directory above:
- Upload the `data/` folder to `/data/docker/infrastructure/deploy-agent/data`
- Upload the `src/` folder to `/data/docker/infrastructure/deploy-agent/src`

Expected directory structure:

```
/data/docker/infrastructure/deploy-agent
├── data
├── Dockerfile
├── requirements.txt
└── src
```

Make sure that the `Dockerfile` and `requirements.txt` files are located in the root of the project (i.e., at the same level as `data` and `src`).

### Step 2: Build Docker Image

Run the following command in the project root directory to build the Docker image:

```bash
docker build -t deploy-agent:v1.0 .
```

Once the build is complete, you can verify the image with:

```bash
docker images
```

### Step 3: Run Docker Container

When running the container, adjust the mounted paths (`-v` options) according to your environment. Example:

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

> Note: The volume mount paths above are for reference only. **You should adjust them based on the actual directory structure of your server.**
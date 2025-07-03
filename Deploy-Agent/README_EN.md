# Deploy Agent

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

## 🚀 Quick Start

```bash
pip install -r requirements.txt
python src/main.py
```

Or use Uvicorn (recommended):

```bash
uvicorn src.main:app --host 0.0.0.0 --port 2333 --reload
```

## 🐳 Deploy with Docker

Make sure Docker is installed on your system.

## Method 1: Use the Official Image

**1. Pull the Image**
```bash
docker pull tianfeiji/deploy-agent:vlatest
```

**2. Run the Container**
```bash
docker run -d \
  -p 2333:2333 \
  --name deploy-agent \
  -v /data/docker/infrastructure/deploy-agent/template:/app/template \
  -v /data/docker/infrastructure/deploy-agent/data:/app/data \
  -v /data/docker/infrastructure/deploy-agent/logs:/app/logs \
  -v /data/docker/projects/java:/app/projects/java \
  -v /data/docker/projects/webs:/app/projects/webs \
  tianfeiji/deploy-agent:latest
```

**Mount Notes:**  
> - `/var/run/docker.sock`: **Must be mounted**. This is the critical socket for the container to access the Docker daemon on the host. Without this, container-related operations will fail.
> - `/usr/bin/docker`: **Must be mounted**. Maps the Docker CLI from the host into the container. The Agent depends on this command to execute deployment processes.
> - `/app/template`: Agent template directory.
> - `/app/data`: Agent data directory.
> - `/app/logs`: Agent log output directory.
> - `/app/projects/java`: Your Java project deployment path.
> - `/app/projects/webs`: Your frontend project deployment path.

> Be sure to adjust the host paths according to your actual environment to avoid issues caused by incorrect path settings.

## Method 2: Build the Image Manually

**1. Prepare the Project Directory**
```bash
mkdir -p /data/docker/infrastructure/deploy-agent
cd /data/docker/infrastructure/deploy-agent
```

**2. Copy the Project Source Code into This Directory**

Expected directory structure:

```
/data/docker/infrastructure/deploy-agent
├── data
├── template
├── Dockerfile
├── requirements.txt
└── src
```

**3. Build the Docker Image**
```bash
docker build -t deploy-agent:latest .
```

> Or tag it with your own version.

**4. Run the Container**
```bash
docker run -d \
  -p 2333:2333 \
  --name deploy-agent \
  -v /data/docker/infrastructure/deploy-agent/template:/app/template \
  -v /data/docker/infrastructure/deploy-agent/data:/app/data \
  -v /data/docker/infrastructure/deploy-agent/logs:/app/logs \
  -v /data/docker/projects/java:/app/projects/java \
  -v /data/docker/projects/webs:/app/projects/webs \
  deploy-agent:latest
```

**Mount Notes:**  
> - `/var/run/docker.sock`: **Must be mounted**. This is the critical socket for the container to access the Docker daemon on the host. Without this, container-related operations will fail.
> - `/usr/bin/docker`: **Must be mounted**. Maps the Docker CLI from the host into the container. The Agent depends on this command to execute deployment processes.
> - `/app/template`: Agent template directory.
> - `/app/data`: Agent data directory.
> - `/app/logs`: Agent log output directory.
> - `/app/projects/java`: Your Java project deployment path.
> - `/app/projects/webs`: Your frontend project deployment path.

> Be sure to adjust the host paths according to your actual environment to avoid issues caused by incorrect path settings.
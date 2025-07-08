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

### Mount Overview

| Host Path | Container Path | Description |
|-----------|----------------|-------------|
| `/var/run/docker.sock` | `/var/run/docker.sock` | **Required**. This socket allows the container to communicate with the Docker daemon on the host. Without it, container-related operations cannot be executed. |
| `/usr/bin/docker` | `/usr/bin/docker` | **Required**. Maps the host's Docker CLI into the container. The Agent relies on this to perform deployment operations. |
| `/data/docker/infrastructure/deploy-agent/template` | `/app/template` | The Agent's template directory, which contains deployment templates (e.g., Dockerfiles, startup scripts, etc.). |
| `/data/docker/infrastructure/deploy-agent/data` | `/app/data` | The Agent's data directory, used to store deployment configurations, state cache, project metadata, etc. |
| `/data/docker/infrastructure/deploy-agent/logs` | `/app/logs` | The Agent's log directory. It is recommended to mount this to the host for persistent logging. |
| `/data/docker/projects` | `/app/projects` | The mount point for your project deployment directory. This is just an example path—you may adjust it to fit your own directory structure. Inside the container, all projects are accessed under `/app/projects/{type}/{project_name}`. |

> `/data/docker/infrastructure/deploy-agent` refers to the directory on the host where you deploy the `deploy-agent`—**typically the location where you cloned or extracted the agent source code**. This directory contains subdirectories such as `template`, `data`, and `logs`. You are free to place this directory wherever you prefer, as long as these subdirectories are correctly mounted to `/app/template`, `/app/data`, and `/app/logs` inside the container.

**Example Project Directory Structure**

You may organize your deployment projects by type, for example:

```
# Example structure on the host
/data/docker/projects/
├── java/      # Java project artifacts
├── webs/      # Frontend project artifacts
├── python/    # Python project artifacts
└── ...        # Other types (customizable)
```

The corresponding paths inside the container would be:

```
/app/projects/java/...
/app/projects/webs/...
/app/projects/python/...
```

> The above paths are for demonstration purposes only. You can organize your host directories however you like, as long as you mount them into `/app/projects` using the `-v` flag. There's no need to follow the example path exactly.

---

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
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker \
  -v /data/docker/infrastructure/deploy-agent/template:/app/template \
  -v /data/docker/infrastructure/deploy-agent/data:/app/data \
  -v /data/docker/infrastructure/deploy-agent/logs:/app/logs \
  -v /data/docker/projects:/app/projects \
  deploy-agent:latest
```

> For container mount path explanations, please refer to the section above.
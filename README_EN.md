# Deploy Center

<p align="center">
  <a href="https://github.com/TianfeiJi/Deploy-Center">
    <img alt="License" src="https://img.shields.io/github/license/TianfeiJi/Deploy-Center.svg">
  </a>
  <a href="https://github.com/TianfeiJi/Deploy-Center/stargazers">
    <img alt="Stars" src="https://img.shields.io/github/stars/TianfeiJi/Deploy-Center.svg">
  </a>
  <a href="https://github.com/TianfeiJi/Deploy-Center/issues">
    <img alt="Issues" src="https://img.shields.io/github/issues/TianfeiJi/Deploy-Center.svg">
  </a>
  <a href="https://github.com/TianfeiJi/Deploy-Center/commits/main">
    <img alt="Last commit" src="https://img.shields.io/github/last-commit/TianfeiJi/Deploy-Center.svg">
  </a>
</p>

<p align="center">
  <a href="./README.md">中文</a> | <a href="./README_EN.md">English</a>
</p>

## Introduction

**`Deploy Center`** is a lightweight project deployment management tool that supports front-end projects as well as various projects that can be deployed via Docker containers (such as Java, Python, etc.). By automating and standardizing operations, **Deploy Center** significantly improves operational efficiency, reduces manual intervention costs, and ensures the efficiency and stability of project deployments.

> This project adheres to a “lightweight-first, modular-evolution” philosophy, focusing on building a controllable and extensible deployment platform designed to both deepen the understanding of cloud-native architecture and address practical deployment scenarios.

## Documentation Navigation
- [Deploy-Center-UI](./Deploy-Center-UI/README.md): Frontend of the Deploy Center, provides UI for task configuration and operations
- [Deploy-Center](./Deploy-Center/README_EN.md): Backend of the Deploy Center, responsible for scheduling and distributing deployment tasks
- [Deploy-Agent](./Deploy-Agent/README_EN.md): Deployment Agent backend, responsible for executing deployment tasks
> For more documentation, please refer to the [A-docs/](./A-docs/) directory.

## Live Demo
**Demo URL:** [http://jitianfei.com/deploy-center-ui](http://jitianfei.com/deploy-center-ui)  
**Username:** admin  
**Password:** admin  

## Features

- **Lightweight and High-Performance**: A single **Deploy Agent** consumes less than 150MB of memory at runtime, ensuring minimal resource usage on business servers while providing high-performance deployment capabilities. It is suitable for deployment scenarios of all sizes, ranging from small and medium-sized enterprises to large enterprises.

- **Flexible Upload and Deployment**: **Deploy Center** offers powerful file management capabilities, allowing users to upload locally packaged project files to the system and complete deployment operations through **Deploy Agent**. The system supports version management of uploaded files, enabling users to conveniently select the desired version for deployment. The entire process is automated, ensuring efficient and controllable deployment.

- **Automated Cloud Build and Deployment**: **Deploy Center** supports automatic code pulls from code repositories (such as GitHub, GitLab) and performs local builds and deployments on business servers using Maven. The entire process is automatically completed by **Deploy Agent** without manual intervention, achieving full automation from code to deployment, significantly simplifying the deployment process and improving development efficiency.

- **Detailed Deployment Logs**: It provides a comprehensive deployment log recording function, allowing users to view detailed information of each deployment process in real-time, including deployment status, executed commands, output information, etc. Logs support multi-dimensional queries by time, project, and more, facilitating quick problem identification and ensuring the transparency and traceability of the deployment process.

- **Complete Deployment History**: It records detailed information of each deployment, including deployment time, version, operator, and results. Users can quickly trace the deployment process through deployment history, compare deployments of different versions, and support one-click rollback to historical versions, ensuring the traceability and stability of deployments.

- **Real-Time Monitoring and Alerts**: It provides real-time monitoring capabilities, supporting real-time viewing and analysis of project runtime status. The system can configure alert rules to notify operations personnel of potential issues in a timely manner, ensuring the stable operation of projects.

## Planned Features
- **Automated Cloud-Based Build and Deployment**: Deploy Center is planned to support automated code fetching from repositories such as GitHub and GitLab. The system will allow code to be pulled, locally built using Maven, and deployed on business servers—all fully automated by the Deploy Agent. This upcoming feature aims to streamline the entire process from code to deployment, significantly improving efficiency and reducing the need for manual intervention.

## Architecture

### Architecture Design Description

#### Deploy Center
- **Deploy Center UI**: Provides a graphical interface for users to send deployment instructions and manage tasks.
- **Deploy Center**: Receives requests from the front end, schedules deployment instructions, and sends commands to each **Deploy Agent**. It is also responsible for security checks across the system.

**Deploy Center** is deployed on a middle server that supports external network access and can receive requests from the external network. It is the management and control center of the entire deployment system, responsible for receiving user instructions, scheduling deployment tasks, and communicating with each **Deploy Agent**.

#### Deploy Agents
- **Project Deployment API**: Deployed on business servers, it exposes APIs to complete project deployment tasks. These APIs cannot be called directly and must be invoked through **Deploy Center** to ensure system security.
- **Business Service Management**: Each business server can deploy multiple types of business services, managed and maintained by **Deploy Agent**.

#### Additional Notes

**Deploy Agent** is a backend service deployed on business servers, responsible for executing specific deployment tasks. It receives instructions from **Deploy Center** to complete service deployment, updates, and management. **Deploy Agent** does not necessarily support external network access and is typically deployed within an internal network, communicating with **Deploy Center** for management.

### Architecture Diagram

```mermaid
flowchart TD
    subgraph Management_Server[Management Server]
        FE[Deploy Center UI]
        BE[Deploy Center]
        FE --> BE
    end

    subgraph Business_Server1[Business Server 1]
        DA1[Deploy Agent 1]
    end

    subgraph Business_Server2[Business Server 2]
        DA2[Deploy Agent 2]
    end

    subgraph Business_Server3[Business Server 3]
        DA3[Deploy Agent 3]
    end

    User[User] --> FE
    BE --> DA1
    BE --> DA2
    BE --> DA3

    DA1 --> Service1[Business Service 1]
    DA1 --> Service2[Business Service 2]

    DA2 --> Service3[Business Service 3]
    DA2 --> Service4[Business Service 4]

    DA3 --> Service5[Business Service 5]
    DA3 --> Service6[Business Service 6]
```

## 🛠️ Technology Stack

The project consists of two main modules: the Deployment Management Platform (Deploy Center) and the Deployment Execution Agent (Deploy Agent).

### 📦 Deploy Center

> Management side, providing Web UI, deployment task dispatching, and log viewing features.

#### Frontend
- **Framework**: Quasar Framework 2 (v2.16.0)
- **Languages**: Vue 3 + TypeScript
- **UI Components**: Quasar UI, Element Plus
- **Build Tool**: Vite
- **State Management**: Pinia

#### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Containerization**: Docker

### ⚙️ Deploy Agent

> Deployment agent running on business servers, responsible for executing actual project deployments.

#### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Containerization**: Docker

---

## 👨‍💻 About the Auhor

> This project is designed and maintained by **[Tianfei Ji](https://github.com/TianfeiJi)**.

Feel free to follow, connect, or share your feedback.
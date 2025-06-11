## Q1: What exactly does the Deploy Agent act as an agent for?

The **Deploy Agent** is a lightweight deployment executor that bridges the **Deploy Center** and target environments.

For front-end projects, it simply unpacks pre-built files to a designated path for immediate access.

For containerized applications—such as Java, Python, or other Docker-compatible services—it automates the entire deployment process by executing `docker build` and `docker run` commands in the background.

In addition to Docker command delegation, the **Deploy Agent** is technically also capable of executing arbitrary shell commands. However, this capability has not been implemented, as it falls outside the current system's intended scope. See Q2 for further explanation.

## Q2: Why doesn't Deploy Center integrate more operations-related functionality?

While technically feasible, it's not part of the system's core responsibility. **Deploy Center** was designed with a clear focus on **deployment**, not as a general-purpose operations platform.

That said, some lightweight operations capabilities closely tied to deployment are already supported, such as:

1. Real-time collection of server performance metrics (CPU, memory, disk usage, etc.);
2. Status monitoring of deployed services based on Docker commands.

These features improve deployment observability and control, but remain strictly within the deployment domain.

From an architectural standpoint, although the **Deploy Agent** is technically capable of executing arbitrary shell commands, its scope is intentionally constrained to ensure system security, auditability, and maintainability.

If more powerful and flexible operations capabilities are needed, it is fully feasible to design an independent **Ops Center** based on the architectural principles of **Deploy Center** and **Deploy Agent** — enabling a modular, clearly scoped system composition.

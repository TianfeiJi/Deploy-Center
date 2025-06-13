from typing import Optional
from pydantic import BaseModel

class AddPythonProjectRequestDto(BaseModel):
    project_code: str
    project_name: str
    project_group: str
    git_repository: Optional[str]
    docker_image_name: str
    docker_image_tag: str
    external_port: int
    internal_port: int
    network: str
    python_version: str
    host_project_path: str
    container_project_path: str
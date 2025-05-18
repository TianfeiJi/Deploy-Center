from pydantic import BaseModel
from typing import Optional

class UpdateJavaProjectRequestDto(BaseModel):
    id: str
    project_code: Optional[str] = None
    project_name: Optional[str] = None
    project_group: Optional[str] = None
    docker_image_name: Optional[str] = None
    docker_image_tag: Optional[str] = None
    external_port: Optional[int] = None
    internal_port: Optional[int] = None
    network: Optional[str] = None
    host_project_path: Optional[str] = None
    container_project_path: Optional[str] = None
    git_repository: Optional[str] = None
    status: Optional[str] = None
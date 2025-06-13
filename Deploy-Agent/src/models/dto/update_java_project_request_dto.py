from pydantic import BaseModel
from typing import Optional

class UpdateJavaProjectRequestDto(BaseModel):
    id: str
    project_code: Optional[str]
    project_name: Optional[str]
    project_group: Optional[str]
    docker_image_name: Optional[str]
    docker_image_tag: Optional[str]
    external_port: Optional[int]
    internal_port: Optional[int]
    network: Optional[str]
    host_project_path: Optional[str]
    container_project_path: Optional[str]
    git_repository: Optional[str]
    status: Optional[str]
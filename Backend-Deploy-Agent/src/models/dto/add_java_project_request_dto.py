from pydantic import BaseModel

class AddJavaProjectRequestDto(BaseModel):
    project_code: str
    project_name: str
    project_group: str
    git_repository: str
    docker_image_name: str
    docker_image_tag: str
    external_port: int
    internal_port: int
    network: str
    jdk_version: int
    host_project_path: str
    container_project_path: str
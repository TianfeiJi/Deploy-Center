from typing import Optional
from pydantic import BaseModel

class AddWebProjectRequestDto(BaseModel):
    project_code: str
    project_name: str
    project_group: str
    git_repository: str
    host_project_path: str
    container_project_path: str
    access_url: Optional[str]
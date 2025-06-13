from pydantic import BaseModel
from typing import Optional

class UpdateWebProjectRequestDto(BaseModel):
    id: str
    project_code: Optional[str]
    project_name: Optional[str]
    project_group: Optional[str]
    host_project_path: Optional[str]
    container_project_path: Optional[str]
    git_repository: Optional[str]
    access_url: Optional[str]
    status: Optional[str]
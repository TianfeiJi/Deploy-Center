from pydantic import BaseModel
from typing import Optional

class UpdateWebProjectRequestDto(BaseModel):
    id: str
    project_code: Optional[str] = None
    project_name: Optional[str] = None
    project_group: Optional[str] = None
    host_project_path: Optional[str] = None
    container_project_path: Optional[str] = None
    git_repository: Optional[str] = None
    access_url: Optional[str] = None
    status: Optional[str] = None
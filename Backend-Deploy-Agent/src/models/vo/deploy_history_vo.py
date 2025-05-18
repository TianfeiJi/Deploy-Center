from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeployHistoryVo(BaseModel):
    id: str
    project_id: str
    project_code: str
    project_name: str
    status: str
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None 
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
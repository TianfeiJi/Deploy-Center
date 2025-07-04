from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeployHistory(BaseModel):
    id: str
    project_id: str
    status: str
    failed_reason: Optional[str] = None
    operator_name: Optional[str] = None # 操作者名称（来自Center透传）
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
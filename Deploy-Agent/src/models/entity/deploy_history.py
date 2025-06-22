from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeployHistory(BaseModel):
    id: str
    project_id: str
    status: str
    failed_reason: Optional[str]
    operator_name: Optional[str]  # 操作者名称（来自Center透传）
    created_at: Optional[datetime]
    created_by: Optional[int]
    updated_at: Optional[datetime]
    updated_by: Optional[int]
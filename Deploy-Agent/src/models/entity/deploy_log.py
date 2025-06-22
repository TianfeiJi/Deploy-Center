from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeployLog(BaseModel):
    filename: str
    filesize: int
    line_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
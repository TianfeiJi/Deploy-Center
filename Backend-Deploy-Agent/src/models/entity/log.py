from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Log(BaseModel):
    filename: str
    filesize: int
    line_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
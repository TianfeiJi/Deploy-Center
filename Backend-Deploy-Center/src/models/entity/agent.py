from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Agent(BaseModel):
    id: int
    name: str
    ip: str
    port: int
    service_url: Optional[str] = None
    os: str
    type: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
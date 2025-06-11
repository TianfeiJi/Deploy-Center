from pydantic import BaseModel
from typing import Optional

class UpdateAgentRequestDto(BaseModel):
    id: str
    name: Optional[str]
    ip: Optional[str]
    port: Optional[int]
    service_url: Optional[str]
    os: Optional[str]
    type: Optional[str]
    status: Optional[str]
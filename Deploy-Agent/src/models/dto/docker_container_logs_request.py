from typing import Optional
from pydantic import BaseModel, Field


class DockerContainerLogsRequest(BaseModel):
    container_name: str = Field(..., description="容器名称")
    tail: int = Field(50, ge=1, le=2000, description="返回最后多少行日志，默认50")
    timestamps: bool = Field(False, description="是否附带时间戳")
    since: Optional[str] = Field(None, description="起始时间，如 10m、1h、2026-04-03T10:00:00")
    until: Optional[str] = Field(None, description="结束时间，如 10m、1h、2026-04-03T11:00:00")
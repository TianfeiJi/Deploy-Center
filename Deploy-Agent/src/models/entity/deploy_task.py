from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class DeployTask(BaseModel):
    id: str
    project_id: str

    task_name: Optional[str] = None

    status: Literal[
        "PENDING",
        "RUNNING",
        "SUCCESS",
        "FAILED",
        "CANCELLED"
    ] = "PENDING"

    trigger_type: Literal["MANUAL", "SCHEDULED"] = "MANUAL"
    deploy_mechanism: Literal["UPLOAD", "CLOUD_BUILD"] = "UPLOAD"

    upload_file_name: Optional[str] = None
    upload_file_path: Optional[str] = None

    build_image_name: Optional[str] = None
    build_image_tag: Optional[str] = None
    container_name: Optional[str] = None
    
    dockerfile_content: Optional[str] = None
    dockercommand_content: Optional[str] = None

    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    failed_reason: Optional[str] = None

    operator_name: Optional[str] = None  # 操作者名称（来自 Center 透传）
    operator_id: Optional[int] = None    # 操作者 ID（如有）

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
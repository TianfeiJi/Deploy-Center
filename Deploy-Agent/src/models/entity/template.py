from pydantic import BaseModel
from datetime import datetime

class Template(BaseModel):
    id: str
    template_name: str
    relative_path: str  # 相对于 template 文件夹的路径
    template_type: str 
    project_type: str
    description: str = ""
    created_at: datetime
    updated_at: datetime

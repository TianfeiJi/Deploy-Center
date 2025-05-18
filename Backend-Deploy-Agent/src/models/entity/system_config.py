from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime

class SystemConfig(BaseModel):
    id: int
    config_name: str
    config_key: str
    config_value: Union[str, bool, int, float, None]  # 支持多种类型
    config_remark: str
    config_group: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
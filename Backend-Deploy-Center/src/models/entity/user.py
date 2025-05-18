from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    id: int
    username: str
    password: str
    nickname: str
    email: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    permissions: Optional[List[str]]
    two_factor_secret: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
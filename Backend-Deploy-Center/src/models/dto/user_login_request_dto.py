from pydantic import BaseModel
from typing import Optional


class UserLoginRequestDto(BaseModel):
    identifier: str
    credential: str
    two_factor_code: Optional[str]

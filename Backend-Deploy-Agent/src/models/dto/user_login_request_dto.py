from pydantic import BaseModel

class UserLoginRequestDto(BaseModel):
    identifier: str
    credential: str

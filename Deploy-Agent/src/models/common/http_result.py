from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class HttpResult(BaseModel, Generic[T]):
    """
    Unified API response wrapper.

    Attributes:
        code: Business status code
        msg: Optional message
        data: Response payload
    """
    code: int = Field(..., description="Business status code")
    msg: Optional[str] = Field(default=None, description="Message")
    data: Optional[T] = Field(default=None, description="Payload")

    @classmethod
    def ok(cls, data: T = None, msg: Optional[str] = None):
        return cls(code=200, msg=msg, data=data)

    @classmethod
    def fail(cls, code: int = 500, msg: str = "failed", data: T = None):
        return cls(code=code, msg=msg, data=data)
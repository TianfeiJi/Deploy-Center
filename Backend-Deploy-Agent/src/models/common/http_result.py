from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

# 定义一个类型变量 T，用于泛型
T = TypeVar("T")

class HttpResult(BaseModel, Generic[T]):
    code: Optional[int] = Field(None, description="HTTP 状态码")
    status: str = Field(..., description="状态描述")
    msg: Optional[str] = Field(None, description="消息内容") 
    data: Optional[T] = Field(None, description="返回数据")
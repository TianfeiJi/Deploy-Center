from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, Union
from fastapi.responses import JSONResponse

T = TypeVar("T")


class HttpResult(BaseModel, Generic[T]):
    """
    统一响应数据结构，用于接口返回
    """
    code: int = Field(200, description="状态码，通常使用 HTTP 状态码或业务码")
    status: str = Field("success", description="状态字符串，例如 success / failed")
    msg: Optional[str] = Field(None, description="提示信息")
    data: Optional[T] = Field(None, description="返回的数据内容")

    @classmethod
    def success(cls, data: Optional[T] = None, msg: Optional[str] = None) -> "HttpResult[T]":
        return cls(code=200, status="success", msg=msg, data=data)

    @classmethod
    def failed(cls, msg: str = "请求失败", code: int = 400, data: Optional[T] = None) -> "HttpResult[T]":
        return cls(code=code, status="failed", msg=msg, data=data)

    def json_response(self, http_code: Optional[int] = None) -> JSONResponse:
        """
        将当前结果对象转换为 FastAPI 可返回的 JSONResponse。
        如果不指定 http_code，默认使用 self.code。
        """
        return JSONResponse(
            status_code=http_code or self.code,
            content=self.model_dump()
        )
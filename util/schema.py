
from typing import Any
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    success: bool = Field(True, description="是否成功")
    message: str = Field("成功！", description="訊息")
    data: Any = Field(None, description="回傳資料")


class ErrorResponse(BaseModel):
    success: bool = Field(False, description="是否成功")
    message: str = Field("失敗！", description="訊息")
    data: Any = Field(None, description="錯誤訊息或詳情")
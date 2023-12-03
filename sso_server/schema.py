from typing import Any, Optional
from pydantic import BaseModel, Field

from sso_server.definition import TokenEndpointAuthMethod

# * request

# GetHome

class GetHomeQuery(BaseModel):
    next: Optional[str] = None

# PostHome

class PostHomeBody(BaseModel):
    username: str = Field(description="Username", min_length=1)
    password: str = Field(description="Password", min_length=1)

# PostCreateClient

class PostCreateClientBody(BaseModel):
    client_name: str = Field("", examples=["My Client"])
    client_uri: str = Field("", examples=["http://localhost:3000"])
    grant_type: list[str] = Field([], examples=[["authorization_code", "password"]])
    redirect_uri: list[str] = Field([], examples=["http://localhost:3000/callback"])
    response_type: list[str] = Field([], examples=["code"])
    scope: str = Field("", examples=["profile"])
    token_endpoint_auth_method: TokenEndpointAuthMethod = (
        TokenEndpointAuthMethod.CLIENT_SECRET_BASIC
    )

class PostAuthorizeBody(BaseModel):
    username: str
    confirm: bool

class PostIssueTokenBody(BaseModel):
    grant_type: str
    username: str
    password: str
    scope: str

# * response

class SuccessResponse(BaseModel):
    success: bool = Field(True, description="是否成功")
    message: str = Field("成功！", description="訊息")
    data: Any = Field(None, description="回傳資料")

class ErrorResponse(BaseModel):
    success: bool = Field(False, description="是否成功")
    message: str = Field("失敗！", description="訊息")
    data: Any = Field(None, description="錯誤訊息或詳情")
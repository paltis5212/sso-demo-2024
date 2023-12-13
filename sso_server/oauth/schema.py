from typing import Any, Optional
from pydantic import BaseModel, Field

from sso_server.oauth.definition import (
    SCOPES,
    ClientGrantType,
    ClientResponseType,
    TokenEndpointAuthMethod,
)
from util.other import get_enum_value_list
from typing import Literal

# * request


class PostHomeQuery(BaseModel):
    next: Optional[str] = None


class PostHomeForm(BaseModel):
    username: str
    password: str
    next: str


class PostRegisterBody(BaseModel):
    username: str = Field(description="Username", min_length=1)
    password: str = Field(description="Password", min_length=1)


class PostCreateClientBody(BaseModel):
    client_name: str = Field("")
    client_uri: str = Field("")
    grant_types: list[ClientGrantType] = Field(
        [], description=f"可多選: {get_enum_value_list(ClientGrantType)}。"
    )
    redirect_uris: list[str] = Field([])
    response_types: list[ClientResponseType] = Field(
        [], description=f"可多選: {get_enum_value_list(ClientResponseType)}。"
    )
    scopes: str = Field("", description=f"可多選: {SCOPES}。使用空格隔開，例如: 'scope1 scope2'。")
    token_endpoint_auth_method: TokenEndpointAuthMethod = (
        TokenEndpointAuthMethod.CLIENT_SECRET_BASIC
    )


class PostAuthorizeBody(BaseModel):
    confirm: bool


# * response

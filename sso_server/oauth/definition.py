from enum import Enum
import logging


class TokenEndpointAuthMethod(Enum):
    CLIENT_SECRET_BASIC = "client_secret_basic"
    CLIENT_SECRET_POST = "client_secret_post"
    NONE = "none"


class ClientGrantType(Enum):
    AUTHORIZATION_CODE = "authorization_code"
    IMPLICIT = "implicit"
    CLIENT_CREDENTIALS = "client_credentials"
    PASSWORD = "password"


class ClientResponseType(Enum):
    CODE = "code"
    TOKEN = "token"
    # ID_TOKEN = "id_token"


SCOPES = ["profile"]

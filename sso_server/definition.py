from enum import Enum
import logging

class ApiException(Exception):
    """
    Custom API Exception
    """
    pass

class TokenEndpointAuthMethod(Enum):
    CLIENT_SECRET_BASIC = "client_secret_basic"
    CLIENT_SECRET_POST = "client_secret_post"
    NONE = "none"
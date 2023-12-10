from authlib.integrations.flask_client import OAuth
import certifi
from flask import Flask, jsonify, url_for, session
from requests import Response
import json
from flask_openapi3 import OpenAPI
from sso_server.routes import get_authorize
from authlib.integrations.flask_client import token_update

from util.error_handler import set_error_handlers
from .routes import api

app = OpenAPI(__name__)
app.config["SECRET_KEY"] = "secret"
app.register_api(api)
oauth = OAuth(app)
sso = oauth.register(
    name='sso',
    client_id='BHTsEyzOgQagBfSvikIytm9L',
    client_secret='WtOq3S9TDUiynQvAQXh3UlMG8Zp8gaOKKkQ4rc4hyTzQsOKI',
    access_token_url='https://www.svc.deltaww-energy.com:5001/oauth/token',
    access_token_params=None,
    authorize_url='https://www.svc.deltaww-energy.com:5001/oauth/authorize',
    authorize_params=None,
    api_base_url='https://www.svc.deltaww-energy.com:5001/',
    client_kwargs={
        'scope': 'profile',
        'token_endpoint_auth_method': 'client_secret_basic',
        'token_placement': 'header',
    },
    verify=False,
)
app.sso = sso

set_error_handlers(app)

app.run(host="127.0.0.1", port=5002, debug=True, ssl_context=("ca/cert.pem", "ca/key.pem"))
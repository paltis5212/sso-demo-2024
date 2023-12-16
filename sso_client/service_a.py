import logging

from authlib.integrations.flask_client import OAuth
from flask_openapi3 import OpenAPI
from flask_openapi3.openapi import Info
from sso_client.authz import api as authz_api
from sso_client.authz import authz_config
from util.error_handler import set_error_handlers
from util.log import get_file_handler, get_rich_handler

from .models import db
from .routes import api

app = OpenAPI(__name__, info=Info(title="OAuth client A", version="0.0.0"))

app.config.update(
    {
        "SECRET_KEY": "secret",
        "SQLALCHEMY_DATABASE_FILENAME": "service_a.sqlite3",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///../../instance/service_a.sqlite3",
        "SQLALCHEMY_TRACK_MODIFICATIONS": True,
    }
)
app.register_api(api)
app.register_api(authz_api)

db.init_app(app)
# Create tables if they do not exist already
with app.app_context():
    db.create_all()

oauth = OAuth(app)
sso = oauth.register(
    name="sso",
    client_id="BHTsEyzOgQagBfSvikIytm9L",
    client_secret="WtOq3S9TDUiynQvAQXh3UlMG8Zp8gaOKKkQ4rc4hyTzQsOKI",
    access_token_url="https://www.svc.deltaww-energy.com:5001/sso/oauth/token",
    access_token_params=None,
    authorize_url="https://www.svc.deltaww-energy.com:5001/sso/oauth/authorize",
    authorize_params=None,
    api_base_url="https://www.svc.deltaww-energy.com:5001/sso/oauth",
    client_kwargs={
        "scope": "profile",
        "token_endpoint_auth_method": "client_secret_basic",
        "token_placement": "header",
    },
    verify=False,
)
app.sso = sso

# register logger
app.logger.setLevel(logging.INFO)
app.logger.handlers = []
app.logger.addHandler(get_rich_handler())
app.logger.addHandler(get_file_handler("log/service_a.log"))


authz_config(app)
set_error_handlers(app)
app.run(
    host="0.0.0.0", port=5002, debug=True, ssl_context=("ca/cert.pem", "ca/key.pem")
)

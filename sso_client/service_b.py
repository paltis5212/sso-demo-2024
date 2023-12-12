from authlib.integrations.flask_client import OAuth
from flask_openapi3 import OpenAPI
from sso_client.authz import authz_config

from util.error_handler import set_error_handlers
from .routes import api
from .models import db

app = OpenAPI(__name__)
app.config.update({
    "SECRET_KEY": "secret",
    "SQLALCHEMY_DATABASE_FILENAME": "service_b.sqlite3",
    "SQLALCHEMY_DATABASE_URI": "sqlite:///../../instance/service_b.sqlite3",
    "SQLALCHEMY_TRACK_MODIFICATIONS": True
})
app.register_api(api)

db.init_app(app)
# Create tables if they do not exist already
with app.app_context():
    db.create_all()

oauth = OAuth(app)
sso = oauth.register(
    name='sso',
    client_id='ZTmJ7IPeK7GgBefpIqBobhtn',
    client_secret='Hg5MDaqENYeLrOB8fHBr9CEtevn8qyH9tK5BX5jZkVt4MfpV',
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

authz_config(app)
set_error_handlers(app)

app.run(host="0.0.0.0", port=5003, debug=True, ssl_context=("ca/cert.pem", "ca/key.pem"))
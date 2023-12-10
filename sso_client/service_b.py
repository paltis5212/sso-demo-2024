from authlib.integrations.flask_client import OAuth
from flask_openapi3 import OpenAPI

from util.error_handler import set_error_handlers
from .routes import api

app = OpenAPI(__name__)
app.config["SECRET_KEY"] = "secret"
app.register_api(api)

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

set_error_handlers(app)

app.run(host="0.0.0.0", port=5003, debug=True, ssl_context=("ca/cert.pem", "ca/key.pem"))
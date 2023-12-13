import logging

from flask_openapi3 import OpenAPI

from util.error_handler import set_error_handlers
from util.log import get_file_handler

from .request_checker import set_app_request_check_rules
from .saml.setup_saml import setup_saml
from .oauth.setup_oauth import setup_oauth_app


def create_app(config=None):
    app = OpenAPI(
        __name__,
        static_folder="./static/assets",
        static_url_path="/dsebd/sso/static/assets",
    )

    setup_oauth_app(app=app, config=config)
    setup_app(app)
    # set_app_request_check_rules(app)
    setup_saml(app)
    return app


def setup_app(app: OpenAPI):

    # register logger
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(get_file_handler("log/sso_server.log"))

    # register error handler

    set_error_handlers(app)

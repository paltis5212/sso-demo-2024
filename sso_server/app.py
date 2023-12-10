import json
import logging
import os
import traceback

from authlib.common.errors import AuthlibBaseError
from authlib.integrations.flask_oauth2.errors import _HTTPException
from flask import Response
from flask_openapi3 import OpenAPI

from util.error_handler import set_error_handlers
from util.log import get_file_handler

from .models import db
from .oauth2 import config_oauth
from .request_checker import set_app_request_check_rules
from .routes import api
from .saml.setup_saml import setup_saml


def create_app(config=None):
    app = OpenAPI(
        __name__,
        static_folder="./static/assets",
        static_url_path="/dsebd/sso/static/assets",
    )

    # load default configuration
    app.config.from_object("sso_server.settings")

    # load environment configuration
    if "SSO_SERVER_CONF" in os.environ:
        app.config.from_envvar("SSO_SERVER_CONF")

    # load app specified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif isinstance(config, str) and config.endswith(".py"):
            app.config.from_pyfile(config)

    setup_app(app)
    # set_app_request_check_rules(app)
    setup_saml(app)
    return app


def setup_app(app: OpenAPI):
    db.init_app(app)
    # Create tables if they do not exist already
    with app.app_context():
        db.create_all()
    config_oauth(app)
    app.register_api(api)

    # register logger
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(get_file_handler("log/sso_server.log"))

    # register error handler

    set_error_handlers(app)

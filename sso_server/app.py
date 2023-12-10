import json
import os
import traceback

from authlib.common.errors import AuthlibBaseError
from authlib.integrations.flask_oauth2.errors import _HTTPException
from flask_openapi3 import OpenAPI

from sso_server.definition import ApiException
from sso_server.schema import ErrorResponse
from util.log import get_file_handler

from .models import db
from .oauth2 import config_oauth
from .routes import api
from .request_checker import set_app_request_check_rules


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
    set_app_request_check_rules(app)
    return app


def setup_app(app: OpenAPI):
    db.init_app(app)
    # Create tables if they do not exist already
    with app.app_context():
        db.create_all()
    config_oauth(app)
    app.register_api(api)

    # register logger
    app.logger.addHandler(get_file_handler("log/sso_server.log"))

    # register error handler
    @app.errorhandler(ApiException)
    def handle_api_exception(error: ApiException):
        app.logger.warn(traceback.format_exc())
        if len(error.args) > 0 and isinstance(response := error.args[0], ErrorResponse):
            return response.model_dump(mode="json")
        return ErrorResponse(data=str(error)).model_dump(mode="json")

    @app.errorhandler(AuthlibBaseError)
    def handle_authlib_base_error(error: AuthlibBaseError):
        app.logger.warn(traceback.format_exc())
        return ErrorResponse(data=error.error).model_dump(mode="json")

    @app.errorhandler(_HTTPException)
    def handle_authlib_http_exception(error: _HTTPException):
        app.logger.warn(traceback.format_exc())
        try:
            return json.loads(error.get_body())
        except Exception:
            return str(error.get_body())

    @app.errorhandler(Exception)
    def handle_exception(error: Exception):
        app.logger.error(traceback.format_exc())
        return ErrorResponse(data="Something went wrong.").model_dump(mode="json")

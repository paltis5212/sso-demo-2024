import traceback
from flask_openapi3 import OpenAPI

from util.schema import ErrorResponse
from flask import Response, request
import json
import traceback

from authlib.common.errors import AuthlibBaseError
from authlib.integrations.flask_oauth2.errors import _HTTPException
from flask_openapi3 import OpenAPI

class ApiException(Exception):
    """
    Custom API Exception
    """
    pass

def set_error_handlers(app: OpenAPI):
    @app.after_request
    def after_request(response: Response):
        form: bytes = request.get_data()
        req_json: dict = request.get_json(silent=True)
        res_json: dict = response.get_json(silent=True)
        app.logger.info(f"Request Form: {form}")
        app.logger.info(f"Request JSON: {req_json}")
        app.logger.info(f"Response: {res_json}")
        # if res_json and res_json.get("error"):
        #     app.logger.warn(traceback.format_stack())
        return response

    @app.errorhandler(ApiException)
    def handle_api_exception(error: ApiException):
        app.logger.warn(traceback.format_exc())
        
        if len(error.args) > 0:
            if isinstance(response := error.args[0], ErrorResponse):
                return response.model_dump(mode="json"), 400
            else:
                return error.args[0], 400
        return str(error), 400

    @app.errorhandler(AuthlibBaseError)
    def handle_authlib_base_error(error: AuthlibBaseError):
        app.logger.warn(traceback.format_exc())
        return ErrorResponse(data=error.error).model_dump(mode="json"), 400

    @app.errorhandler(_HTTPException)
    def handle_authlib_http_exception(error: _HTTPException):
        app.logger.warn(traceback.format_exc())
        try:
            return json.loads(error.get_body()), 400
        except Exception:
            return str(error.get_body()), 400

    @app.errorhandler(Exception)
    def handle_exception(error: Exception):
        app.logger.error(traceback.format_exc())
        return ErrorResponse(data="Something went wrong.").model_dump(mode="json"), 500

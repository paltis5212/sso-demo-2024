from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, abort, jsonify, request
from rich import print

from util.error_handler import ApiException
from util.schema import ErrorResponse


class SimpleMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        print("Middleware: Before request")
        new_environ = environ.copy()

        new_environ = self.ec_01(environ)
        new_environ = self.ec_05(new_environ)

        query_string = new_environ["QUERY_STRING"]
        if query_string != "":
            new_environ["REQUEST_URI"] = f"{new_environ['REQUEST_URI']}?{query_string}"
        print(new_environ)

        # Call the actual Flask application
        response = self.app(new_environ, start_response)
        # Do something after the request is handled

        return response

    def ec_01(self, environ):
        """
        If this HTTP method is GET and the path is /dsebd/sso/resource,
        please modify the path to /dsebd/sso/static/assets
        """
        new_environ = environ.copy()
        orig_path = str(environ["PATH_INFO"])
        method = environ["REQUEST_METHOD"]
        if method == "GET":
            if orig_path.startswith("/dsebd/sso/resource/"):
                new_path = (
                    f"/dsebd/sso/static/assets{orig_path[len('/dsebd/sso/resource') :]}"
                )
                new_environ["PATH_INFO"] = new_path
                query_string = environ["QUERY_STRING"]
                if query_string != "":
                    new_environ["REQUEST_URI"] = f"{new_path}?{query_string}"
                # new_environ["RAW_URI"] = str(new_environ["REQUEST_URI"])
        # print(new_environ)
        return new_environ

    def ec_05(self, environ):
        """If this HTTP method is POST/PUT,
        please remove all the URL query strings.
        """

        # TODO:
        # only handle the request not in auth
        new_environ = environ.copy()
        method = environ["REQUEST_METHOD"]
        if method in ["PUT", "POST"]:
            new_environ["REQUEST_URI"] = ""
        return new_environ


def set_app_request_check_rules(app: Flask):
    app.wsgi_app = SimpleMiddleware(app.wsgi_app)
    pass

    # EC02
    @app.get("/shopback/me")
    def shopback_me():
        """
        If this HTTP method is GET and the path is /shopback/me, please check if sbcookie Cookie exists in the header. Throw an error if not existing. [In Rule 2, maybe we are not only checking the sbcookie existing but also checking the value if it is correct or not.]
        """
        sbcookie = request.cookies.get("sbcookie")
        if sbcookie is None:
            raise ApiException(ErrorResponse(message="Invalid cookie."))

    # # EC03
    # @app.before_request
    # def check_referer():
    #     # Only check for GET requests
    #     if request.method == "GET":
    #         # Get the referer header from the request
    #         referer = request.headers.get("Referer")

    #         # Check if the referer is None or does not belong to the specified domain
    #         if not referer or "www.svc.deltaww-energy.com" not in referer:
    #             raise ApiException("Invalid Referer")

    # EC04
    @app.after_request
    def modify_headers_for_get_ssoapi(response):
        """
        If this HTTP method is GET and the path is match /dsebd/sso/api/*,
        Please add From in the header and the value is hello@deltaww-energy.com."""
        if request.method == "GET" and request.path.startswith("/dsebd/sso/api/"):
            response.headers["From"] = "hello@deltaww-energy.com"
        return response

    @app.get("/dsebd/sso/api/test", host="www.svc.deltaww-energy.com")
    def test():
        return jsonify({"Hello": "kitty"})

    # # EC07
    # @app.before_request
    # def check_content_type_header():
    #     """
    #     If this HTTP method is POST/PUT, please check if Content-Type exists in the header and the value should be “application/json”. Throw an error if it is invalid.
    #     """
    #     if request.method in ["POST", "PUT"]:
    #         # Check if Content-Type header exists in the request
    #         content_type_header = request.headers.get("Content-Type")

    #         if not content_type_header or content_type_header != "application/json":
    #             abort(
    #                 400,
    #                 'Invalid or missing Content-Type header (should be "application/json")',
    #             )

    # EC06
    # EC08
    # @app.before_request
    # def check_dsebd_agent_header():
    #     """
    #     If this HTTP method is POST/PUT, please check if X-DSEBD-AGENT exists in the header. Throw an error if not existing.
    #     If this HTTP method is DELETE, please check if X-DSEBD-AGENT exists in the header and the value should be “AGENT_1” only. Throw an error if it is invalid. [In Rule 8, maybe we are not only allowing “AGENT_1” to be valid but also “AGENT_2”, or we don’t check the value anymore.]
    #     """
    #     if request.method in ["POST", "PUT"]:
    #         # Check if X-DSEBD-AGENT header exists in the request
    #         agent_header = request.headers.get("X-DSEBD-AGENT")
    #         if not agent_header:
    #             abort(400, "X-DSEBD-AGENT header is missing")

    #     if request.method == "DELETE":
    #         # Check if X-DSEBD-AGENT header exists in the request
    #         agent_header = request.headers.get("X-DSEBD-AGENT")

    #         if not agent_header or agent_header not in ["AGENT_1", "AGENT_2"]:
    #             abort(400, "Invalid or missing X-DSEBD-AGENT header")

    # EC09
    @app.after_request
    def add_timestamp_header(response):
        timestamp = str(int(datetime.timestamp(datetime.now())))
        response.headers["X-DSEBD-TIMESTAMP"] = timestamp
        return response

    # EC10
    # @app.before_request
    # def check_domain():
    #     ALLOWED_DOMAIN = "www.svc.deltaww-energy.com"
    #     hostname = urlparse(request.base_url).hostname
    #     if hostname != ALLOWED_DOMAIN:
    #         return ErrorResponse(message="Invalid domain").model_dump(mode="json"), 403

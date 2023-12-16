from datetime import datetime
from urllib.parse import urlparse

from flask import Flask, Response, abort, jsonify, request, redirect, url_for
from rich import print

from util.exception import BadRequestException
from util.schema import ErrorResponse, SuccessResponse


class SimpleMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ: dict, start_response):
        # print("Middleware: Before request")
        new_environ = environ.copy()

        new_environ = self.ec_01(new_environ)
        new_environ = self.ec_05(new_environ)

        query_string = new_environ["QUERY_STRING"]
        if query_string != "":
            new_environ["REQUEST_URI"] = f"{new_environ['REQUEST_URI']}?{query_string}"
        # print(new_environ)

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

        new_environ = environ.copy()
        method = environ["REQUEST_METHOD"]
        if method in ["PUT", "POST"] and new_environ["PATH_INFO"] == "/dsebd/sso/api/remove_query_string":
            new_environ["QUERY_STRING"] = ""
        return new_environ


def set_app_request_check_rules(app: Flask):
    pass
    app.wsgi_app = SimpleMiddleware(app.wsgi_app)


    # EC02
    @app.get("/shopback/me")
    def shopback_me():
        """
        If this HTTP method is GET and the path is /shopback/me, please check if sbcookie Cookie exists in the header. Throw an error if not existing. [In Rule 2, maybe we are not only checking the sbcookie existing but also checking the value if it is correct or not.]
        """
        sbcookie = request.cookies.get("sbcookie")
        if sbcookie is None:
            raise BadRequestException(message="Invalid cookie.")
        return SuccessResponse(data={"sbcookie": sbcookie}).model_dump(mode="json")

    # EC03
    @app.get("/check_referer")
    def check_referer():
        # Get the referer header from the request
        referer = request.headers.get("Referer")

        # Check if the referer is None or does not belong to the specified domain
        if not referer or "www.svc.deltaww-energy.com" not in referer:
            raise BadRequestException(message="Invalid Referer")
        
        return SuccessResponse().model_dump(mode="json")

    # EC04
    @app.after_request
    def modify_headers_for_get_ssoapi(response: Response):
        """
        If this HTTP method is GET and the path is match /dsebd/sso/api/*,
        Please add From in the header and the value is hello@deltaww-energy.com."""
        if request.method == "GET" and request.path.startswith("/dsebd/sso/api/"):
            response.headers["From"] = "hello@deltaww-energy.com"
        return response

    @app.get("/dsebd/sso/api/test")
    def test():
        return SuccessResponse(data={"A new From header": "hello@deltaww-energy.com"}).model_dump(mode="json")
    
    # EC05
    @app.post("/dsebd/sso/api/remove_query_string")
    def remove_query_string():
        return SuccessResponse(data={"New url is": request.url}).model_dump(mode="json")

    # EC07
    @app.post("/check_content_type")
    def check_content_type_header():
        """
        If this HTTP method is POST/PUT, please check if Content-Type exists in the header and the value should be “application/json”. Throw an error if it is invalid.
        """
        content_type_header = request.headers.get("Content-Type")
        # Check if Content-Type header exists in the request

        if content_type_header != "application/json":
            raise BadRequestException(
                message="Invalid or missing Content-Type header (should be 'application/json')"
            )
        
        return SuccessResponse(data="You have the nice Content-Type header.").model_dump(mode="json")

    # EC06
    # EC08
    @app.before_request
    def check_dsebd_agent_header():
        """
        If this HTTP method is POST/PUT, please check if X-DSEBD-AGENT exists in the header. Throw an error if not existing.
        If this HTTP method is DELETE, please check if X-DSEBD-AGENT exists in the header and the value should be “AGENT_1” only. Throw an error if it is invalid. [In Rule 8, maybe we are not only allowing “AGENT_1” to be valid but also “AGENT_2”, or we don’t check the value anymore.]
        """
        if "/dsebd/sso/api/check_dsebd_agent_header" in request.path:
            if request.method in ["POST", "PUT"]:
                # Check if X-DSEBD-AGENT header exists in the request
                agent_header = request.headers.get("X-DSEBD-AGENT")
                if not agent_header:
                    raise BadRequestException(message="X-DSEBD-AGENT header is missing")

            if request.method == "DELETE":
                # Check if X-DSEBD-AGENT header exists in the request
                agent_header = request.headers.get("X-DSEBD-AGENT")

                if not agent_header or agent_header not in ["AGENT_1", "AGENT_2"]:
                    raise BadRequestException(message="Invalid or missing X-DSEBD-AGENT header")
    
    @app.post("/dsebd/sso/api/check_dsebd_agent_header")
    def post_check_dsebd_agent_header():
        return SuccessResponse(data={"X-DSEBD-AGENT": request.headers.get("X-DSEBD-AGENT")}).model_dump(mode="json")

    @app.delete("/dsebd/sso/api/check_dsebd_agent_header")
    def delete_check_dsebd_agent_header():
        return SuccessResponse(data={"X-DSEBD-AGENT": request.headers.get("X-DSEBD-AGENT")}).model_dump(mode="json")

    # EC09
    @app.after_request
    def add_timestamp_header(response: Response):
        if request.method == "GET" and request.path.startswith("/dsebd/sso/api/check_timestamp"):
            timestamp = str(int(datetime.timestamp(datetime.now())))
            response.headers["X-DSEBD-TIMESTAMP"] = timestamp
        return response
    
    @app.get("/dsebd/sso/api/add_timestamp_header")
    def get_add_timestamp_header():
        return SuccessResponse(data={"Please check X-DSEBD-TIMESTAMP": "in your response header."}).model_dump(mode="json")

    # EC10
    @app.before_request
    def check_domain():
        ALLOWED_DOMAIN = "deltaww-energy.com"
        hostname = urlparse(request.base_url).hostname
        if ALLOWED_DOMAIN not in hostname:
            return ErrorResponse(message="Invalid domain").model_dump(mode="json"), 403

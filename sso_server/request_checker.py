from flask import request, Flask, abort
from datetime import datetime


def set_app_request_check_rules(app: Flask):
    # EC01
    @app.before_request
    def modify_path():
        if request.method == "GET" and request.path.startswith(
                "/dsebd/sso/resource"):
            # Modify the path to /dsebd/sso/static/assets
            new_path = ("/dsebd/sso/static/assets" +
                        request.path[len("/dsebd/sso/resource"):])
            request.path = new_path

    # EC03
    @app.before_request
    def check_referer():
        # Only check for GET requests
        if request.method == "GET":
            # Get the referer header from the request
            referer = request.headers.get("Referer")

            # Check if the referer is None or does not belong to the specified domain
            if not referer or "www.svc.deltaww-energy.com" not in referer:
                abort(403, "Invalid Referer")

    # EC04
    @app.before_request
    def modify_headers():
        if request.method == "GET" and request.path.startswith(
                "/dsebd/sso/api/"):
            request.headers["From"] = "hello@deltaww-energy.com"

    # EC05
    @app.before_request
    def modify_request():
        if request.method in ["POST", "PUT"]:
            # Remove all URL query strings
            request.args = {}

    # EC06
    @app.before_request
    def check_agent_header():
        if request.method in ["POST", "PUT"]:
            # Check if X-DSEBD-AGENT header exists in the request
            if "X-DSEBD-AGENT" not in request.headers:
                abort(400, "X-DSEBD-AGENT header is missing")

    # EC07
    @app.before_request
    def check_content_type_header():
        if request.method in ["POST", "PUT"]:
            # Check if Content-Type header exists in the request
            content_type_header = request.headers.get("Content-Type")

            if not content_type_header or content_type_header != "application/json":
                abort(
                    400,
                    'Invalid or missing Content-Type header (should be "application/json")',
                )

    # EC08
    @app.before_request
    def check_headers():
        if request.method == "DELETE":
            # Check if X-DSEBD-AGENT header exists in the request
            agent_header = request.headers.get("X-DSEBD-AGENT")

            if not agent_header or agent_header != "AGENT_1":
                abort(
                    400,
                    'Invalid or missing X-DSEBD-AGENT header (should be "AGENT_1")'
                )

    # EC09
    @app.before_request
    def add_timestamp_header():
        timestamp = str(int(datetime.timestamp(datetime.now())))
        request.headers["X-DSEBD-TIMESTAMP"] = timestamp

    # EC10
    @app.before_request
    def check_domain():
        ALLOWED_DOMAIN = "www.deltaww-energy.com"
        if request.headers.get("Host") != ALLOWED_DOMAIN:
            abort(403, "Invalid domain")

#!/usr/bin/env python3
import logging
from urllib import response

from flask import Flask, Response, abort, redirect, request, session, url_for
from flask.views import MethodView

from flask_saml2.idp import IdentityProvider

from .tests.idp.base import CERTIFICATE, PRIVATE_KEY, User
from .tests.sp.base import CERTIFICATE as SP_CERTIFICATE

logger = logging.getLogger(__name__)


class ExampleIdentityProvider(IdentityProvider):

    def login_required(self):
        if not self.is_user_logged_in():
            next = url_for("saml_login", next=request.url)

            abort(redirect(next))

    def is_user_logged_in(self):
        return "user" in session and session["user"] in users

    def logout(self):
        del session["user"]

    def get_current_user(self):
        return users[session["user"]]


users = {
    user.username: user for user in [
        User("alex", "alex@example.com"),
        User("jordan", "jordan@example.com"),
    ]
}

idp = ExampleIdentityProvider()


class Login(MethodView):

    def get(self):
        options = "".join(
            f'<option value="{user.username}">{user.email}</option>'
            for user in users.values())
        select = f'<div><label>Select a user: <select name="user">{options}</select></label></div>'

        next_url = request.args.get("next")
        next = f'<input type="hidden" name="next" value="{next_url}">'
        password = f'Password: <input name="password">'

        submit = '<div><input type="submit" value="Login"></div>'

        form = f'<form action="login" method="post">{select}{password}{next}{submit}</form>'
        header = "<title>Login</title><p>Please log in to continue.</p>"

        return header + form

    # def get(self):
    #     next_url = request.args.get("next")
    #     header = """
    #     <!DOCTYPE html>
    #     <html lang="en">
    #     <head>
    #         <meta charset="UTF-8">
    #         <meta name="viewport" content="width=device-width, initial-scale=1.0">
    #         <title>Login Form</title>
    #         <!-- 引入 jQuery -->
    #         <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
    #     </head>
    #     """
    #     form = (
    #         """
    #     <body>
    #         <h2>Login Form</h2>
    #         <form id="loginForm">
    #             <label for="username">Username:</label>
    #             <input type="text" id="username" name="username" required><br>

    #             <label for="password">Password:</label>
    #             <input type="password" id="password" name="password" required><br>

    #             <button type="button" onclick="login()">Login</button>
    #         </form>

    #         <script>
    #             function login() {
    #                 // Get input values
    #                 var username = $('#username').val();
    #                 var password = $('#password').val();

    #                 // Create a JSON object
    #                 var data = {
    #                     username: username,
    #                     password: password,
    #                     """
    #         f"next: {next_url}"
    #         """
    #                 };

    #                 // Send the JSON data to the login API
    #                 $.ajax({
    #                     url: '.',
    #                     type: 'POST',
    #                     contentType: 'application/json',
    #                     data: JSON.stringify(data),
    #                     success: function(response) {
    #                         // Handle the response from the API
    #                         console.log(response);

    #                         // Redirect to another page if the API call is successful
    #                         window.location.href = '{next_url}';
    #                     },
    #                     error: function(error) {
    #                         console.error('Error:', error);
    #                     }
    #                 });
    #             }
    #         </script>
    #     </body>
    #     </html>"""
    #     )
    #     return header + form

    def post(self):
        username = request.form["user"]
        password = request.form["password"]
        next_url = request.form["next"]
        # data = request.get_json()
        # username = data.get("username")
        # password = data.get("password")
        # next_url = data.get("next")

        # TODO: if password not match...
        if password != "12345":
            abort(401)

        session["user"] = username
        logging.info(f"Logged user {username} in")
        logging.info("Redirecting to", next_url)

        from rich import print
        print(next_url)

        return redirect(next_url)
        # return Response("Good", 200)


def setup_saml(app: Flask):
    # app.debug = True
    app.secret_key = "not a secret"
    app.config["SERVER_NAME"] = "www.svc.deltaww-energy.com:5001"
    app.config["SAML2_IDP"] = {
        "autosubmit": True,
        "certificate": CERTIFICATE,
        "private_key": PRIVATE_KEY,
    }
    app.config["SAML2_SERVICE_PROVIDERS"] = [
        {
            "CLASS": "sso_server.saml.tests.idp.base.AttributeSPHandler",
            "OPTIONS": {
                "display_name": "Example Service Provider A",
                "entity_id": "https://www.svc.deltaww-energy.com:9000/saml/metadata.xml",
                "acs_url": "https://www.svc.deltaww-energy.com:9000/saml/acs/",
                "certificate": SP_CERTIFICATE,
            },
        },
        {
            "CLASS": "sso_server.saml.tests.idp.base.AttributeSPHandler",
            "OPTIONS": {
                "display_name": "Example Service Provider B",
                "entity_id": "https://www.svc.deltaww-energy.com:9001/saml/metadata.xml",
                "acs_url": "https://www.svc.deltaww-energy.com:9001/saml/acs/",
                "certificate": SP_CERTIFICATE,
            },
        },
    ]

    app.add_url_rule("/sso/saml/login", view_func=Login.as_view("saml_login"))
    app.register_blueprint(idp.create_blueprint(), url_prefix="/sso/saml/api")

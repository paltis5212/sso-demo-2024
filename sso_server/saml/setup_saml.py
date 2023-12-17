#!/usr/bin/env python3
from flask import Flask, abort, redirect, request, session, url_for, current_app
from flask.views import MethodView

from flask_saml2.idp import IdentityProvider

from .tests.idp.base import CERTIFICATE, PRIVATE_KEY, User
from .tests.sp.base import CERTIFICATE as SP_CERTIFICATE

class ExampleIdentityProvider(IdentityProvider):

    def login_required(self):
        if not self.is_user_logged_in():
            next = url_for("saml_login", next=request.url)

            abort(redirect(next))

    def is_user_logged_in(self):
        return "saml_user" in session and session["saml_user"] in users

    def logout(self):
        del session["saml_user"]

    def get_current_user(self):
        return users[session["saml_user"]]


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

    def post(self):
        username = request.form["user"]
        password = request.form["password"]
        next_url = request.form["next"]

        # TODO: if password not match...
        if password != "12345":
            abort(401)

        session["saml_user"] = username
        current_app.logger.info(f"Logged user {username} in")
        current_app.logger.info("Redirecting to", next_url)

        return redirect(next_url)


def setup_saml(app: Flask):
    # app.debug = True
    if "SECRET_KEY" not in app.config:
        app.secret_key = "secret"
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
                "display_name":
                    "Example Service Provider A",
                "entity_id":
                    "https://saml-spa.deltaww-energy.com:9000/saml/metadata.xml",
                "acs_url":
                    "https://saml-spa.deltaww-energy.com:9000/saml/acs/",
                "certificate":
                    SP_CERTIFICATE,
            },
        },
        {
            "CLASS": "sso_server.saml.tests.idp.base.AttributeSPHandler",
            "OPTIONS": {
                "display_name":
                    "Example Service Provider B",
                "entity_id":
                    "https://saml-spb.deltaww-energy.com:9001/saml/metadata.xml",
                "acs_url":
                    "https://saml-spb.deltaww-energy.com:9001/saml/acs/",
                "certificate":
                    SP_CERTIFICATE,
            },
        },
    ]

    app.add_url_rule("/sso/saml/login", view_func=Login.as_view("saml_login"))
    app.register_blueprint(idp.create_blueprint(), url_prefix="/sso/saml/api")

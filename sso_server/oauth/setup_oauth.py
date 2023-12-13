import os

from flask import Flask

from .models import db
from .oauth2 import config_oauth
from .routes import api


def setup_oauth_app(app: Flask, config=None):
    # load default configuration
    app.config.from_object("sso_server.oauth.settings")

    # load environment configuration
    if "SSO_SERVER_CONF" in os.environ:
        app.config.from_envvar("SSO_SERVER_CONF")

    # load app specified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif isinstance(config, str) and config.endswith(".py"):
            app.config.from_pyfile(config)

    db.init_app(app)
    # Create tables if they do not exist already
    with app.app_context():
        db.create_all()
    config_oauth(app)
    app.register_api(api)

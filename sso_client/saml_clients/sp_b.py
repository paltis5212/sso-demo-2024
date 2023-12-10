#!/usr/bin/env python3
from venv import logger

from flask import Flask, url_for

from flask_saml2.sp import ServiceProvider
from sso_server.saml.tests.idp.base import CERTIFICATE as IDP_CERTIFICATE
from sso_server.saml.tests.sp.base import CERTIFICATE, PRIVATE_KEY


class ExampleServiceProvider(ServiceProvider):

    def get_logout_return_url(self):
        return url_for("index", _external=True)

    def get_default_login_return_url(self):
        return url_for("index", _external=True)


sp = ExampleServiceProvider()

app = Flask(__name__)
app.debug = True
app.secret_key = "not a secret"

app.config["SERVER_NAME"] = "localhost:9001"
app.config["SAML2_SP"] = {
    "certificate": CERTIFICATE,
    "private_key": PRIVATE_KEY,
}

app.config["SAML2_IDENTITY_PROVIDERS"] = [
    {
        "CLASS": "flask_saml2.sp.idphandler.IdPHandler",
        "OPTIONS": {
            "display_name":
                "Identity Provider B",
            "entity_id":
                "https://www.svc.deltaww-energy.com:5001/sso/saml/api/metadata.xml",
            "sso_url":
                "https://www.svc.deltaww-energy.com:5001/sso/saml/api/login/",
            "slo_url":
                "https://www.svc.deltaww-energy.com:5001/sso/saml/api/logout/",
            "certificate":
                IDP_CERTIFICATE,
        },
    },
]


@app.route('/')
def index():
    if sp.is_user_logged_in():
        auth_data = sp.get_auth_data_in_session()

        message = f'''
        <p>Hi~ this is Service Provider B</p>
        <p>You are logged in as <strong>{auth_data.nameid}</strong>.
        The IdP sent back the following attributes:<p>
        '''

        print(auth_data.to_dict())

        # attrs = '<dl>{}</dl>'.format(''.join(
        #     f'<dt>{attr}</dt><dd>{value}</dd>'
        #     for attr, value in auth_data.attributes.items()))
        attrs = ""
        for attr, value in auth_data.attributes.items():
            attrs += f'{attr}: {value}\n'

        logout_url = url_for('flask_saml2_sp.logout')
        logout = f'<form action="{logout_url}" method="POST"><input type="submit" value="Log out"></form>'

        return message + attrs + logout
    else:
        message = '<p>Hi~ this is Service Provider A</p><p>You are logged out.</p>'

        login_url = url_for('flask_saml2_sp.login')
        link = f'<p><a href="{login_url}">Log in to continue</a></p>'

        return message + link


app.register_blueprint(sp.create_blueprint(), url_prefix='/saml/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001, ssl_context='adhoc')

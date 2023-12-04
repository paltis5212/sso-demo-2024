from sso_server.app import create_app


app = create_app({
    'SECRET_KEY': 'secret',
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.sqlite',
})

app.run(host="127.0.0.1", port=5001, debug=True, ssl_context="adhoc")

from flask import redirect, current_app, session, url_for
from flask_openapi3 import APIBlueprint
from requests import Response
from authlib.integrations.flask_client.apps import FlaskOAuth2App
from authlib.integrations.requests_client import OAuth2Session
from sso_server.oauth2 import authorization
from authlib.integrations.requests_client.oauth2_session import OAuth2Session


def get_sso() -> FlaskOAuth2App:
    return current_app.sso


def get_token() -> dict:
    return session.get("token")


def pop_token() -> dict:
    return session.pop("token")


def refresh_token(sso: FlaskOAuth2App = None, refresh_token: str = None, token: dict = None) -> dict | None:
    """
    Refresh token

    @param sso: A FlaskOAuth2App (Client).
    @param refresh_token: refresh_token 和 token['refresh_token'] 二選一，refresh_token 優先使用。
    @param token: 用於獲取 token['refresh_token']，如為 None，自動從 session 中獲取。
    @return: token: dict | None (獲取成功返回 token，失敗返回 None)
    """
    if not sso:
        sso = get_sso()

    # use refresh_token or token['refresh_token'] or get_token()['refresh_token']
    if _refresh_token := (
        refresh_token
        if refresh_token
        else token.get("refresh_token")
        if token
        else _token.get("refresh_token")
        if (_token := get_token())
        else None
    ):
        refresh_token = _refresh_token
    else:
        return None

    try:
        return sso.fetch_access_token(grant_type="refresh_token", refresh_token=refresh_token)
    except Exception:
        return None


api = APIBlueprint("Service", __name__)


@api.get("/")
def index():
    sso = get_sso()
    token = get_token()
    profile = None
    if token:
        # try get my data
        try:
            response: Response = sso.get("/api/me", token=token)
            profile = response.json()
            response.raise_for_status()
            uid = profile.get('id')

            return profile
        except:
            pass

        # try refresh token
        if new_token := refresh_token(sso, token["refresh_token"]):
            session["token"] = new_token
            return redirect("/")
        else:
            pop_token()

    # try login
    redirect_uri = url_for(".authorize", _external=True)
    return sso.authorize_redirect(redirect_uri)


@api.route("/authorize")
def authorize():
    sso = get_sso()
    token = sso.authorize_access_token()
    session["token"] = token
    return redirect("/")
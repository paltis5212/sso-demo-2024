import time

import bcrypt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error
from flask import jsonify, redirect, render_template, request, session, url_for
from flask_openapi3 import APIBlueprint
from sso_server.definition import ApiException, TokenEndpointAuthMethod
from sso_server.schema import (
    ErrorResponse,
    PostAuthorizeBody,
    PostCreateClientBody,
    PostHomeForm,
    PostRegisterBody,
)
from werkzeug.security import gen_salt

from .models import OAuth2Client, User, db
from .oauth2 import authorization, require_oauth

api = APIBlueprint("home", __name__)


def current_user() -> User | None:
    if uid := session.get("user_id"):
        return User.query.get(uid)
    return None


def split_by_crlf(s: str):
    return [v for v in s.splitlines() if v]


@api.get("/")
def get_home():
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []

    return render_template("home.html", user=user, clients=clients)


@api.post("/")
def post_home(form: PostHomeForm):
    """登入"""
    user: User = User.query.filter_by(username=form.username).first()
    if not user:
        raise ApiException(ErrorResponse(message="User not found."))
    if not user.check_password(form.password):
        raise ApiException(ErrorResponse(message="Invalid password."))

    # 驗證通過，登入
    session["user_id"] = user.id

    next_page = request.args.get("next")
    if next_page:
        return redirect(next_page)
    return redirect("/")


@api.get("/register")
def get_register():
    return render_template("register.html")


@api.post("/register")
def post_register(form: PostRegisterBody):
    """註冊"""
    username = form.username

    user: User = User.query.filter_by(username=username).first()
    if user:
        raise ApiException(ErrorResponse(message="User already exists."))

    # 加密
    password = form.password.encode("utf-8")
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    # 儲存
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return redirect("/")


@api.get("/logout")
def logout():
    """登出"""
    del session["user_id"]
    return redirect("/")


@api.get("/create_client")
def get_create_client():
    return render_template("create_client.html")


@api.post("/create_client")
def post_create_client(form: PostCreateClientBody):
    """建立客戶端"""
    user = current_user()
    if not user:
        return redirect("/")

    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=user.id,
    )

    client_metadata = {
        "client_name": form.client_name,
        "client_uri": form.client_uri,
        "grant_types": split_by_crlf(form.grant_type),
        "redirect_uris": split_by_crlf(form.redirect_uri),
        "response_types": split_by_crlf(form.response_type),
        "scope": form.scope,
        "token_endpoint_auth_method": form.token_endpoint_auth_method.value,
    }
    client.set_client_metadata(client_metadata)

    if form.token_endpoint_auth_method == TokenEndpointAuthMethod.NONE:
        client.client_secret = ""
    else:
        client.client_secret = gen_salt(48)

    db.session.add(client)
    db.session.commit()
    return redirect("/")


@api.get("/oauth/authorize")
def get_authorize():
    user = current_user()
    if not user:
        return redirect(url_for("home.get_home", next=request.url))

    try:
        grant = authorization.get_consent_grant(end_user=user)
    except OAuth2Error as error:
        raise ApiException(ErrorResponse(message=error.error))

    return render_template("authorize.html", user=user, grant=grant)


@api.post("/oauth/authorize")
def post_authorize(form: PostAuthorizeBody):
    user = current_user()
    if not user:
        return redirect(url_for("home.get_home", next=request.url))

    if form.confirm:
        grant_user = user
    return authorization.create_authorization_response(grant_user=grant_user)


@api.post("/oauth/token")
def issue_token():
    """根據 https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.1 規定，使用 form 來傳遞 Request。"""
    return authorization.create_token_response()


@api.post("/oauth/revoke")
def revoke_token():
    return authorization.create_endpoint_response("revocation")


@api.get("/api/me")
@require_oauth("profile")
def api_me():
    user: User = current_token.user
    return jsonify(id=user.id, username=user.username)

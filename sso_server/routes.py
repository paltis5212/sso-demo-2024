import time
from typing import Optional
import bcrypt
from flask import render_template, redirect, request, session, jsonify
from pydantic import BaseModel, Field
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error

from sso_server.definition import ApiException, TokenEndpointAuthMethod
from sso_server.schema import (
    ErrorResponse,
    GetHomeQuery,
    PostAuthorizeBody,
    PostCreateClientBody,
    PostHomeBody,
    PostIssueTokenBody,
    SuccessResponse,
)
from .models import db, User, OAuth2Client
from .oauth2 import authorization, require_oauth
from flask_openapi3 import APIBlueprint


api = APIBlueprint("home", __name__)


def current_user() -> User | None:
    if uid := session.get("user_id"):
        return User.query.get(uid)
    return None


def split_by_crlf(s: str):
    return [v for v in s.splitlines() if v]


@api.get("/")
def get_home(query: GetHomeQuery):
    """取得帳號和客戶端資訊"""
    if next_page := query.next:
        return redirect(next_page)

    user = current_user()

    if not user:
        raise ApiException(ErrorResponse(message="Please login first."))

    clients = [
        {
            "client_info": client.client_info,
            "client_metadata": client.client_metadata,
        }
        for client in OAuth2Client.query.filter_by(user_id=user.id).all()
    ]

    return SuccessResponse(data={"user": str(user), "clients": clients}).model_dump(mode="json")


@api.post("/")
def post_home(body: PostHomeBody):
    """登入或註冊"""
    username = body.username
    password = body.password

    user: User = User.query.filter_by(username=username).first()
    if user:
        if not user.check_password(password):
            raise ApiException(ErrorResponse(message="Invalid password."))
    else:
        # 加密
        password = password.encode("utf-8")
        password = bcrypt.hashpw(password, bcrypt.gensalt())
        # 存入
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
    # 保存帳號
    session["user_id"] = user.id

    return SuccessResponse().model_dump(mode="json")

@api.get('/logout')
def logout():
    """登出"""
    del session['user_id']
    return SuccessResponse().model_dump(mode="json")


@api.post("/create_client")
def post_create_client(body: PostCreateClientBody):
    """建立客戶端"""
    user = current_user()
    if not user:
        raise ApiException(ErrorResponse(message="Please login first."))

    client_id = gen_salt(24)
    client_id_issued_at = int(time.time())
    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=user.id,
    )

    client_metadata = {
        "client_name": body.client_name,
        "client_uri": body.client_uri,
        "grant_types": body.grant_type,
        "redirect_uris": body.redirect_uri,
        "response_types": body.response_type,
        "scope": body.scope,
        "token_endpoint_auth_method": body.token_endpoint_auth_method.value,
    }
    client.set_client_metadata(client_metadata)

    if body.token_endpoint_auth_method == TokenEndpointAuthMethod.NONE:
        client.client_secret = ""
    else:
        client.client_secret = gen_salt(48)

    db.session.add(client)
    db.session.commit()
    return SuccessResponse().model_dump(mode="json")


@api.get("/oauth/authorize")
def get_authorize():
    user = current_user()
    if not user:
        raise ApiException(ErrorResponse(message="Please login first."))
    try:
        grant = authorization.get_consent_grant(end_user=user)
    except OAuth2Error as error:
        raise ApiException(ErrorResponse(message=error.error))
    return SuccessResponse(data={"user": str(user), "grant": grant}).model_dump(mode="json")


@api.post("/oauth/authorize")
def post_authorize(body: PostAuthorizeBody):
    user = current_user()
    if not user:
        raise ApiException(ErrorResponse(message="Please login first."))

    if username := body.username:
        user = User.query.filter_by(username=username).first()
    grant_user = None
    if body.confirm:
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
    user = current_token.user
    return jsonify(id=user.id, username=user.username)

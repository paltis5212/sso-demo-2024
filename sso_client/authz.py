from enum import Enum
from flask import current_app, session, Response
from flask_authz import CasbinEnforcer
from flask_openapi3 import OpenAPI, APIBlueprint, Tag
import casbin_sqlalchemy_adapter
from casbin import Enforcer
from typing import Callable
from pydantic import BaseModel, Field
from sso_client.models import User
from util.schema import ErrorResponse, SuccessResponse
from util.exception import BadRequestException


class Role(Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class GetRolesQuery(BaseModel):
    user_id: str = Field(description="client user id")


class PostRoleBody(BaseModel):
    user_id: str = Field(description="client user id")
    role: Role = Field(description="role name")


class DeleteRolePath(BaseModel):
    user_id: str = Field(description="client user id")
    role: Role = Field(description="role name")


def authz_config(app: OpenAPI):
    app.config.update(
        {
            "CASBIN_MODEL": "sso_client/casbin_files/casbinmodel.conf",
            "CASBIN_OWNER_HEADERS": {"X-User", "X-Group"},
            "CASBIN_USER_NAME_HEADERS": {"X-User"},
        }
    )
    adapter = casbin_sqlalchemy_adapter.Adapter(
        f"sqlite:///instance/{app.config['SQLALCHEMY_DATABASE_FILENAME']}"
    )
    casbin_enforcer: CasbinEnforcer = CasbinEnforcer(app, adapter)
    casbin_enforcer.owner_loader(lambda: [str(session.get("user_id"))])
    app.casbin_enforcer = casbin_enforcer


def conditional_decorator(dec: Callable, condition: bool):
    def decorator(func):
        if not condition:
            # 如果條件不成立，則返回未裝飾的函數
            return func
        return dec(func)

    return decorator


def enforcer_or_manager(
    use_enforcer: bool = False, use_manager: bool = False
) -> Enforcer | tuple[Response, int]:
    casbin_enforcer: CasbinEnforcer = current_app.casbin_enforcer

    @conditional_decorator(casbin_enforcer.enforcer, use_enforcer)
    @conditional_decorator(casbin_enforcer.manager, use_manager)
    def protected(manager: Enforcer = None):
        return manager

    return protected()


def get_hello_message(role_name: str):
    manager = enforcer_or_manager(use_enforcer=True)
    if isinstance(manager, tuple):
        return manager

    user: User = User.query.get(session["user_id"])

    return f"Hello {user.profile.get('username')}, you have a {role_name} role."


api = APIBlueprint("RBAC", __name__, abp_tags=[Tag(name="RBAC")], url_prefix="/rbac")


@api.get("/roles")
def roles(query: GetRolesQuery):
    """獲得某位 User 的角色列表"""
    manager = enforcer_or_manager(use_enforcer=True, use_manager=True)
    if isinstance(manager, tuple):
        return manager
    manager.load_policy()
    return manager.get_roles_for_user(query.user_id)


@api.post("/role")
def post_role(body: PostRoleBody):
    """給某位 User 增加角色"""
    manager = enforcer_or_manager(use_enforcer=True, use_manager=True)
    if isinstance(manager, tuple):
        return manager
    try:
        if manager.add_role_for_user(body.user_id, body.role.value):
            return SuccessResponse(message="add role success").model_dump(mode="json")
    except Exception:
        pass
    raise BadRequestException(message="add role fail")


@api.delete("/role/<string:user_id>/<string:role>")
def delete_role(path: DeleteRolePath):
    manager = enforcer_or_manager(use_enforcer=True, use_manager=True)
    if isinstance(manager, tuple):
        return manager
    try:
        if manager.delete_role_for_user(path.user_id, path.role.value):
            return SuccessResponse(message="delete role success").model_dump(
                mode="json"
            )
    except Exception:
        pass
    raise BadRequestException(message="add role fail")


@api.get("/admin/hello")
def get_admin_hello():
    return get_hello_message(Role.ADMIN.value)


@api.get("/moderator/hello")
def get_moderator_hello():
    return get_hello_message(Role.MODERATOR.value)


@api.get("/user/hello")
def get_user_hello():
    return get_hello_message(Role.USER.value)

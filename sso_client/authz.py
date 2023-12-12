from flask import Flask, jsonify, current_app, request, session, Response
from flask_authz import CasbinEnforcer
from flask_openapi3 import OpenAPI, APIBlueprint, Tag
import casbin_sqlalchemy_adapter
from casbin import Enforcer
from typing import Callable

def authz_config(app: OpenAPI):
    app.config.update({
        "CASBIN_MODEL": 'sso_client/casbin_files/casbinmodel.conf',
        'CASBIN_OWNER_HEADERS': {'X-User', 'X-Group'},
        'CASBIN_USER_NAME_HEADERS': {'X-User'},
    })
    adapter = casbin_sqlalchemy_adapter.Adapter(f"sqlite:///instance/{app.config['SQLALCHEMY_DATABASE_FILENAME']}")
    casbin_enforcer: CasbinEnforcer = CasbinEnforcer(app, adapter)
    # casbin_enforcer.owner_loader(lambda: session.get("user_id"))
    casbin_enforcer.owner_loader(lambda: ["person123"])
    app.casbin_enforcer = casbin_enforcer

def conditional_decorator(dec: Callable, condition: bool):
    def decorator(func):
        if not condition:
            # 如果條件不成立，則返回未裝飾的函數
            return func
        return dec(func)
    return decorator

def enforcer_or_manager(use_enforcer: bool=False, use_manager: bool=False) -> Enforcer | Response:
    casbin_enforcer: CasbinEnforcer = current_app.casbin_enforcer

    @conditional_decorator(casbin_enforcer.enforcer, use_enforcer)
    @conditional_decorator(casbin_enforcer.manager, use_manager)
    def protected(manager: Enforcer = None):
        return manager
    
    return protected()

# def enforcer_or_manager():
#     casbin_enforcer: CasbinEnforcer = current_app.casbin_enforcer
#     @casbin_enforcer.enforcer
#     @casbin_enforcer.manager
#     def protected(_manager: Enforcer):
#         return _manager


api = APIBlueprint('RBAC', __name__, abp_tags=[Tag(name='RBAC')], url_prefix='/rbac')

@api.get("/my_roles")
def my_roles():

    # if isinstance(enforcer_or_manager(use_manager=True), Response):

    return {"123":"vvv"}
    # casbin_enforcer: CasbinEnforcer = current_app.casbin_enforcer
    # @casbin_enforcer.enforcer
    # @casbin_enforcer.manager
    # def protected(_manager: Enforcer):
    #     return _manager
    # manager: Enforcer = protected()
    # manager.load_policy()
    # return manager.get_all_roles()

@api.get("/add_role")
def add_role():
    casbin_enforcer: CasbinEnforcer = current_app.casbin_enforcer
    # @casbin_enforcer.enforcer
    @casbin_enforcer.manager
    def protected(manager: Enforcer):
        manager.load_policy()
        print(manager)
        return manager.get_all_roles()
    
    return protected()
# @app.route('/', methods=['GET'])
# @casbin_enforcer.enforcer
# def get_root():
#     return jsonify({'message': 'If you see this you have access'})

# @app.route('/manager', methods=['POST'])
# @casbin_enforcer.enforcer
# @casbin_enforcer.manager
# def make_casbin_change(manager):
#     # Manager is an casbin.enforcer.Enforcer object to make changes to Casbin
#     return jsonify({'message': 'If you see this you have access'})
from os import path
from functools import wraps
from flask import g, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import app_api
from app import login_manager
from .admin_utils import AdminUtils, AdminConf
from app.admin_mgt.models.embedded_user import EmbeddedUser

if app_api.is_app_module_enabled('user_mgt'):
    from app.user_mgt.models.users import User
    from app.user_mgt.models.roles import Role


def requires_auth(f):
    """ Декоратор для осуществлениы доступа к частям портала """

    _private_portal = True
    _app_pth = app_api.get_app_root_dir()
    __key_file = path.join(_app_pth, 'portal_auth.disable')
    if path.exists(__key_file):
        _private_portal = False  # disable @login_required

    if _private_portal:
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            # print(request.environ)
            # print(g)
            # print(current_user)
            curr_user = g.user if g.user else current_user
            # print('User is admin', EmbeddedUser.is_local_admin(curr_user.login))
            # print('request.path', request.path)
            # print('is_admin_url', AdminUtils.is_admin_url(request.path))
            if not EmbeddedUser.is_local_admin(curr_user.login) and AdminUtils.is_admin_url(request.path):
                # flash(u'You need to be signed in for this page as Administrator.')
                return redirect(url_for(login_manager.login_view, next=request.path))
            # if not AdminUtils.can_access_to_url(request.path):
            #     flash(u'У Вас нет прав доступа к данному адресу.')
            #     next_page = request.args.get('next')
            #     return redirect(url_for(login_manager.login_view, next=request.path))
            return f(*args, **kwargs)
    else:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # print(request.environ)
            # print(g)
            # print('decorated_function -> current_user', current_user)
            curr_user = g.user if g.user else current_user
            # print('decorators.open_portal.User is admin', EmbeddedUser.is_local_admin(curr_user.login))
            # print('decorators.open_portal.request.path', request.path)
            # print('decorators.open_portal.is_admin_url', AdminUtils.is_admin_url(request.path))
            # Требуется добавить проверку
            _u_login = curr_user.login if hasattr(curr_user, 'login') else 'anonimous'
            # print('decorators.open_portal->_u_login', _u_login)
            if AdminUtils.is_admin_url(request.path) and not EmbeddedUser.is_local_admin(_u_login):
                # flash(u'You need to be signed in for this page as Administrator.')
                # print('decorators.open_portal.request.path', request.path)
                return redirect(url_for(login_manager.login_view, next=request.path))
            # if not AdminUtils.can_access_to_url(request.path):
            #     flash(u'У Вас нет прав доступа к данному адресу.')
            #     next_page = request.args.get('next')
            #     return redirect(url_for(login_manager.login_view, next=request.path))
            return f(*args, **kwargs)
    return decorated_function

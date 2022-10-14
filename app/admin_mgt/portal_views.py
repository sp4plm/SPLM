# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса портала по URL - /portal
"""

from flask import Blueprint, request, flash, g, session, redirect, url_for, current_app
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from .admin_utils import os # import embeded pythons
from .admin_utils import app_api # import application globals
from .admin_utils import AdminConf, AdminUtils # import current module libs
from .portal_navigation import PortalNavigation
from app.utilites.code_helper import CodeHelper

from .forms import LoginForm # , RegisterForm
from .configurator import Configurator

from app.admin_mgt.models.user import User, EmbeddedUser
if app_api.is_app_module_enabled('user_mgt'):
    # print('catch user module')
    from app.user_mgt.models.users import User

mod = Blueprint('portal', __name__, url_prefix=AdminConf.MOD_WEB_ROOT,
                static_folder=AdminConf.get_web_static_path(),
                template_folder=AdminConf.get_web_tpl_path())

from .decorators import requires_auth


@mod.route('/login', methods=['GET', 'POST'])
def login():
    # print(request.environ)
    tmpl_vars = {}
    tmpl_vars['title'] = 'Авторизация'
    tmpl_vars['page_title'] = 'Авторизация'

    _p_navi = PortalNavigation()
    _start_url = _p_navi.get_portal_index_url()

    if current_user.is_authenticated:
        # правильную страницу надо определять в настройках
        # redirect to defautl page from settings
        return redirect(_start_url)
    form = LoginForm()
    if form.validate_on_submit():
        # try to log in by local admin
        is_local_admin = False
        secret = form.secret.data
        if User.is_local_admin(form.username.data):
            user = User.auth_admin(form.username.data, form.secret.data)
            is_local_admin = True
        else:
            # если портал не сконфигурирован то возвращаем False
            _portal_configurator = Configurator()
            _portal_configurator.set_app_dir(app_api.get_app_root_dir())
            if not _portal_configurator.check_inst_marker():
                flash('Неверное имя пользователя или пароль')
                return redirect(url_for('portal.login'))
            user = User.query.filter_by(login=form.username.data).first()
            portal_cfg = AdminUtils.get_portal_config()
            # если авторизовываемся во внешнем сервисе, то:
            if 'local' != portal_cfg.get('main.Auth.type'):
                # получить драйвер авторизации
                portal_auth = AdminUtils.get_auth_provider() # type: AuthProvider
                # попытаться авторизоваться во внешнем сервисе
                # при успешной авторизации получить данные пользователя
                if portal_auth.login(form.username.data, secret):
                    # если такого пользователя нет, то требуется создать и выбрать заново
                    auth_user = portal_auth.get_user(form.username.data)
                    spec_key = 'password'
                    # hack - если поиск пустой а пользователь валидный и авторизовался
                    if not isinstance(auth_user, dict):
                        _t = {'name': '', 'login': '', 'email':''}
                        _t['name'] = form.username.data
                        _t['login'] = form.username.data
                        _t['email'] = form.username.data + '@company.local'
                        auth_user = _t
                    from hashlib import sha1
                    auth_user[spec_key] = ''
                    base = auth_user['email'] + secret + '//'
                    auth_user[spec_key] = sha1(base.encode()).hexdigest()
                    if not user:
                        new_user_data = {}
                        new_user_data['name'] = auth_user['name']
                        new_user_data['login'] = auth_user['login']
                        new_user_data[spec_key] = auth_user[spec_key]
                        new_user_data['email'] = auth_user['email']
                        new_user_data['roles'] = []
                        # print('new user')
                        try:
                            user = User(**new_user_data)
                            user.set_password(new_user_data[spec_key])
                            db.session.add(user)
                            db.session.commit()
                        except:
                            user = None
                    # пароль локального пользователя будет отличаться от введеного в форму
                    # следовательно его следует заменить на правильный!!!
                    # перезапрашиваем данные пользователя
                    secret = auth_user[spec_key]
                    user = User.query.filter_by(login=form.username.data).first()
                else:
                    user = None
        # print(user)
        if user is None or not user.check_password(secret):
                flash('Неверное имя пользователя или пароль')
                return redirect(url_for('portal.login'))
        login_user(user, remember=form.remember_me.data)
        # добавим в лог запись об успешной авторизации пользователя
        _auth_logger = AdminUtils.get_auth_logger()
        _str = ''
        _now = AdminUtils.get_now()
        _str = '['+_now.strftime("%Y-%m-%d")+'] ['+_now.strftime("%H:%M:%S")+'] ['+form.username.data+']'+"\n"
        _auth_logger.write(form.username.data)
        # перенаправляем на требуюмую страницу
        # https://habr.com/en/post/346346/ look
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            # правильней из настроек брать URL для перенаправления на стартовую
            # redirect to defautl page from settings
            next_page = _start_url
            if not app_api.check_in_registred_urls(next_page):
                next_page = url_for('admin_mgt.index')
        if is_local_admin:
            next_page = url_for('admin_mgt.index')
        return redirect(next_page)
    tmpl_vars['form'] = form
    _tpl_name = os.path.join(AdminConf.MOD_NAME, 'login.html')
    return app_api.render_page(_tpl_name, **tmpl_vars)
# # """


@mod.route('/logout', methods=['GET'])
def logout():
    logout_user()
    # redirect to portal main page page from settings
    _url = '/'
    try:
        _p_navi = PortalNavigation()
        _url = _p_navi.get_portal_index_url()
    except Exception as ex:
        print(AdminConf.MOD_NAME + '.views.logout.Exception: ' + str(ex))
        _url = '/'
    return redirect(_url)


@mod.route('/welcome', methods=['GET'])
def welcome():
    tmpl_vars = {}
    tmpl_vars['title'] = 'Приветственная страница портала'
    tmpl_vars['page_title'] = 'Добро пожаловать на портал'
    prj_name = ''
    try:
        prj_name = app_api.get_portal_labels('projectLabel')
        tmpl_vars['page_title'] += ' ' + prj_name
    except:
        pass
    tmpl_vars['welcome_text'] = 'Еще чуть-чуть и портал откроет свои двери для посетителей. :)'
    _tpl_name = os.path.join(AdminConf.MOD_NAME, 'portal', 'welcome.html')
    return app_api.render_page(_tpl_name, **tmpl_vars)


@mod.route('/uacclog/export/excel/', methods=['GET'])
@requires_auth
def __export_users_log():
    errorMsg = 'Не удалось скачать лог авторизации пользователей!'
    _auth_logger = AdminUtils.get_auth_logger()
    # _auth_logger = Utils.get_auth_logger()
    file_name = 'access_log_export.xls'
    _dir = app_api.get_mod_data_path(AdminConf.MOD_NAME)
    file_path = os.path.join(_dir, file_name)
    CodeHelper.add_file(file_path)
    _data = _auth_logger.export()
    CodeHelper.write_to_file(file_path, _data)
    file_handle = CodeHelper.get_file(file_path)

    if CodeHelper.check_file(file_path) and file_handle is not None:

        @mod.after_app_request
        def _remove_file(response):
            try:
                os.unlink(file_path)
                file_handle.close()
            except Exception as error:
                current_app.logger.error("Error removing or closing downloaded file handle", error)
            return response

        mime = 'application/x-unknown'
        from flask import send_file
        return send_file(file_path, mimetype=mime,
                         as_attachment=True, attachment_filename=file_name)
    return app_api.render_page("errors/404.html", message=errorMsg)

# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса портала
"""

import os
import json
import subprocess
import sys
from math import ceil

from flask import Blueprint, request, flash, g, session, redirect, url_for
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app import app_api
# mod_manager = app_api.get_mod_manager()
from app.module_mgt.manager import Manager
from .admin_utils import AdminUtils, AdminConf
from .mod_api import ModApi
from .admin_navigation import AdminNavigation
from .decorators import requires_auth


from ..utilites.extend_processes import ExtendProcesses


from .forms import LoginForm # , RegisterForm

from app.admin_mgt.models.user import User, EmbeddedUser
if app_api.is_app_module_enabled('user_mgt'):
    # print('catch user module')
    from app.user_mgt.models.users import User

mod = Blueprint(AdminConf.MOD_NAME, __name__, url_prefix=AdminConf.MOD_WEB_ROOT,
                static_folder=AdminConf.get_web_static_path(),
                template_folder=AdminConf.get_web_tpl_path())

mod.add_app_template_global(ModApi.get_root_tpl, name='admin_root_tpl')
# добавить навигацию по секциям
admin_navi = AdminNavigation()
mod.add_app_template_global(request, name='flask_request')
mod.add_app_template_global(admin_navi.get_sections, name='admin_sections')
mod.add_app_template_global(admin_navi.get_sections_navi, name='admin_section_navi')
mod.add_app_template_global(admin_navi.get_current_section, name='admin_current_section')
mod.add_app_template_global(admin_navi.get_current_subitem, name='admin_current_subitem')


# импорт дочерних модулей {
try:
    from .portal_views import mod as portal_mod
    from .installer_views import mod as installer_mod
    from .management_views import mod as management_mod
    from .configurator_views import mod as configurator_mod
except Exception as ex:
    print(AdminConf.MOD_NAME + '.ImportBlueprintsException: Try import in views:', ex)
# импорт дочерних модулей {


# для начала опишем системную обработку перед любым запросом


@mod.route('/', methods=['GET'])
@requires_auth
def index():
    """
    Функция отвечает за обработку главной страницы административного интерфейса
    :return: html страницы
    """
    # проверяем тип авторизации
    # стартуем сессию для пользователя

    tmpl_vars = {}
    # tmpl_vars['project_name'] = 'Semantic PLM'
    tmpl_vars['title'] = 'Административный интерфейс'
    tmpl_vars['page_title'] = 'Административный интерфейс портала'
    tmpl_vars['page_side_title'] = 'Содержание раздела'
    admin_navi = AdminNavigation()
    sections = admin_navi.get_sections()
    if sections:
        tmpl_vars['current_section'] = sections[0]
        tmpl_vars['page_title'] = tmpl_vars['current_section']['label']
    # tmpl_vars['page_side_title'] = 'Содержание раздела'

    # print('host', request.host)
    # print('endpoint', request.endpoint)
    # print('url', request.url)
    # print('full_path', request.full_path)
    # print('path', request.path)
    # print('module', request.module) # ???????
    return app_api.render_page(AdminConf.get_root_tpl(), **tmpl_vars)


@mod.route('/modes', methods=['GET'])
@requires_auth
def __modes_management():
    _tpl_vars = {}
    _tpl_name = os.path.join(AdminConf.MOD_NAME, 'modes.html')
    _tpl_vars['base_url'] = url_for(mod.name + '.__modes_management')
    _tpl_vars['modes_list'] = []
    _admin_mgt_api = app_api.get_mod_api('admin_mgt')
    _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
    _portal_mode = None
    if _portal_modes_util is not None:
        _modes = _portal_modes_util.get_modes()
        if _modes:
            # _mode is a PortalMode
            for _mode in _modes:
                """
                <td>Название</td>
                <td>Модуль инициатор</td>
                <td>Время старта</td>
                <td>Использует перенаправление</td>
                """
                _t = {}
                _t['name'] = _mode.get_name()
                _t['app_module'] = _mode.get_initiator()
                _t['started'] = _mode.get_start_time('%Y-%m-%d %H:%M:%S')  # default is timestamp
                _t['use_redirect'] = _mode.use_redirecting()  # True or False
                _tpl_vars['modes_list'].append(_t)

    return app_api.render_page(_tpl_name, **_tpl_vars)


@mod.route('/modes/drop/<name>', methods=['GET'])
@requires_auth
def __drop_portal_mode(name):
    _next_page = mod.name + '.__modes_management'
    _admin_mgt_api = app_api.get_mod_api('admin_mgt')
    _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
    _portal_mode = None
    if _portal_modes_util is not None:
        _portal_mode = _portal_modes_util.get_current(name)
        if _portal_mode is not None:
            # _portal_mode.disable()
            _portal_modes_util.drop(_portal_mode)
    _go_to = url_for(_next_page)
    return redirect(_go_to)


@mod.route('/<modname>' , methods=['GET'])
@requires_auth
def module_base_view(modname):
    """"""
    # требуется определить по имени url зарегистрированного модуля


@mod.route('/configure/db', methods=['GET'])
@mod.route('/db_reconfigure', methods=['GET'])
@requires_auth
def local_db_reconfigure():
    """"""

    from app.admin_mgt.configurator import Configurator
    _portal_configurator = Configurator()
    _portal_configurator.set_app_dir(app_api.get_app_root_dir())

    _flg = _portal_configurator.configure_db(app_api.get_app_root_dir())
    steps = _portal_configurator.get_db_configure_steps()

    steps_str = ''
    if steps:
        steps_str = '<br />'.join(steps)
        steps_str = '<hr />' + steps_str
    return 'Reconfiguration complite!' + steps_str


@mod.route('/export/tz', methods=['GET'])
def export_tz():
    # определяем дефолтный префикс
    if 'prefix' in request.args:
        pref = request.args['prefix']
    else:
        pref = "onto"

    # находим онтологию по префиксу
    prefixes = app_api.get_mod_api('onto_mgt').get_prefixes()
    for p in prefixes:
        if p[0] == pref:
            ontology = p[1]

    html = ''
    html = '<pre>' + str(app_api.tsc_query('query_mgt.exports.list_tz', {"PREF" : ontology})) + '</pre>'
    return html


@mod.route('/test/mode/enable', methods=['GET'])
def _enable_portal_mode():
    _html = ''
    # требуется установить режим портала ограничивающий
    _admin_mgt_api = app_api.get_mod_api('admin_mgt')
    _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
    _portal_mode = None
    if _portal_modes_util is not None:
        _portal_mode = _portal_modes_util.set_portal_mode('test_mod')
        _portal_mode.set_target('admin_mgt._view_portal_mode')
        _portal_mode.set_opened(['admin_mgt._disable_portal_mode'])
        _portal_mode.enable_redirect()
        _portal_mode.enable()
    return _html


@mod.route('/test/mode/view', methods=['GET'])
def _view_portal_mode():
    _html = ''
    # требуется установить режим портала ограничивающий
    _admin_mgt_api = app_api.get_mod_api('admin_mgt')
    _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
    _portal_mode = None
    if _portal_modes_util is not None:
        _portal_mode = _portal_modes_util.get_current()
        _html = 'Portal mode "' + _portal_mode.get_name() + '" started: ' + str(_portal_mode.get_start_time('%Y-%m-%d %H:%M:%S'))
    return _html


@mod.route('/test/mode/disable', methods=['GET'])
def _disable_portal_mode():
    _html = ''
    # требуется установить режим портала ограничивающий
    _admin_mgt_api = app_api.get_mod_api('admin_mgt')
    _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
    _portal_mode = None
    if _portal_modes_util is not None:
        _portal_mode = _portal_modes_util.get_current('test_mod')
        _portal_mode.disable()
    return _html

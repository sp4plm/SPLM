# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса портала
"""

import os

from flask import Blueprint, request, redirect, url_for
from app import app_api
from .admin_utils import AdminUtils, AdminConf
from .mod_api import ModApi
from .admin_navigation import AdminNavigation
from .decorators import requires_auth
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
    :return: html код страницы
    :rtype str:
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


@mod.route('/version_info')
def __portal_version():
    _v = AdminUtils.get_build_version()
    return _v


@mod.route('/modes', methods=['GET'])
@requires_auth
def __modes_management():
    """
    Функция формирует страницу - реестр режимов работы портала. На странице отображаются
    только действющие(включенные) режимы портала.
    :return: HTML страница.
    :rtype str:
    """
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
    """
    Функция реализует остановку работы режима портала
    :param name: имя режима
    :return: перенаправление на страницу реестра
    """
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
    html = '<pre>' + str(app_api.tsc_query('mod_reports.exports.list_tz', {"PREF" : ontology})) + '</pre>'
    return html

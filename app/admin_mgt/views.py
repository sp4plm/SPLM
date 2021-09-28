# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса портала
"""

import os
import json
import subprocess
import sys
from math import ceil

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app import app, db, app_api, CodeHelper, mod_manager
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
    return render_template(AdminConf.get_root_tpl(), **tmpl_vars)


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

    # # проверка что DB неинициализирована - flask db init
    # cmd = 'flask db init'
    # app_root_dir = app_api.get_app_root_dir()
    # migrate_dir = os.path.join(os.path.dirname(app_root_dir), 'migrations')
    # versions_dir = os.path.join(migrate_dir, 'versions')
    # errors = None
    # output = None
    # steps = []
    #
    # print('os.getcwd()', os.getcwd())
    # is_init = False
    # if os.path.exists(migrate_dir) and os.path.isdir(migrate_dir)\
    #     and os.path.exists(versions_dir) and os.path.isdir(versions_dir):
    #     """ будем считать что директория инициализирована"""
    #     is_init = True
    # else:
    #     """ запускаем инициализацию """
    #     # print('sys.path', sys.path)
    #     cmd_args = cmd.split(' ')
    #     run_cmd = subprocess.Popen(cmd_args)
    #     output, errors = run_cmd.communicate()
    #     is_init = True
    #     if errors:
    #         is_init = False
    #         return errors
    # if is_init:
    #     scripts = [it.name for it in os.scandir(versions_dir)]
    #     # создаем комментарий о дате реконфигурации
    #     cmt = 'DB autoreconfiguration ' + AdminUtils.get_dbg_now()
    #     # создаем скрипт реконфигурации
    #     cmd = 'flask db migrate -m'
    #     cmd_args = cmd.split(' ')
    #     cmd_args.append('"' + cmt + '"')
    #     run_cmd = subprocess.Popen(cmd_args)
    #     output, errors = run_cmd.communicate()
    #     scripts1 = [it.name for it in os.scandir(versions_dir)]
    #     if errors:
    #         return errors
    #     # выполняем реконфигурацию
    #     cmd = 'flask db upgrade'
    #     if 0 < len(scripts1) - len(scripts):
    #         cmd_args = cmd.split(' ')
    #         run_cmd = subprocess.Popen(cmd_args)
    #         output, errors = run_cmd.communicate()
    #         if errors:
    #             return errors
    #         steps.insert(0, 'DB upgrade done!')
    #     steps.insert(0, 'Create migration scripts!')
    #     steps.insert(0, 'DB initialization done!')
    steps_str = ''
    if steps:
        steps_str = '<br />'.join(steps)
        steps_str = '<hr />' + steps_str
    return 'Reconfiguration complite!' + steps_str


# @mod.route('/PortalSettings/Configs/<config_name>', defaults={'config_name': ''}, methods=['GET'])
# @requires_auth
# def edit_settings_view(config_name):
#     """
#     Функция создает страницу редактирования ini файла
#     :param config_name: имя ini файла из директории data/cfg в директории модуля
#     :return: сформированный шаблон страницы
#     """
#     tmpl_vars = {}
#     # tmpl_vars['project_name'] = 'Semantic PLM'
#     tmpl_vars['title'] = 'Административный интерфейс'
#     tmpl_vars['page_title'] = 'Настройки портала: ' + config_name
#     tmpl_vars['page_side_title'] = 'Содержание раздела'
#     work_dir = AdminConf.CONFIGS_PATH
#     files_list = [fi.name for fi in os.scandir(work_dir)]
#     for fi in files_list:
#         lp = fi.rfind('.')
#         name = fi[:lp]
#         if name == config_name:
#             break
#     data_file = os.path.join(work_dir, fi)
#     # превращаем словарь в HTML
#     edit_data = AdminUtils.ini2dict(data_file)
#     # первичные ключи это секции - Вопрос где хранить натменование секций????
#     # вторичные ключи - имена полей
#     tmpl_vars['edit_data'] = edit_data
#     return render_template('config_editor.html', **tmpl_vars)

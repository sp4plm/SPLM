# -*- coding: utf-8 -*-
import os
from datetime import datetime
from flask import Blueprint

from app import app_api
from app.utilites.utilites import Utilites
from .mod_utils import ModUtils

__mod_utils= ModUtils()
__mod_utils.init()
_mod_path = __mod_utils.get_mod_path()
_mod_name = __mod_utils.get_mod_name()
_web_prefix = __mod_utils.get_mod_web_prefix()


mod = Blueprint(_mod_name, __name__, url_prefix=_web_prefix,
                static_folder=os.path.join(_mod_path, 'static'),
                template_folder=os.path.join(_mod_path, 'templates'))

_auth_decorator = app_api.get_auth_decorator()


@mod.route('/servers', methods=['GET'])
@_auth_decorator
def __servers_manage():
    _tpl_name = os.path.join(_mod_name, 'servers.html')
    _tpl_vars = {}
    _tpl_vars['page_title'] = 'Настройка серверов авторизации'
    _tpl_vars['page_side_title'] = ''
    _tpl_vars['base_url'] = _web_prefix
    _tpl_vars['servers'] = []  # список имеющихся

    # надо смешать файлы находящиеся в модуле - неизмененные
    # и пересечение с измененными и созданными вновь файлами
    _lst = ModUtils().get_navi_servers_lst()
    if _lst:
        for _li in _lst:
            _tpl_vars['servers'].append(_li)

    return app_api.render_page(_tpl_name, **_tpl_vars)


@mod.route('/server/<name>', methods=['GET'])
@_auth_decorator
def __server_view(name):
    _mod_utils = ModUtils()
    _mod_name = _mod_utils.get_mod_name()
    _tpl_name = os.path.join(_mod_name, 'server.html')
    _tpl_vars = {}
    _tpl_vars['page_title'] = 'Настройка серверa авторизации: ' + name
    _tpl_vars['page_side_title'] = 'Список настроенных серверов'
    _tpl_vars['base_url'] = _web_prefix

    _tpl_vars['navi'] = []  # список имеющихся файлов
    _t = ModUtils().get_navi_servers_lst()
    if _t:
        for ni in _t:
            if not ni['href'].endswith(name):
                _tpl_vars['navi'].append(ni)

    _tpl_vars['is_default'] = False

    data_file = _mod_utils.get_server_file(name)  # get server ini file if no file - use default.ini from module ConfiguratorUtils.get_conf_file(config_name)
    # print(_mod_name + '.views.__server_view->data_file: ', data_file)
    # _time = str(datetime.now().timestamp())
    # _new_name = 'server_' + _time.split('.')[0]
    # _tpl_vars['edit_name'] = name if 'new' != name else os.path.basename(data_file).replace('.ini', '')
    editor = Utilites.get_file_editor()
    _tpl_vars['is_default'] = _mod_utils.is_default_server(data_file)
    _tpl_vars['mod_name'] = _mod_name
    _tpl_vars['source_name'] = data_file
    edit_data = {}
    if os.path.exists(data_file):
        edit_data = editor.ini2dict(data_file)
        mod_path = _mod_utils.get_mod_path()
        _tpl_vars['source_name'] = data_file.replace(mod_path, '')
    else:
        _template = _mod_utils.get_server_template()
        edit_data = editor.ini2dict(_template, True)
    _tpl_vars['edit_data'] = edit_data
    return editor.render_page(_tpl_name, _tpl_vars)

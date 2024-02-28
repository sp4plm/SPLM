# -*- coding: utf-8 -*-
"""
Модуль предназначен для печати в PDF
"""
import os

from flask import Blueprint, request, url_for
from app import app_api
from app.utilites.utilites import Utilites
from .mod_conf import ModConf


mod = Blueprint(ModConf.MOD_NAME, __name__, url_prefix=ModConf.MOD_WEB_ROOT,
                static_folder=ModConf.get_web_static_path(),
                template_folder=ModConf.get_web_tpl_path())

_admin_mod_api = None
_admin_mod_api = app_api.get_mod_api('admin_mgt')
_auth_decorator = app_api.get_auth_decorator()


@mod.route('/manage', methods=['GET', 'POST'])
@_auth_decorator
def manage():
    tmpl_vars = {}
    tmpl_vars['page_title'] = 'Настройки модуля ' + ModConf.MOD_NAME

    editor = Utilites.get_file_editor()
    _config_file = os.path.join(ModConf.get_mod_path('env'), 'main.ini')
    if os.path.exists(_config_file):
        # превращаем словарь в HTML
        edit_data = editor.ini2dict(_config_file)
        # первичные ключи это секции - Вопрос где хранить натменование секций????
        # вторичные ключи - имена полей
        tmpl_vars['edit_data'] = edit_data
        mod_path = ModConf.SELF_PATH
        tmpl_vars['source_name'] = _config_file.replace(mod_path, '')
        tmpl_vars['mod_name'] = ModConf.MOD_NAME
    return editor.render_page(os.path.join(ModConf.MOD_NAME, 'manage.html'), tmpl_vars)

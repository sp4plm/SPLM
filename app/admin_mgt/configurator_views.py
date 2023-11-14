# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса портала по URL - /portal/
"""
import json

from flask import Blueprint, request, flash, g, session, redirect, url_for

from .admin_utils import os  # import embeded pythons
from .admin_utils import app_api, CodeHelper  # import application globals
from .admin_utils import AdminConf, AdminUtils  # import current module libs
from .admin_navigation import AdminNavigation
from .configurator_utils import ConfiguratorUtils
from app.utilites.utilites import Utilites

from .decorators import requires_auth

WEB_MOD_NAME = 'portal_configurator'
mod = Blueprint(WEB_MOD_NAME, __name__, url_prefix=AdminConf.MOD_WEB_ROOT+'/' + WEB_MOD_NAME.split('_')[1],
                static_folder=AdminConf.get_web_static_path(),
                template_folder=AdminConf.get_web_tpl_path())

mod.add_app_template_global(os.path.join(AdminConf.MOD_NAME, 'portal', ''), name='_tpl_path')


@mod.route('/configs', defaults={'config_name': ''}, methods=['GET'], strict_slashes=False)
@mod.route('/configs/<config_name>', methods=['GET'], strict_slashes=False)
@requires_auth
def edit_settings_view(config_name):
    """
    Функция создает страницу редактирования ini файла
    :param config_name: имя ini файла из директории data/cfg в директории модуля
    :return: сформированный шаблон страницы
    """
    tmpl_vars = {}
    tmpl_vars['title'] = 'Административный интерфейс'
    tmpl_vars['page_title'] = 'Конфигурационный файл: ' + config_name
    tmpl_vars['page_side_title'] = 'Содержание раздела'

    tmpl_vars['navi'] = _get_configurator_navi()
    tmpl_vars['edit_name'] = config_name
    tmpl_vars['is_default'] = ConfiguratorUtils.is_default_conf(config_name)
    _base_url = mod.url_prefix
    _app_url_prefix = app_api.get_app_url_prefix()
    if _app_url_prefix and not _base_url.startswith(_app_url_prefix):
        _base_url = _app_url_prefix.rstrip('/') + '/' + _base_url.lstrip('/')
    tmpl_vars['base_url'] = _base_url
    tmpl_vars['js_base_url'] = _base_url

    data_file = ConfiguratorUtils.get_conf_file(config_name)
    if os.path.exists(data_file):
        editor = Utilites.get_file_editor()
        # превращаем словарь в HTML
        edit_data = editor.ini2dict(data_file)
        # первичные ключи это секции - Вопрос где хранить натменование секций????
        # вторичные ключи - имена полей
        tmpl_vars['edit_data'] = edit_data
        mod_path = AdminConf.SELF_PATH
        tmpl_vars['source_name'] = data_file.replace(mod_path, '')
        tmpl_vars['mod_name'] = AdminConf.MOD_NAME
        _tpl_name = os.path.join(AdminConf.MOD_NAME, 'portal', 'config_creator.html')
    return editor.render_page(_tpl_name, tmpl_vars)


def _get_configurator_navi():
    lst = []
    conf_list = ConfiguratorUtils.get_configurator_navi()
    for ci in conf_list:
        tpl = AdminNavigation.get_link_tpl()
        tpl['label'] = ci['label']
        tpl['href'] = _cook_conf_link(ci['href'])
        tpl['roles'] = ci['roles']
        tpl['code'] = 'Config_' + ci['code']
        lst.append(tpl)
    return lst


def _cook_conf_link(conf_name):
    lnk = url_for(ConfiguratorUtils.get_webeditor_endpoint(), config_name=conf_name)
    return lnk

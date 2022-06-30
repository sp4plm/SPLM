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

""""""
# @mod.route('/configs/section/tpl')
# def get_section_tpl():
#     _tpl_name = os.path.join(AdminConf.MOD_NAME, 'portal', 'config_section.html')
#     return app_api.render_page(_tpl_name)
#
#
# @mod.route('/configs/param/tpl')
# def get_param_tpl():
#     _tpl_name = os.path.join(AdminConf.MOD_NAME, 'portal', 'config_param.html')
#     return app_api.render_page(_tpl_name)
#
#
# @mod.route('/configs/<conf_name>/save', methods=['POST'])
# def save_config(conf_name):
#     answer = {'Msg': 'Ошибка при выполнении', 'Data': None, 'State': 404}
#
#     origin_file = ConfiguratorUtils.get_conf_file(conf_name)
#     # разбираем данные пришедшие от клиента
#     form_dict = request.form.to_dict(flat=False)
#     _t =  {}
#     for item in form_dict:
#         _parsed_key = _parse_form_key(item)
#         _l = {}
#         for k in _parsed_key[::-1]:
#             if k == _parsed_key[-1]:
#                 _l[k] = form_dict[item][0]
#             else:
#                 _t1 = {**_l}
#                 _l = {}
#                 _l[k] = {**_t1}
#         _t = _dict_sum(_t, _l)
#     form_dict = _t
#
#     edit_name = ''
#     field = 'ConfigName'
#     if field in form_dict and form_dict[field]:
#         edit_name = form_dict[field]
#     origin_name = ''
#     field = 'ConfigOrigin'
#     if field in form_dict and form_dict[field]:
#         origin_name = form_dict[field]
#     new_content = ''
#     field = 'ConfContent'
#     if field in form_dict and form_dict[field]:
#         new_content = form_dict[field]
#
#     flg = False
#     answer['Msg'] = 'Отсутствует конфигурационный файл с именем "{}"!' . format(conf_name)
#     if os.path.exists(origin_file):
#         answer['Msg'] = 'Не удалось сохранить новое содержимое файла конфигурации "{}"!' . format(conf_name)
#         flg = AdminUtils.dict2ini(origin_file, new_content)
#
#     if flg:
#         answer['State'] = 200
#         answer['Msg'] = ''
#
#     return json.dumps(answer)
#
#
# def _parse_form_key(str_path):
#     _pth = []
#     if _count_symbols(str_path, '[') == _count_symbols(str_path, ']'):
#         _t = str_path.split('[')
#         for k in _t:
#             k = k.rstrip(']')
#             _pth.append(k)
#     else:
#         _pth.append(str_path)
#     return _pth
#
#
# def _dict_sum(d1, d2):
#     for key2, val2 in d2.items():
#         if key2 not in d1:
#             d1[key2] = val2
#         else:
#             if type(d1[key2]) != type(val2):
#                 d1[key2] = val2
#             else:
#                 if isinstance(val2, list):
#                     d1[key2] = list(set(d1[key2] + val2))
#                 elif isinstance(val2, dict):
#                     d1[key2] = _dict_sum(d1[key2], val2)
#                 else:
#                     d1[key2] = val2
#     return d1
#
#
# def _count_symbols(source, target):
#     summ = 0
#     summ = sum(map(lambda x: 1 if target in x else 0, source))
#     return summ


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

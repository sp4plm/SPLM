# -*- coding: utf-8 -*-
"""
Модуль предоставляет форму редактирования данных представленных в виде ключ-значение
"""
import os
import json
from flask import Blueprint, render_template, request

from app import app_api

from .mod_api import ModApi

mod = Blueprint(ModApi.MOD_NAME, __name__, url_prefix=ModApi.MOD_WEB_ROOT,
                static_folder=ModApi.get_web_static_path(),
                template_folder=ModApi.get_web_tpl_path())

_auth_decorator = app_api.get_auth_decorator()


@mod.route('/<conf_name>/remove', methods=['POST'])
@_auth_decorator
def remove_config(conf_name):
    answer = {'Msg': 'Ошибка при выполнении', 'Data': None, 'State': 404}

    _mod_api = ModApi()
    form_dict = request.form.to_dict(flat=True)
    work_mod = ''
    relative = ''
    field = 'MOD_NAME'
    if field in form_dict and form_dict[field]:
        work_mod = form_dict[field]
    else:
        answer['Msg'] = 'Неизвестный модуль файла'
    field = 'SOURCE_NAME'
    if field in form_dict and form_dict[field]:
        relative = form_dict[field]
    else:
        answer['Msg'] = 'Неизвестный файл'

    answer['Msg'] = 'Неудалось удалить файл ' + os.path.basename(relative)
    remove_flg = False
    remove_flg = _mod_api.remove_file(work_mod, relative)
    if remove_flg:
        answer['Msg'] = 'Файл {} успешно удален'. format(os.path.basename(relative))
        answer['State'] = 200
    return json.dumps(answer)


@mod.route('/<conf_name>/save', methods=['POST'])
@_auth_decorator
def save_config(conf_name):
    answer = {'Msg': 'Ошибка при выполнении', 'Data': None, 'State': 404}

    _mod_api = ModApi()

    origin_file = ''
    # разбираем данные пришедшие от клиента
    form_dict = request.form.to_dict(flat=False)
    form_dict = __normalize_recive_form(form_dict)

    edit_name = ''
    field = 'ConfigName'
    if field in form_dict and form_dict[field]:
        edit_name = form_dict[field]
    origin_name = ''
    field = 'ConfigOrigin'
    if field in form_dict and form_dict[field]:
        origin_name = form_dict[field]
    new_content = ''
    field = 'ConfContent'
    if field in form_dict and form_dict[field]:
        new_content = form_dict[field]

    work_mod = ''
    relative = ''
    field = 'MOD_NAME'
    if field in form_dict and form_dict[field]:
        work_mod = form_dict[field]
    field = 'SOURCE_NAME'
    if field in form_dict and form_dict[field]:
        relative = form_dict[field]

    _root_path = _mod_api.get_app_path()
    _app_conf_pth = app_api.get_app_cfg_path()
    _app_data_pth = app_api.get_app_data_path()
    if relative.startswith(_app_conf_pth) or relative.startswith(_app_data_pth):
        # получается мы работаем с файлом который только в конфиге или в данных вне модуля
        answer['Msg'] = 'Не удалось сохранить новое содержимое файла конфигурации "{}"!'.format(conf_name)
        # print(mod.name + '.views.save_config->relative ', relative)
        if not os.path.exists(relative):
            pass
        flg = _mod_api.dict2ini(relative, new_content)
        # print(mod.name + '.views.save_config->save flg ', flg)
    else:

        if '' != relative and ''!=work_mod:
            relative = relative.lstrip(os.path.sep).replace(work_mod, '')

        origin_file = os.path.join(_root_path, work_mod, relative.lstrip(os.path.sep))
        # print(mod.name + '.views.save_config->origin_file: ', origin_file)
        flg = False
        answer['Msg'] = 'Отсутствует конфигурационный файл с именем "{}"!' . format(conf_name)
        if os.path.exists(origin_file):
            answer['Msg'] = 'Не удалось сохранить новое содержимое файла конфигурации "{}"!' . format(conf_name)
            flg = _mod_api.dict2ini(origin_file, new_content)

    if flg:
        answer['State'] = 200
        answer['Msg'] = ''

    return json.dumps(answer)


@mod.route('/section/tpl')
@_auth_decorator
def get_section_tpl():
    _tpl_name = os.path.join(ModApi.MOD_NAME, 'portal', 'config_section.html')
    return render_template(_tpl_name)


@mod.route('/param/tpl')
@_auth_decorator
def get_param_tpl():
    _tpl_name = os.path.join(ModApi.MOD_NAME, 'portal', 'config_param.html')
    return render_template(_tpl_name)


def __normalize_recive_form(form_dict):
    _t = {}
    for item in form_dict:
        _parsed_key = __parse_form_key(item)
        _l = {}
        for k in _parsed_key[::-1]:
            if k == _parsed_key[-1]:
                _l[k] = form_dict[item][0]
            else:
                _t1 = {**_l}
                _l = {}
                _l[k] = {**_t1}
        _t = __dict_sum(_t, _l)
    return _t


def __parse_form_key(str_path):
    _pth = []
    if __count_symbols(str_path, '[') == __count_symbols(str_path, ']'):
        _t = str_path.split('[')
        for k in _t:
            k = k.rstrip(']')
            _pth.append(k)
    else:
        _pth.append(str_path)
    return _pth


def __dict_sum(d1, d2):
    for key2, val2 in d2.items():
        if key2 not in d1:
            d1[key2] = val2
        else:
            if type(d1[key2]) != type(val2):
                d1[key2] = val2
            else:
                if isinstance(val2, list):
                    d1[key2] = list(set(d1[key2] + val2))
                elif isinstance(val2, dict):
                    d1[key2] = __dict_sum(d1[key2], val2)
                else:
                    d1[key2] = val2
    return d1


def __count_symbols(source, target):
    summ = 0
    summ = sum(map(lambda x: 1 if target in x else 0, source))
    return summ

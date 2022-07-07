# -*- coding: utf-8 -*-

"""
Модуль управления темами проекта
Flask Themes2 в файле описания темы info.json  могут находиться только символы из ASCII, так как класс Theme читает
данный файл в конструкторе без указания кодировки
"""

import os
import json
import shutil
from math import ceil

from flask import Blueprint, request, g, redirect, url_for, current_app

from app.utilites.jqgrid_helper import JQGridHelper

from app import app_api
from .mod_utils import ModUtils

_mod_utils = ModUtils()

mod = Blueprint(_mod_utils.MOD_NAME, __name__, url_prefix=_mod_utils.MOD_WEB_ROOT,
                static_folder=_mod_utils.get_web_static_path(),
                template_folder=_mod_utils.get_web_tpl_path())

# _admin_mod_api = None
# _admin_mod_api = app_api.get_mod_api('admin_mgt')
_auth_decorator = app_api.get_auth_decorator()


@mod.route('/reset', methods=['GET'])
@_auth_decorator
def __update_defaults():
    """
    Удаляет предустановленные темы и копирует их из директории модуля как при инсталляции
    :return:
    """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['Msg'] = 'Отсутствуют данные для выполнения операций!'
    _mod_utils = ModUtils()

    flg = _mod_utils.reset_to_defaults()
    if flg:
        answer['Msg'] = 'Предустановленные темы обновлены!'
        answer['State'] = 200
        _themes_mg = _mod_utils.get_manager()
        _themes_mg.refresh()
    else:
        answer['Msg'] = 'Не удалось произвести перенастройку пердустановленных тем!'
    return json.dumps(answer)


@mod.route('/theme/upload', methods=['POST'])
@_auth_decorator
def __upload_new():
    """
    Загружает архив новой темы. Архив должен содержать одну директорию, называющуюся именем новой темы.
    :return: json object
    """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    args = {"method": "POST"}
    if request.method == "POST":
        _mod_utils = ModUtils()
        MAX_FILE_SIZE = _mod_utils.get_max_filesize()
        appended = []
        # answer = {'Status': 500, 'msg': 'No files to save!'}
        answer['Msg'] = 'Нет файлов для сохранения.'
        if request.files and 'File' in request.files:
            file = None # type: werkzeug.datastructures.FileStorage
            errors = []
            # print(request.files.getlist('File'))
            for file in request.files.getlist('File'):
                if bool(file.filename):
                    file_bytes = file.read(MAX_FILE_SIZE)
                    args["file_size_error"] = len(file_bytes) == MAX_FILE_SIZE
                    # сохранялись пустые файлы
                    # решение:
                    # https://stackoverflow.com/questions/28438141/python-flask-upload-file-but-do-not-save-and-use
                    # # snippet to read code below
                    file.stream.seek(0)  # seek to the beginning of file
                    answer['Msg'] = 'Не удалось загрузить тему: {}.'.format(file.filename)
                    try:
                        # теперь требуется сохранить файл архива в директорию данных
                        new_theme_path = _mod_utils.save_uploaded_file(file)
                        # print('new_theme_path', new_theme_path)
                        add_flg = _mod_utils.add_new(new_theme_path)
                        if add_flg:
                            answer['Msg'] = ''
                            answer['State'] = 200
                            _themes_mg = _mod_utils.get_manager()
                            _themes_mg.refresh()
                        os.unlink(new_theme_path) # в любом случае удаляем загрудженый файл
                    except Exception as ex:
                        answer['Msg'] = 'Не удалось загрузить тему: {}. Ошибка: {}'.format(file.filename, ex)
                        errors.append('Не удалось загрузить тему: {}. Ошибка: {}'.format(file.filename, ex))
    return json.dumps(answer)


@mod.route('/theme/remove', methods=['POST'])
@_auth_decorator
def __remove_theme():
    """
    Удаляет выбранную тему. Предустановленные темы удалить нельзя. Текущую тему удалить нельзя.
    :return: json object
    """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['Msg'] = 'Отсутствуют данные для выполнения операций!'
    if request.method == "POST":
        _mod_utils = ModUtils()
        name = request.form['ThemeName'].strip() if 'ThemeName' in request.form else ''
        # проверяем наличие темы с именем
        _available = _mod_utils.get_list()
        answer['Msg'] = 'Не известная тема "{}"!'.format(name)
        if name in _available:
            # получаем идентификатор темы
            _theme_path = _mod_utils.get_path_by_name(name)
            _current_theme = app_api.get_current_theme()
            answer['Msg'] = 'Нельзя удалить, используемую порталом, тему!'
            if _current_theme != os.path.basename(_theme_path):
                shutil.rmtree(_theme_path, ignore_errors=True)
                flg = not os.path.exists(_theme_path)
                if flg:
                    answer['Msg'] = 'Тема "{}" успешно удалена!'.format(name)
                    answer['State'] = 200
                    _themes_mg = _mod_utils.get_manager()
                    _themes_mg.refresh()
                else:
                    answer['Msg'] = 'Не удалось сменить текущую тему портала на"{}"!'.format(name)
    return json.dumps(answer)


@mod.route('/theme/set', methods=['POST'])
@_auth_decorator
def __set_portal_theme():
    """
    Назначает в настройках выбранную тему
    :return: json object
    """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['Msg'] = 'Отсутствуют данные для выполнения операций!'
    if request.method == "POST":
        _mod_utils = ModUtils()
        name = request.form['ThemeName'].strip() if 'ThemeName' in request.form else ''
        # проверяем наличие темы с именем
        _available = _mod_utils.get_list()
        answer['Msg'] = 'Не известная тема "{}"!' .format(name)
        answer['State'] = 500
        if name in _available:
            # получаем идентификатор темы
            _theme_id = _mod_utils.get_id_by_name(name)
            _admin_mod_api = app_api.get_mod_api('admin_mgt')
            # сохраняем новую настройку
            flg = _admin_mod_api.set_portal_theme(_theme_id)
            if flg:
                answer['Msg'] = 'Текущая тема портала успешно изменена на "{}"!'.format(name)
                answer['State'] = 200
                _themes_mg = _mod_utils.get_manager()
                _themes_mg.refresh()
            else:
                answer['Msg'] = 'Не удалось сменить текущую тему портала на "{}"!'.format(name)
    return json.dumps(answer)


@mod.route('/list', methods=['POST'])
@_auth_decorator
def __get_list():
    """
    Возвращает список тем портала для таблицы jqGrid  с учетом сортировки и поиска
    :return: json object
    """
    answer = {'rows': [], 'page': 1, 'records': 20, 'total': 1}
    page = 1  # get the requested page
    limit = 20  # get how many rows we want to have into the grid
    sidx = 'Name'  # get index row - i.e. user click to sort
    sord = 'asc'  # get the direction
    search_flag = False
    filters = ''

    if request.method == "GET":
        page = int(request.args['page']) if 'page' in request.args else page
        limit = int(request.args['rows']) if 'rows' in request.args else limit
        sidx = request.args['sidx'] if 'sidx' in request.args else sidx
        sord = request.args['sord'] if 'sord' in request.args else sord
        if '_search' in request.args:
            search_flag = not ('false' == request.args['_search']) # инверсия от значения
        filters = request.args['filters'] if 'filters' in request.args else filters

    if request.method == "POST":
        page = int(request.form['page']) if 'page' in request.form else page
        limit = int(request.form['rows']) if 'rows' in request.form else limit
        sidx = request.form['sidx'] if 'sidx' in request.form else sidx
        sord = request.form['sord'] if 'sord' in request.form else sord
        if '_search' in request.form:
            search_flag = not ('false' == request.form['_search']) # инверсия от значения
        filters = request.form['filters'] if 'filters' in request.form else filters

    offset = 0 if 1==page else (page-1)*limit
    _mod_utils = ModUtils()
    _themes_mg = _mod_utils.get_manager()
    _current_theme = app_api.get_current_theme()

    rows = []
    _defaults = []
    _defaults = _mod_utils.get_default_list()
    for _theme in _themes_mg.list_themes():
        row = {'Toolbar': '', 'Enabled': 'Нет', 'Name': '', 'Description':'', 'IsDefault':''}
        row['id'] = _theme.identifier
        row['Name'] = _theme.name
        row['Description'] = _theme.description
        if _theme.identifier == _current_theme:
            row['Enabled'] = 'Да'
        if _theme.identifier in _defaults:
            row['IsDefault'] = 'Да'
        rows.append(row)

    if 1 < len(rows):
        rows = __sort_files(rows, sord, sidx)

    answer['page'] = page
    answer['records'] = len(rows)
    answer['total'] = ceil(answer['records'] / limit)
    answer['rows'] = rows[offset:offset + limit] if len(rows) > limit else rows
    return json.dumps(answer)


def __sort_files(file_list, ord='asc', attr='name'):
    sort_result = []
    sort_result = file_list
    revers = True if 'asc' != ord else False
    sort_result = sorted(sort_result, key=lambda x: x[attr], reverse=revers)
    return sort_result


@mod.route('', methods=['GET'])
@_auth_decorator
def __index():
    """
    Отображение списка(реестра) тем портала ввиде таблицы в административном интерфейсе
    :return: html page
    """
    _mod_utils = ModUtils()
    _themes_mg = _mod_utils.get_manager()
    _tmpl_vars = {}
    _tmpl_vars['page_title'] = 'Управление темами проекта'

    _tmpl_vars['base_url'] = _mod_utils.MOD_WEB_ROOT
    _base_tbl = JQGridHelper.get_jqgrid_config()
    # теперь надо добавить состав колонок
    _base_tbl['colModel'] = _mod_utils.get_view_table_columns()
    _base_tbl['url'] = url_for(_mod_utils.MOD_NAME +'.__get_list')
    _tmpl_vars['themes_tbl'] = json.dumps(_base_tbl)
    _tpl_name = os.path.join(_mod_utils.MOD_NAME, 'manage.html')
    return app_api.render_page(_tpl_name, **_tmpl_vars)

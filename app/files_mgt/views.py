# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса управления файлами
"""
import os
import json
from math import ceil

from flask import Blueprint, request, render_template
from .mod_utils import app_api, ModConf, ModUtils
from .data_files import DataFiles

mod = Blueprint(ModConf.MOD_NAME, __name__, url_prefix=ModConf.MOD_WEB_ROOT,
                static_folder=ModConf.get_web_static_path(),
                template_folder=ModConf.get_web_tpl_path())

_admin_mod_api = None
_admin_mod_api = app_api.get_mod_api('admin_mgt')
_auth_decorator = app_api.get_auth_decorator()
_mod_utils = None
_mod_utils = ModUtils()

mod.add_app_template_global(_mod_utils.get_jslib_jstree_vers, name='jstree_vers')
mod.add_app_template_global(_mod_utils.get_jslib_jqGrid_vers, name='jqgrid_vers')


@mod.route('/', methods=['GET', 'POST'])
@_auth_decorator
def files_management():
    portal_cfg = app_api.get_app_config()
    return render_template("/media_files.html", title="Управление файлами",
                           page_title="Управление файлами")


@mod.route('/getStructTree', methods=['GET', 'POST'])
@_auth_decorator
def files_struct_tree():
    answer = {'msg': '', 'data': None, 'state': 404}
    df = DataFiles()
    answer = df.get_struct_tree()
    return json.dumps(answer)


@mod.route('/getDirSource', methods=['GET', 'POST'])
@mod.route('/getDirSource/', methods=['GET', 'POST'])
@mod.route('/getDirSource/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def get_dir_source(dir_name=''):
    answer = {'rows': [], 'page': 1, 'records': 20, 'total': 1}
    page = 1 # get the requested page
    limit = 20 # get how many rows we want to have into the grid
    sidx = 'Name' # get index row - i.e. user click to sort
    sord = 'asc' # get the direction
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

    df = DataFiles()
    file_list = []
    if search_flag:
        """ сперва будем искать """
        file_list = df.search_items(dir_name, filters)
    else:
        """ просто выбираем все """
        file_list = df.get_dir_source(dir_name)

    # answer = df.get_dir_source(dir_name, page, limit, sidx, sord, search_flag, filters)

    """ теперь после поиска надо отсортировать """
    file_list = df.sort_files(file_list, sord)

    rows = []
    for item in file_list:
        row = {'Toolbar': '', 'Type': '', 'Name': '', 'Path': ''}
        file_name = item.name.decode('utf-8', 'unicode_escape')
        row['Name'] = file_name
        row['Path'] = os.path.join(df.get_relative_path(dir_name), file_name).replace('$', '/')
        row['Type'] = 'f'
        if item.is_dir():
            row['Type'] = 'd'
        rows.append(row)

    answer['page'] = page
    answer['records'] = len(rows)
    answer['total'] = ceil(answer['records'] / limit)
    answer['rows'] = rows[offset:offset + limit] if len(rows) > limit else rows
    return json.dumps(answer)


@mod.route('/saveDirectory', methods=['GET', 'POST'])
@_auth_decorator
def save_directory():
    answer = {'Msg': '', 'data': None, 'State': 500}
    if request.method == 'POST':
        base = request.form['base'].strip() if 'base' in request.form else ''
        dirname = request.form['directory'].strip() if 'directory' in request.form else ''
        df = DataFiles()
        if df.save_directory(dirname, base):
            answer['State'] = 200
            answer['Msg'] = ''
            answer['Data'] = {'directory': dirname}
    return json.dumps(answer)


@mod.route('/renameDirectory', methods=['GET', 'POST'])
@_auth_decorator
def rename_directory():
    answer = {'msg': '', 'data': None, 'state': 500}
    if request.method == 'POST':
        base = request.form['base'].strip() if 'base' in request.form else ''
        dirname = request.form['directory'].strip() if 'directory' in request.form else ''
        new_name = request.form['newName'].strip() if 'newName' in request.form else ''
        df = DataFiles()
        if df.rename_directory(dirname, new_name, base):
            answer['State'] = 200
            answer['Msg'] = ''
            answer['Data'] = {'directory': new_name}
    return json.dumps(answer)


@mod.route('/removeDirectory', methods=['GET', 'POST'])
@_auth_decorator
def remove_directory():
    answer = {'msg': '', 'data': None, 'state': 500}
    if request.method == 'POST':
        base = request.form['base'].strip() if 'base' in request.form else ''
        dirname = request.form['directory'].strip() if 'directory' in request.form else ''
        df = DataFiles()
        if df.remove_directory(dirname, base):
            answer['State'] = 200
            answer['Msg'] = ''
            answer['Data'] = {'directory': dirname}
    return json.dumps(answer)


@mod.route('/uploadFiles', methods=['GET', 'POST'])
@mod.route('/uploadFiles/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def upload_files(dir_name=None):
    answer = {'Msg': '', 'Data': None, 'State': 404}
    args = {"method": "POST"}
    if request.method == "POST":
        MAX_FILE_SIZE = _mod_utils.get_max_filesize()
        appended = []
        # answer = {'Status': 500, 'msg': 'No files to save!'}
        answer['Msg'] = 'Нет файлов для сохранения.'
        if request.files and 'File[]' in request.files:
            file = None # type: werkzeug.datastructures.FileStorage
            df = DataFiles()
            errors = []
            # print(request.files.getlist('File[]'))
            for file in request.files.getlist('File[]'):
                if bool(file.filename):
                    file_bytes = file.read(MAX_FILE_SIZE)
                    args["file_size_error"] = len(file_bytes) == MAX_FILE_SIZE
                    # сохранялись пустые файлы
                    # решение:
                    # https://stackoverflow.com/questions/28438141/python-flask-upload-file-but-do-not-save-and-use
                    # # snippet to read code below
                    file.stream.seek(0)  # seek to the beginning of file
                    try:
                        df.save_uploaded_file(file, dir_name)
                        answer['Msg'] = ''
                        answer['State'] = 200
                    except Exception as ex:
                        answer['Msg'] = 'Cann`t upload file: {}. Error: {}'.format(file.filename, ex)
                        errors.append('Cann`t upload file: {}. Error: {}'.format(file.filename, ex))
    return json.dumps(answer)


@mod.route('/editFile', methods=['GET', 'POST'])
@mod.route('/editFile/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def edit_file(dir_name=None):
    answer = {'Msg': '', 'Data': None, 'State': 404}
    if request.method == 'POST':
        _mod_utils = ModUtils()
        MAX_FILE_SIZE = _mod_utils.get_max_filesize()
        oname = request.form['OldName'].strip() if 'OldName' in request.form else ''
        new_name = request.form['FileName'].strip() if 'FileName' in request.form else ''
        df = DataFiles()
        file = None
        if request.files and 'File' in request.files:
            file = request.files['File']
            if bool(file.filename):
                file_bytes = file.read(MAX_FILE_SIZE)
                if len(file_bytes) >= MAX_FILE_SIZE:
                    answer['Msg'] = 'File size error! (Max Size: {})'.format(MAX_FILE_SIZE)
                    answer['State'] = 400
                    file = None
            else:
                answer['Msg'] = 'File name error: undefined uploaded file!'
                answer['State'] = 400
                file = None
        try:
            flg = df.edit_file(oname, new_name, file, dir_name)
            if flg:
                answer['Msg'] = ''
                answer['State'] = 200
                print_name = new_name if ''!=new_name and new_name!=oname else oname
                answer['Data'] = {'file': print_name}
        except Exception as ex:
            answer['Msg'] = str(ex)
            answer['State'] = 400
            answer['Data'] = {}
    return json.dumps(answer)


@mod.route('/removeFile', methods=['GET', 'POST'])
@mod.route('/removeFile/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def remove_file(dir_name=None):
    answer = {'msg': '', 'data': None, 'state': 404}
    if request.method == "POST":
        name = request.form['file'].strip() if 'file' in request.form else ''
        if '' != name:
            df = DataFiles()
            if df.remove_file(name, dir_name):
                answer['State'] = 200
                answer['Msg'] = ''
                answer['Data'] = {'file': name}
    return json.dumps(answer)


@mod.route('/removeSelection', methods=['GET', 'POST'])
@mod.route('/removeSelection/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def remove_selection(dir_name=None):
    answer = {'Msg': '', 'Data': None, 'State': 404}
    result = None
    if request.method == "POST":
        form_dict = request.form.to_dict(flat=False)
        items = form_dict['items[]'] if 'items[]' in form_dict else []
        if items:
            df = DataFiles()
            result = df.remove_selected_items(items, dir_name)
    if result and 0 < len(result['deleted']):
        answer['State'] = 200
        answer['Msg'] = '' if len(result['deleted']) == len(result['all']) else 'Не все данные были удалены!'
        answer['Data'] = result
    else:
        answer['Msg'] = 'Не удалось удалить данные!'
    return json.dumps(answer)

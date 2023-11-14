# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса управления файлами
"""
import os
from sys import platform
import json
from math import ceil

from flask import Blueprint, request, url_for, redirect, send_from_directory
from .mod_utils import app_api, ModConf, ModUtils
from .data_files import DataFiles
from app.utilites.portal_navi import PortalNavi

mod = Blueprint(ModConf.MOD_NAME, __name__, url_prefix='',
                static_folder=ModConf.get_web_static_path(),
                static_url_path=ModConf.MOD_WEB_ROOT + '/static',
                template_folder=ModConf.get_web_tpl_path())

_admin_mod_api = None
_admin_mod_api = app_api.get_mod_api('admin_mgt')
_auth_decorator = app_api.get_auth_decorator()
_mod_utils = None
_mod_utils = ModUtils()

# выносим префикс для обработки перенаправлений старых файлов из данных
__web_prefix = ModConf.MOD_WEB_ROOT

mod.add_app_template_global(_mod_utils.get_jslib_jstree_vers, name='jstree_vers')
mod.add_app_template_global(_mod_utils.get_jslib_jqGrid_vers, name='jqgrid_vers')

"""
send_from_directory
 требуется переделать хранение загружаемых пользователем файлов в app.config['UPLOAD_PATH'] 
 вместо static/files
"""

# инициализация модуля
__mod_path = app_api.get_mod_data_path(ModConf.MOD_NAME)
if not os.path.exists(__mod_path):
    try: os.mkdir(__mod_path)
    except: pass
# теперь добавим симлинку внутри себя
_files_lnk = os.path.join(_mod_utils.get_web_static_path(), 'files')
if not os.path.exists(_files_lnk):
    if "win32" == platform:
        import ctypes
        try:
            _kdll = ctypes.windll.LoadLibrary("kernel32.dll")
            _kdll.CreateSymbolicLinkA(_files_lnk, __mod_path, 1)
        except: pass
    else:
        try: os.symlink(__mod_path, _files_lnk, True)
        except: pass


# теперь нужно обработать перенаправление
# TODO: создать механизм определения перенаправления ???
@mod.route('/opendata/f/<path:file_path>', strict_slashes=False)
@mod.route('/static/files/<path:file_path>', strict_slashes=False)
@_auth_decorator
def view_ufile(file_path=''):
    _2fs_file = file_path.replace('/', os.path.sep)
    _fs_relative = os.path.join('files', file_path.lstrip(os.path.sep))
    # в первуюю очередь просматриваем пользовательскую директорию
    if not os.path.exists(_files_lnk):
        # print(" no symlink in blueprint static for user data file")
        _check_file = os.path.join(__mod_path, _2fs_file.lstrip(os.path.sep))
        if os.path.exists(_check_file):
            return send_from_directory(__mod_path, file_path)
    _relative = os.path.join('files', file_path.lstrip(os.path.sep))
    if "win32" == platform:
        _relative = _relative.replace('\\', '/')
    # print(ModConf.MOD_NAME + '.__view_loaded->_relative:', _relative)
    __go_to = url_for(ModConf.MOD_NAME + '.static', filename=_relative)
    # print(ModConf.MOD_NAME + '.__view_loaded->__go_to:', __go_to)
    return redirect(__go_to)


@mod.route(__web_prefix, methods=['GET', 'POST'], strict_slashes=False)
@_auth_decorator
def files_management():
    portal_cfg = app_api.get_app_config()
    _tpl_name = os.path.join(ModConf.MOD_NAME, 'media_files.html')
    _base_url = __web_prefix
    _app_url_prefix = app_api.get_app_url_prefix()
    if _app_url_prefix and not _base_url.startswith(_app_url_prefix):
        _base_url = _app_url_prefix.rstrip('/') + '/' + _base_url.lstrip('/')
    return app_api.render_page(_tpl_name, title="Управление файлами",
                           page_title="Управление файлами",
                        base_url=_base_url)


@mod.route(__web_prefix + '/getStructTree', methods=['GET', 'POST'])
@_auth_decorator
def files_struct_tree():
    answer = {'msg': '', 'data': None, 'state': 404}
    df = DataFiles()
    answer = df.get_struct_tree()
    return json.dumps(answer)


@mod.route(__web_prefix + '/getDirSource', methods=['GET', 'POST'])
@mod.route(__web_prefix + '/getDirSource/', methods=['GET', 'POST'])
@mod.route(__web_prefix + '/getDirSource/<dir_name>', methods=['GET', 'POST'])
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


@mod.route(__web_prefix + '/saveDirectory', methods=['GET', 'POST'])
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


@mod.route(__web_prefix + '/renameDirectory', methods=['GET', 'POST'])
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


@mod.route(__web_prefix + '/removeDirectory', methods=['GET', 'POST'])
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


@mod.route(__web_prefix + '/uploadFiles', methods=['GET', 'POST'])
@mod.route(__web_prefix + '/uploadFiles/<dir_name>', methods=['GET', 'POST'])
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


@mod.route(__web_prefix + '/editFile', methods=['GET', 'POST'])
@mod.route(__web_prefix + '/editFile/<dir_name>', methods=['GET', 'POST'])
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


@mod.route(__web_prefix + '/removeFile', methods=['GET', 'POST'])
@mod.route(__web_prefix + '/removeFile/<dir_name>', methods=['GET', 'POST'])
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


@mod.route(__web_prefix + '/removeSelection', methods=['GET', 'POST'])
@mod.route(__web_prefix + '/removeSelection/<dir_name>', methods=['GET', 'POST'])
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


@mod.route(__web_prefix + '/view', methods=['GET'], defaults={'relative':''})
@mod.route(__web_prefix + '/view/<path:relative>', methods=['GET'], strict_slashes=False)
def dir_view(relative=''):
    """
    Функция отображает содержимое одной директории relative, включая первый уровень поддиректорий, а именно: сперва
    отображаются файлы директории relative, а потом список поддиректорий с их файлами.
    :param relative: имя директории для отображения содержимого
    :return: HTML Template
    """


    portal_cfg = app_api.get_app_config()
    _tpl_name = os.path.join(ModConf.MOD_NAME, 'dir_view.html')
    _tpl_vars = {}
    _page_label = 'Содержимое директории'
    _tpl_vars['dir_source'] = None
    _tpl_vars['dir_source'] = {'files':[], 'dirs':{}}

    relative = relative.strip(os.path.sep)
    _page_label += ' ' + relative
    #  считаем что директория  относительно корня директории данных
    _files_ctrl = DataFiles()
    _rel_start = relative

    if not os.path.exists(_files_ctrl.get_dir_path(relative)):
        return app_api.render_page(os.path.join('errors', '404.html'), message='Неизвестная директория!')

    _src = _files_ctrl.get_dir_source(_rel_start)
    _start = _files_ctrl.get_dir_path(_rel_start)
    if _src:
        _files_list = []
        _dirs_list = {}
        for _i in _src:
            _item = _i.name.decode('utf-8')
            _t = os.path.join(_start, _item)
            _t_rel = os.path.join(_rel_start, _item)
            if os.path.isfile(_t.encode('utf-8')):
                _files_list.append(_t)
                pass
            if os.path.isdir(_t.encode('utf-8')):
                _cd = _t
                _cd_src = _files_ctrl.get_dir_source(_t_rel)
                _dirs_list[_t] = [os.path.join(_t_rel, _i2.name.decode('utf-8')) for _i2 in _cd_src]
                pass
        if _files_list:
            for _fi in _files_list:
                _a = __cook_file_link(_fi)
                _tpl_vars['dir_source']['files'].append(_a)

        if _dirs_list:
            _t_dirs = _dirs_list.keys()
            for _dn in _t_dirs:
                _t_name = os.path.basename(_dn)
                _t_lst = [__cook_file_link(_df) for _df in _dirs_list[_dn]]
                _tpl_vars['dir_source']['dirs'][_t_name] = _t_lst
                pass

    # предполагаем что возможно данную ссылку вставили в навигацию
    # значит заголовок страницы должен соответствовать
    _cur_navi = None
    try:
        _cur_navi = PortalNavi.get_current_navi_item()
        if _cur_navi is not None:
            if 'label' in _cur_navi:
                _page_label = _cur_navi['label']
    except Exception as ex:
        print(ModConf.MOD_NAME + '.views.dir_view -> get_current_navi.Exception: ' + str(ex))

    _tpl_vars['title'] = _page_label
    _tpl_vars['page_title'] = _page_label
    return app_api.render_page(_tpl_name, **_tpl_vars)


def __cook_file_link(file_path, str_res=False):
    _files_ctrl = DataFiles()
    # print('__cook_file_link->file_path', file_path)
    _d_url = url_for(ModConf.MOD_NAME + '.download_file', relative=_files_ctrl.get_relative_path(file_path))
    if str_res:
        _a = '<a href="' + _d_url + '" target="_blank">' + os.path.basename(file_path) + '</a>'
    else:
        _a = {'href': _d_url, 'label': os.path.basename(file_path)}
    return _a


@mod.route(__web_prefix + '/download/<path:relative>', methods=['GET'])
def download_file(relative):
    _files_ctrl = DataFiles()
    _root = _files_ctrl.get_dir_path(None)
    download_file = os.path.join(_root, relative)
    errorMsg='Файл не найден: ' + relative
    if os.path.exists(download_file.encode('utf-8')):
        if os.path.isdir(download_file.encode('utf-8')):
            # заготовка для скачивания директории одним архивом
            pass
        from flask import send_file
        _fp = open(download_file.encode('utf-8'), 'rb')
        return send_file(_fp, as_attachment=True, download_name=os.path.basename(relative))
    return app_api.render_page(os.path.join('errors', '404.html'), message=errorMsg)

# -*- coding: utf-8 -*-
import os
from flask import Blueprint, current_app, url_for
from .. import app_api
from .mod_utils import ModUtils
from .config import Config

__mod_path = ModUtils().get_mod_path()
__mod_name = ModUtils().get_mod_name()
__mod_static = os.path.join(__mod_path, 'static')
__mod_templates = os.path.join(__mod_path, 'templates')
__mod_web_prefix = '/' + __mod_name


mod = Blueprint(__mod_name, __name__, url_prefix=__mod_web_prefix,
                static_folder=__mod_static,
                template_folder=__mod_templates)

_auth_decorator = app_api.get_auth_decorator()


@mod.route('/')
@_auth_decorator
def __index():
    """
    Функция отображает список файлов логирования приложения
    :return:
    """
    _utils = ModUtils()
    _tpl = _utils.get_template('index')
    _tpl_vars = {}
    # навигацию на странице будем использовать для скачивания файла
    # заголовок левой навигационной колонки
    _tpl_vars['page_side_title'] = 'Файлы для скачивания'
    # список файлов скачивания
    _root_path = current_app.config['APP_LOG_PATH']
    _files = _utils.get_error_logs(_root_path)
    if _files:
        _files.sort()
        _navi = []
        for _fn in _files:
            _url = url_for(mod.name + '.__download', filename=_fn)
            # _ni = '<a href="' + _url + '">' + _fn + '</a>'
            _ni = {}
            _ni['code'] = _fn.replace('.', '-')
            _ni['href'] = _url
            _ni['label'] = _fn
            _navi.append(_ni)
        _tpl_vars['navi'] = _navi
    # текущий файл для вывода построчно
    _log_lines = _utils.read_log_file(_root_path)
    if _log_lines:
        _t = []
        for _li in _log_lines:
            _nl = _li
            if _nl.startswith('['):
                _nl = '<b>' + _nl + '</b>'
                pass
            else:
                _nl = '&nbsp;'*5 + _nl
            _t.append(_nl)
        _tpl_vars['text_lines'] = _t
    _tpl_vars['page_title'] = 'Файл: ' + Config.error_file
    _tpl_vars['base_url'] = mod.url_prefix
    return app_api.render_page(_tpl, **_tpl_vars)


@mod.route('/download/<filename>')
@_auth_decorator
def __download(filename):
    # получаем путь до директории с логами
    _root_path = current_app.config['APP_LOG_PATH']
    download_file = os.path.join(_root_path, filename)
    # проверяем существует ли файл
    errorMsg = 'Файл не найден: ' + filename
    if os.path.exists(download_file.encode('utf-8')):
        if not os.path.isdir(download_file.encode('utf-8')):
            from flask import send_file
            _fp = open(download_file.encode('utf-8'), 'rb')
            return send_file(_fp, as_attachment=True, download_name=os.path.basename(filename))
    return app_api.render_page(os.path.join('errors', '404.html'), message=errorMsg)

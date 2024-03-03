# -*- coding: utf-8 -*-
"""
Модуль предназначен для предоставление функциональности текстового поиска
"""

import os
import json

from flask import Blueprint, request, flash, g, session, redirect, url_for
from werkzeug.utils import secure_filename
from app import app
from werkzeug.urls import url_parse
from flask_login import login_required

from app.utilites.code_helper import CodeHelper
from app.utilites.some_config import SomeConfig
from app.search_mgt.portal_search import PortalSearch

from app.search_mgt.search_conf import SearchConf

from app import app_api

MOD_NAME = SearchConf.MOD_NAME
mod = Blueprint(MOD_NAME, __name__, url_prefix='/' + MOD_NAME, template_folder=SearchConf.get_mod_tpl_path(), static_folder=SearchConf.get_mod_static_path())

MOD_DATA_PATH = SearchConf.get_mod_data_path()
if not os.path.exists(MOD_DATA_PATH):
    try: os.mkdir(MOD_DATA_PATH)
    except: pass


_auth_decorator = app_api.get_auth_decorator()

@mod.route('' , methods=['POST', 'GET'], strict_slashes=False)
@_auth_decorator
def search():
    """
    Метод возвращает результаты поиска по заданным параметрам
    """
    tmpl_vars = {}
    search_obj = PortalSearch()
    uname = 'anonymous'

    if g.user:
        uname = g.user.login
    search_obj.set_current_user(uname)
    search_obj.read_request_args(request)

    tmpl_vars = search_obj.run()
    tmpl_vars['title'] = "Поиск по данным портала"
    tmpl_vars['page_title'] = "Результаты поиска"
    tmpl_vars['base_url'] = url_for('search_mgt.search', **tmpl_vars['paging_vars'])
    tmpl_vars['request_args'] = request.args
    if 'result_list' in tmpl_vars:
        if 1 == len(tmpl_vars['result_list']):
            _go2 = search_obj.get_result_item_link(tmpl_vars['result_list'][0])
            return redirect(_go2)
    return app_api.render_page("/search.html", **tmpl_vars)


@mod.route('/by_code/<label_code>', methods=['GET'])
@_auth_decorator
def __search_by_code(label_code):
    """
    Функция производит поиск объекта по rdfs:label label_code и
    Реализация для использования с семантическими технологиями и модулем splm_nav
    Настройка осуществляется - SearchConf.OBJECT_VIEW = 'splm_nav.uri_class' указание endpoint для создания ссылки с
    помощью функции flask.url_for
    :param str label_code: код индентифицирующий объект на портале
    :return: flask.redirect
    """
    _query_code = SearchConf.SEARCH_BY_CODE_QUERY
    _query_vars = {}
    _query_vars[SearchConf.SEARCH_BY_CODE_VAR] = str(label_code)
    _first = {}
    try:
        _result = app_api.tsc_query(_query_code, _query_vars)
        if not _result and isinstance(_result, dict):
            _result = []
        if not isinstance(_result, list):
            _result = []
        if _result:
            _first = _result[0]
    except Exception as ex:
        _result = []
    class_name = ''
    uri=''
    if _first:
        if 'o' in _first:
            uri = _first.get('o')
        if 'o_cls' in _first:
            class_name = _first.get('o_cls').split('#')[1]
    _go2 = url_for(SearchConf.OBJECT_VIEW, class_object=class_name, uri=uri)
    return redirect(_go2)


@mod.route('/test/code/<label_code>', methods=['GET'])
def __test_search_links(label_code):
    _mod_api = app_api.get_mod_api('search_mgt')
    _html = ''
    _search_link = _mod_api.make_search_link(label_code)
    _html += 'Link tester!'
    _html += '<hr />'
    _html += 'Simple search link: &nbsp;' + _search_link + '<br />'
    _html += '<br />'
    _seach_by_code_link = _mod_api.make_code_link(label_code)
    _html += 'Search by code link: &nbsp;' + _seach_by_code_link + '<br />'
    return _html

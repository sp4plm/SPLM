# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса портала
предоставляет функциональность управления модулями
"""
import os
import json
from math import ceil

from flask import Blueprint, url_for, request

from app.utilites.jqgrid_helper import JQGridHelper
from app import app_api
from .mod_utils import ModUtils

__mod_utils = ModUtils()

mod = Blueprint(__mod_utils.get_mod_name(), __name__, url_prefix='/appmodules',
                static_folder=__mod_utils.get_web_static_path(),
                template_folder=__mod_utils.get_web_tpl_path())

_auth_decorator = app_api.get_auth_decorator()


@mod.route('/module/<name>', methods=['GET'])
@_auth_decorator
def __view_module_info(name):
    _mod_utils = ModUtils()
    mod_name = _mod_utils.get_mod_name()
    _tpl_vars = {}
    _tpl_name = os.path.join(mod_name, 'module.html')

    # имя модуля должно быть
    _mod_man = app_api.get_mod_manager()
    _mod_inf = _mod_man.get_mod_decscription(name)  # type: rdflib.Graph()

    # соберем навигацию из списка модулей

    _source_lst = []
    _source_lst = _mod_man.get_modules_register()
    rows = []
    for _item in _source_lst:
        row = {'code': '', 'label': '', 'href': ''}
        _href = url_for(mod.name +'.__view_module_info', name=_item['name'])
        _a = '<a href="%s">%s</a>' % (_href, _item['name'])
        row['code'] = _item['name']
        row['label'] = str(_item['title'])
        row['href'] = _href
        rows.append(row)

    _tpl_vars['navi'] = rows
    _tpl_vars['page_side_title'] = 'Список модулей'
    _tpl_vars['module'] = None
    _tpl_vars['_admin_links'] = []
    # если информация пришла, то подготавливаем вывод
    if _mod_inf is not None:
        _dc = {}
        _q = """
        SELECT ?p ?o WHERE {
            ?s a osplm:Module .
            ?s ?p ?o . FILTER(?p != osplm:hasURL)
        }
        """
        _info = _mod_inf.query(_q)
        _t = []
        for _r in _info:
            _t = _r.asdict()
            _k = __normalize_ns(_t['p'])
            _dc[_k] = __normalize_ns(_t['o'])  # str(_t['o'])
        _tpl_vars['module'] = _dc
        _urls = _mod_man.get_mod_admin_urls(name)
        # print('_urls', _urls)
        _tpl_vars['_admin_links'] = _urls
        _tpl_vars['page_title'] = _dc['dc:title']
        pass
    else:
        pass
    # иначе выводим сообщение что модуля не существует
    return app_api.render_page(_tpl_name, **_tpl_vars)


def __normalize_ns(_uri):
    _ns_lst = {}
    _ns_lst['http://www.w3.org/1999/02/22-rdf-syntax-ns'] = 'rdf'
    _ns_lst['http://purl.org/dc/elements/1.1/'] = 'dc'
    _ns_lst['http://www.w3.org/2000/01/rdf-schema'] = 'rdfs'
    _ns_lst['http://splm.portal.web/osplm'] = 'osplm'
    _ns_lst['http://purl.org/dc/dcmitype/'] = 'DCMI'
    _ns_lst['http://www.w3.org/2001/XMLSchema'] = 'xsd'
    for _long in _ns_lst:
        if _uri.startswith(_long):
            _t = _uri.replace(_long, '')
            _t = _t.lstrip('#')
            _t = _ns_lst[_long] + ':' + _t
            _uri = _t
    return _uri


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
    from app import mod_manager
    _source_lst = []
    _source_lst = mod_manager.get_modules_register()

    if search_flag and '' != filters:
        print('try find by filters', filters)
        _source_lst = _mod_utils.search_tbl_rows(_source_lst, filters)

    rows = []
    for _item in _source_lst:
        row = {'Toolbar': '', 'Label': '', 'Name': '', 'Description':'', 'IsDefault':''}
        _href = url_for(mod.name +'.__view_module_info', name=_item['name'])
        _a = '<a style="color:#3366BB; text-decoration:underline;" href="%s">%s</a>' % (_href, _item['name'])
        row['Name'] = _a  # _item['name']
        row['Label'] = str(_item['title'])
        row['Description'] = str(_item['description'])
        if not _item['name'].startswith('mod_'):
            row['IsDefault'] = 'Да'
        rows.append(row)

    if 1 < len(rows):
        rows = _mod_utils.sort_tbl_rows(rows, sord, sidx)

    answer['page'] = page
    answer['records'] = len(rows)
    answer['total'] = ceil(answer['records'] / limit)
    answer['rows'] = rows[offset:offset + limit] if len(rows) > limit else rows
    return json.dumps(answer)


@mod.route('/manage', methods=['GET'])
@_auth_decorator
def __manage():
    _mod_utils = ModUtils()
    mod_name = _mod_utils.get_mod_name()
    _tpl_vars = {}
    _tpl_vars['page_title'] = 'Управление модулями портала'
    _base_tbl = JQGridHelper.get_jqgrid_config()
    if 30 not in _base_tbl['rowList']:
        _base_tbl['rowList'].append(30)
    _base_tbl['rowNum'] = 30
    _base_tbl['rowList'].append(50)
    # теперь надо добавить состав колонок
    _base_tbl['colModel'] = _mod_utils.get_view_table_columns()
    _base_tbl['url'] = url_for(mod_name + '.__get_list')
    _base_tbl['sortname'] = 'Name'
    _base_tbl['sortorder'] = 'asc'
    _tpl_vars['json_tbl'] = json.dumps(_base_tbl)
    _tpl_name = os.path.join(mod_name, 'index.html')
    return app_api.render_page(_tpl_name, **_tpl_vars)

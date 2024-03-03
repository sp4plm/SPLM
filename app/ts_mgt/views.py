# -*- coding: utf-8 -*-

import os
import json

from flask import Blueprint, request
from app import app_api
from .mod_utils import ModUtils


mod = Blueprint('ts_mgt', __name__,
                url_prefix=ModUtils.get_web_root(),
                static_folder=os.path.join(ModUtils.get_mod_pth(), 'static'),
                template_folder=os.path.join(ModUtils.get_mod_pth(), 'templates'))

_auth_decorator = app_api.get_auth_decorator()


@mod.route('/man/download_exported/<key>')
@_auth_decorator
def __download_exported(key):
    file_name = ''
    file_path = ''
    file_path = ModUtils.get_exported_file(key)
    file_name = os.path.basename(file_path)
    mime = 'application/x-unknown'
    from flask import send_file, after_this_request
    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
        except Exception as error:
            print("Error removing or closing downloaded file handle", error)
        return response
    return send_file(file_path, mimetype=mime,
                     as_attachment=True, attachment_filename=file_name)


@mod.route('/man/api/exportQuery', methods=['POST'])
@_auth_decorator
def __export_results():
    answer = {'Data': None, 'Error': '', 'State': 200, 'Msg': ''}

    _ts = request.form['ts']  # triple store
    _q = request.form['q']  # query text
    _f = request.form['fmt']  # result format: xml, ttl, json, csv

    _q_res = app_api.tsc_query(_q)
    _q_res = ModUtils.format_qanswer(_q_res)
    _res = ''
    try:
        _res = ModUtils.export_format(_q_res, _f)
    except Exception as ex:
        answer['Error'] = 'Не удалось выбранные данные привести к нужному формату -> ' + str(_f)
        answer['State'] = 500

    _key = ModUtils.get_some_key()

    # создать файл, записать содержимое, отдать файл клиенту
    _mod_path = '' + ModUtils.get_exported_path()
    file_name = ModUtils.get_exported_name(_key) + '.' + str(_f)
    file_path = os.path.join(_mod_path, file_name)

    try:
        with open(file_path, "w", encoding="utf-8") as _fp:
            _fp.write(_res)
    except Exception as ex:
        answer['Error'] = 'Не удалось сохранить выбранные данные в файл: {}' . format(ex)
        answer['State'] = 500
        error_msg = 'Some error. Can not export query result! ({})' . format(ex)
        print(mod.name + '.views.__export_results.Error:', error_msg)

    answer['Data'] = _key
    answer['State'] = 200
    answer['Error'] = ''

    return json.dumps(answer)

@mod.route('/man/api/sendQuery', methods=['POST'])
@_auth_decorator
def __exec_query():
    # {'Data': [], 'Error': '', '?State': 0-1000, 'Msg':''}
    answer = {'Data': [], 'Error': '', 'State': 200, 'Msg':''}

    _ts = request.form['ts']  # triple store
    _q = request.form['q']

    _q_res = app_api.tsc_query(_q)

    # требуется обработать граф - rdflib.Graph
    if ModUtils.is_construct_query(_q):
        from rdflib import Graph
        if isinstance(_q_res, Graph):
            _g = Graph()
            _g += _q_res
            _q_res = []
            # тепрь будем преобразовывать в список словарей
            if _g.__len__() > 0:
                pass
                _r_keys = ['s', 'p', 'o']
                for _i in _g:
                    _t = {}
                    # print(mod.name + '.views.__exec_query -> _i', _i)
                    _t1 = []
                    for _c in _i:
                        # print(mod.name + '.views.__exec_query -> _c', _c)
                        _t1.append(str(_c))
                    # print(mod.name + '.views.__exec_query -> _t1', _t1)

                    # _t = (_r_keys, *_t1)
                    _t = {_r_keys[_k]: _t1[_k] for _k in range(len(_r_keys))}
                    # print(mod.name + '.views.__exec_query -> _t', _t)
                    _q_res.append(_t)

    if isinstance(_q_res, list):
        answer['Data'] = ModUtils.format_qanswer(_q_res)
    else:
        answer['Error'] = _q_res
        answer['Msg'] = 'Ошибка выполнения запроса: ' + str(answer['Error'])
        answer['State'] = 500

    return json.dumps(answer)


@mod.route('/view_node', methods=['GET'])
@_auth_decorator
def __view_node():
    return 'View node page'


@mod.route('/man/interface', methods=['GET'])
@_auth_decorator
def __index():
    _tpl_name = os.path.basename(os.path.dirname(__file__)) + '/editor.html'
    _tpl_vars = {}
    _tpl_vars['title'] = 'Интерфейс работы с TripleStore'
    _tpl_vars['use_js_jquery'] = True
    _tpl_vars['base_url'] = mod.url_prefix
    _tpl_vars['ts_list'] = __get_ts_list()
    return app_api.render_page(_tpl_name, **_tpl_vars)


def __get_ts_list():
    _res = []
    _t = ModUtils.get_portal_storage()
    _res.append((_t.get_repository(), _t.get_endpoint()))
    return _res

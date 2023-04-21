# -*- coding: utf-8 -*-
import json
import os

from app.utilites.utilites import Utilites

class ModUtils:
    _class_file=__file__
    _debug_name='ts_mgt.Utils'

    @staticmethod
    def get_exported_file(key):
        _file = ''
        _pth = ModUtils.get_exported_path()
        _name = ModUtils.get_exported_name(key)
        catched = ''
        for _f in os.scandir(_pth):
            if not _f.is_file():
                continue
            file_name = _f.name
            if file_name.startswith(_name):
                catched = file_name
                break;
        _file = os.path.join(_pth, catched)
        return _file

    @staticmethod
    def get_exported_name(key=None):
        if not isinstance(key, str) or '' == key:
            key = ModUtils.get_now()
            _t = str(key).split('.')
            key = '-'.join(_t)
        _pref = ModUtils.get_export_prefix()
        if not str(key).startswith(_pref + '-'):
            _name = _pref + '-' + str(key)
        else:
            _name = str(key)
        return _name

    @staticmethod
    def get_export_prefix():
        return 'query_result'

    @staticmethod
    def get_some_key():
        key = ModUtils.get_now()
        _t = str(key).split('.')
        key = '-'.join(_t)
        return key

    @staticmethod
    def get_exported_path():
        _pth = ''
        _pth = ModUtils.get_mod_pth()
        _pth = os.path.join(_pth, 'tmp')
        if not os.path.exists(_pth):
            os.mkdir(_pth)
        return _pth

    @staticmethod
    def export_format(data, _fmt):
        _res = None
        try:
            _func = getattr(ModUtils, 'data_2_' + str(_fmt))
            _res = _func(data)
        except Exception as ex:
            raise Exception('Неизвестный преобразователь данных -> ' + str(_fmt))
        return _res

    @staticmethod
    def data_2_json(data):
        _res = ''
        _res = json.dumps(data)
        return _res

    @staticmethod
    def __data_2_xml_cells(_data, _keys=None):
        _res = []
        _work = None
        if not _data:
            return ''
        if _data and isinstance(_data, list):
            if not isinstance(_keys, list) or 0 == len(_keys):
                _x = 0
                _keys = [_it + str(_x + 1) for _x, _it in enumerate(('Cell ' * len(_data)).split(' ')[:-1])]
            _work = dict(zip(_keys, _data))
        else:
            _work = _data
        if isinstance(_work, dict):
            for _k in _work:
                _d2s = ''
                _d2s += ModUtils.__str2tag(_k)
                _d2s += str(_work.get(_k, ''))
                _d2s += ModUtils.__str2tag(_k).replace('<', '</')
                _res.append(_d2s)
        return ''.join(_res)

    @staticmethod
    def __str2tag(_str):
        return '<' + str(_str) + '>'

    @staticmethod
    def data_2_xml(data):
        _xml = ''
        _xml += '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+"\r\n"
        _xml += '<Rows>'
        for ud in data:
            _xml += '<Row>'+ModUtils.__data_2_xml_cells(ud)+'</Row>'
        _xml += '</Rows>'
        return _xml

    @staticmethod
    def get_portal_storage():
        _store = Utilites.get_storage_driver()
        return _store

    @staticmethod
    def send_query(end_point, q):
        _send_data = {}
        _answer = []
        _store = ModUtils.get_portal_storage()
        try:
            _answer = _store.query(q)
        except Exception as ex:
            print('Can not send query to ' + _store.get_endpoint())
        return _answer

    @staticmethod
    def format_qanswer(qanswer):
        _res = []
        _res = qanswer
        return _res

    @staticmethod
    def get_now():
        from time import time
        return time()

    @staticmethod
    def get_web_root():
        return '/' + os.path.basename(os.path.dirname(__file__))

    @staticmethod
    def get_mod_pth():
        return os.path.dirname(__file__)

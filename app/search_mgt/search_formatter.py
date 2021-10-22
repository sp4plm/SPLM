# -*- coding: utf-8 -*-
import html
from flask import url_for

from app.utilites.code_helper import CodeHelper, os

from app.search_mgt.search_conf import SearchConf

MOD_NAME = SearchConf.MOD_NAME


class SearchFormatter:

    def __init__(self):
        self._basicTypes = ['literal', 'literal-typed']
        self._EOL = ["\r\n", "\r", "\n"]
        self._resultRows = []
        self._extLink = True # при создании ссылок на объекты указывает что ссылку открывать в новом окне

        # допустим нам надо по какому-то условию не включать строку в результат
        self._canAddThisResult = True
        self._checkedLinks = {} # будем складывать ссылки только уникальные

        self._lastCls = ''
        self._lastTxt = ''

        self._serviceKey = ''
        self._res = []
        self._ch = CodeHelper()
        self._work_dir = SearchConf.get_mod_data_path()

    def _proc_cell(self, ky, val):
        """"""

    def _proc_item(self, data):
        """"""
        res = {}
        service_keys = ['cls', 'lbl']
        for k, val in data.items():
            """"""
            origin_k = k
            sub_k = ''
            if -1 < k.find('_'):
                # ключ составной - надо сворачивать
                _t_k = k.split('_')
                if _t_k[1] in service_keys:
                    origin_k = _t_k[0]
                    sub_k = _t_k[1]

            if origin_k not in res:
                res[origin_k] = val
                if '' != sub_k:
                    res[origin_k] = {}

            if 'cls' == sub_k:
                """"""
                if not isinstance(res[origin_k], dict):
                    _t = res[origin_k]
                    res[origin_k] = {}
                    res[origin_k]['value'] = _t
                    if self._is_uri(_t):
                        res[origin_k]['type'] = 'uri'
                res[origin_k]['class'] = {}
                res[origin_k]['class']['value'] = val
                if self._is_uri(val):
                    res[origin_k]['class']['type'] = 'uri'
            if 'lbl' == sub_k:
                """"""
                if not isinstance(res[origin_k], dict):
                    _t = res[origin_k]
                    res[origin_k] = {}
                    res[origin_k]['value'] = _t
                    if self._is_uri(_t):
                        res[origin_k]['type'] = 'uri'
                res[origin_k]['label'] = {}
                res[origin_k]['label']['value'] = val
        # обошли все ключи и отформатировали результат
        # теперь требуется доформатировать результат: объекты превращаем в ссылки если возможно
        # если нет то приводим к примитивам
        res = self._format_for_view(res)
        #print('formated - item:', res)
        file_n = 'sr-' + str(len(self._resultRows) + 1) + '.logres'
        file_n = os.path.join(self._work_dir, file_n)
        #self._ch.add_file(file_n)
        #self._ch.write_to_file(file_n, str(res))
        self._resultRows.append(res)

    def _format_for_view(self, row):
        _t = {}
        for k, val in row.items():
            if isinstance(val, dict):
                href = self._cook_onto_href(val)
                val = self._to_primitive(val)
                if '' != href:
                    """"""
                    val = "<a href=\"" + href + "\">" + val + "</a>"
            else:
                val = self._to_primitive(val)
            _t[k] = val
        return _t

    def _parse_uri(self, uri_str):
        result = {'prefix': '', 'key': ''}
        if -1 < uri_str.find('#'):
            _t = uri_str.split('#')
            result['prefix'] = _t[0]
            result['key'] = _t[1]
        return result

    def format(self, src):
        """"""
        for itx in src:
            self._proc_item(itx)
        self._clearResult()
        return self._resultRows

    def _clearResult(self):
        _t = []
        for row in self._resultRows:
            if row is None:
                continue
            _t.append(row)
        self._resultRows = _t

    def _is_linked_obj(self, check):
        return ('type' in check and 'uri'==check['type'])

    @staticmethod
    def _to_primitive(some_data):
        if not isinstance(some_data, dict) and not isinstance(some_data, list):
            return html.escape(some_data) # надо разобраться с html тэгами
        if isinstance(some_data, list):
            # сперва каждый элемент списка надо привести к нормальному виду
            _t = []
            for ilst in some_data:
                _t.append(SearchFormatter._to_primitive(ilst))
            return ', '.join(_t)
        # теперь мы будем работать со словарем
        if 'label' in some_data and '' != some_data['label']:
            if isinstance(some_data['label'], dict) and 'value' in some_data['label']\
                    and '' != some_data['label']['value']:
                return SearchFormatter._to_primitive(some_data['label']['value'])
            else:
                if isinstance(some_data['label'], list):
                    return SearchFormatter._to_primitive(some_data['label'])
            return some_data['label']
        if 'value' in some_data and '' != some_data['value']:
            return SearchFormatter._to_primitive(some_data['value'])
        # безысходность
        val = ''
        try:
            # надо закодировать теги
            val = html.escape(some_data)
        except:
            val = ''
        return val

    def _cook_onto_href(self, some_obj):
        """"""
        href = ''
        if isinstance(some_obj, list):
            return href
        if isinstance(some_obj, dict):
            _cls = ''
            _uri = ''
            if 'class' in some_obj:
                if 'value' in some_obj['class']:
                    _parsed_cls = self._parse_uri(some_obj['class']['value'])
                    if '' != _parsed_cls['key']:
                        _cls = _parsed_cls['key']
            if 'value' in some_obj:
                _uri = some_obj['value']
        else:
            parsed_val = self._parse_uri(some_obj)
            if '' != parsed_val['key']:
                _uri = some_obj
                # теперь надо определить класс для URI
                _cls = ''
        if '' != _cls and '' != _uri:
            href = self._create_obj_link(_cls, _uri)
        return href

    def _create_obj_link(self, class_name, uri):
        try:
            # link = url_for('onto.uri_class', class_object=class_name, uri=uri)
            link = uri
        except:
            link = ''
        return link

    def _is_uri(self, test):
        flg = False
        _parsed = self._parse_uri(test)
        if '' != _parsed['prefix'] and '' != _parsed['key']:
            flg = True
        return flg
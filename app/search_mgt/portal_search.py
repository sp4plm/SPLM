# -*- coding: utf-8 -*-

import os
from urllib.parse import unquote
from math import ceil, floor
import re
import json

from bs4 import BeautifulSoup

from app.utilites.code_helper import CodeHelper
from app.utilites.some_config import SomeConfig
from app.utilites.data_serializer import DataSerializer
from app.search_mgt.search_formatter import SearchFormatter, html

from app.app_api import tsc_query

from app.search_mgt.search_conf import SearchConf

MOD_NAME = SearchConf.MOD_NAME


class PortalSearch:
    _class_file = __file__
    _debug_name = 'PortalSearch'
    _def_query_code = 'query_mgt.app.search'

    _file_ext = 'search'
    _file_res_struct = {
        'user': '', # текущий пользователь
        'request': '', # строка поиска
        'records': [], # список записей результата,
        'history': [], # стек запросов
        'resHistory': {} # храним результаты запросов, где ключ md5 строки запроса, а знач - записи
    }
    _format_limit = 100

    _basic_types = ['literal', 'literal-typed']
    _eol = ["\r\n", "\r", "\n"]
    _no_read_files = ['.', '..']

    settings_file = 'settings.json'

    def __init__(self):
        self._cnt_results = 0
        self._cnt_page_results = 1
        self._q_hash = '' # хеш кода запроса
        self._res = None # результат выполнения sparql запроса
        self._ext_link = True # все созданные ссылки открывать в новом окне

        self._search_key = 'arg' # ключ в $_GET/$_POST параметрах - строка поиска
        self._subsearch_key = 'SearchIn'
        self._page_key = 'page' # ключ в $_GET/$_POST параметрах - номер страницы
        self._qcode_key = 'q' # ключ в GET параметрах идентификатора sparql запроса
        self._lang_key = 'lang' # ключ в $_GET/$_POST параметрах - переменнная языка запроса
        self._cls_search_key = 'SearchCLS'
        self._clspref_search_key = 'cls_'
        self._request_str = ''
        self._is_subsearch = False
        self._curr_page = 1
        self._query_code = '' # идентификатор шаблона sparql запроса
        self._search_lang = ''
        # self._search_vars = {} # переменные-параметры к sparql запросу
        self._search_vars = {"prefix" : "PREFIX onto: <http://proryv2020.ru/req_onto#>"} 
        self._other_params = {} # дополнительные параметры для выполнения запроса или форматирования результата
        self._use_cache = False
        self._current_user = None
        self._result_struct = None
        self._result_classes = None
        self._result_filters = None
        self._work_dir = SearchConf.get_mod_data_path()
        self.breaker = '<!-- #@# -->'
        self._request = None # flask request link - should be set before search


        # Чтение настроек из файла
        with open(os.path.join(self._work_dir, self.settings_file),  "r", encoding="utf-8") as f:
            data = json.load(f)

        self._recs_on_page = data['_recs_on_page'] if '_recs_on_page' in data else 20
        self._pages_on_page = data['_pages_on_page'] if '_pages_on_page' in data else 3


    def run(self):
        """"""
        if self._result_struct is None:
            self._result_struct = self._file_res_struct
        # получить механизм поиска по данным
        self._get_result()
        if self._is_subsearch:
            self._get_sub_result()
       # обработать полученные результаты
        count = len(self._result_struct['records'])
        cntPages = ceil(count / self._recs_on_page)
        if cntPages < self._curr_page:
            self._curr_page = cntPages
        if 0 >self._curr_page:
            self._curr_page = 1
        limit = self._recs_on_page
        offset = (self._curr_page * self._recs_on_page) - self._recs_on_page
        if limit+offset > count:
            limit = count-offset
        list = self._result_struct['records'][offset:offset+limit]
        curPage = int(self._curr_page)
        PonP = self._pages_on_page
        pB = ceil(cntPages /PonP)
        cntRecs = count
        request = self._result_struct['request']
        hideSearchForm = True
        # форматирование результата
        # ну и раскрасим результат
        if list:
            _tmp = []
            for item in list:
                #print('input item:', item)
                rec = self._mark_search_result(item)
                #print('marked item:', rec)
                _tmp.append(rec)
            list = _tmp
        tmpl_vars = {}
        tmpl_vars['count'] = count
        tmpl_vars['cntPages'] = cntPages
        tmpl_vars['limit'] = limit
        tmpl_vars['offset'] = offset
        tmpl_vars['list'] = list
        tmpl_vars['curPage'] = curPage
        tmpl_vars['PonP'] = PonP
        tmpl_vars['pB'] = pB
        tmpl_vars['cntRecs'] = cntRecs
        tmpl_vars['request'] = self._result_struct['request']
        tmpl_vars['hideSearchForm'] = hideSearchForm
        tmpl_vars['classFilter'] = self._result_struct['classes']
        tmpl_vars['result_list'] = list
        tmpl_vars['str_request'] = self._result_struct['request']
        tmpl_vars['search_in'] = self._is_subsearch
        tmpl_vars['offset'] = offset

        tmpl_vars['cnt_pages'] = cntPages
        tmpl_vars['pageOff'] = floor(curPage/PonP)*PonP
        if curPage == PonP:
            tmpl_vars['pageOff'] -= PonP
        tmpl_vars['start'] = tmpl_vars['pageOff']+1
        tmpl_vars['stop'] = tmpl_vars['start'] + 1

        if cntPages < (tmpl_vars['pageOff']+PonP):
            tmpl_vars['stop'] = cntPages + 1
        else:
            tmpl_vars['stop'] = tmpl_vars['pageOff']+PonP+1

        # теперь надо собрать все параметры для url пагинации
        paging_vars = {}
        paging_vars[self._search_key] = tmpl_vars['request'] # строка запроса
        paging_vars[self._subsearch_key] = 1 if tmpl_vars['search_in'] else 0 # поиск в найденном
        # теперь разберемся с фильтром классов
        if tmpl_vars['classFilter']:
            for _cls, _lbl in tmpl_vars['classFilter'].items():
                _key = self._clspref_search_key + _cls
                if _key not in self._request.args:
                    continue
                paging_vars[_key] = _lbl['name']
        tmpl_vars['paging_vars'] = paging_vars

        return tmpl_vars

    def _format_data(self):
        """"""
        if self._res:
            """"""
            frm = SearchFormatter()
            _t = frm.format(self._res)
            self._res = _t

    def _get_result(self):
        """"""
        # read data - arguments for search from request should exec user
        if self._is_subsearch:
            """"""
            self._read_search_result()
            self._cnt_results = len(self._result_struct['records'])
            self._cnt_page_results = ceil(self._cnt_results / self._recs_on_page)
            self._result_struct['history'].append(self._request_str)
        else:
            """"""
            self._get_data()
            self._format_data()
            q_hash = self._cook_request_hash()
            self._result_struct['history'].append(self._request_str)
            self._result_struct['clsResult'] = {}
            self._result_struct['classes'] = {}
            q_ind = len(self._result_struct['history'])-1
            self._result_struct['resHistory'][q_hash] = self._customize_result()
            self._result_struct['request'] = self._result_struct['history'][q_ind]
            self._result_struct['records'] = self._result_struct['resHistory'][q_hash]
            self._result_struct['user'] = self._current_user
            self._cnt_results = len(self._result_struct['records'])
            self._cnt_page_results = ceil(self._cnt_results/self._recs_on_page)
            self._save_search_result()

    def _get_sub_result(self):
        new_records = []
        classes_list = {}
        new_classes_list = {}
        new_classitems_list = {}
        _class_select_flg = self._is_classes_selected()
        if _class_select_flg:
            classes_list = self._get_filtered_classes()

        for k in range(len(self._result_struct['records'])):
            rec = self._result_struct['records'][k]
            # print('_get_sub_result.rec:', rec)
            _t = rec.split(self.breaker)
            # print('_get_sub_result._t[0]:', _t[0])
            # выполняем всю работу с классами - если классы вообще выбраны
            if _class_select_flg:
                _cls = self._is_key_is_in_selected_classes(k, classes_list)
                if False == _cls:
                    continue
                if _cls not in new_classes_list:
                    new_classes_list[_cls] = {'name': classes_list[_cls],'key': _cls}
                if _cls not in new_classitems_list:
                    new_classitems_list[_cls] = []
                new_classitems_list[_cls].append(len(new_records))
            if re.search('('+self._request_str+')', _t[0], flags=re.I & re.U):
                new_records.append(rec)

        q_hash = self._cook_request_hash()
        self._result_struct['history'].append(self._request_str)
        q_ind = len(self._result_struct['history']) - 1
        self._result_struct['resHistory'][q_hash] = new_records
        self._result_struct['request'] = self._result_struct['history'][q_ind]
        self._result_struct['records'] = self._result_struct['resHistory'][q_hash]
        self._result_struct['user'] = self._current_user
        self._result_struct['clsResult'] = new_classitems_list
        self._result_struct['classes'] = new_classes_list
        self._save_search_result()

    def _is_key_is_in_selected_classes(self, k, selected):
        res = False
        for cls, lst in self._result_struct['clsResult'].items():
            if k in lst:
                if cls in selected:
                    res = cls
                    break
        return res

    def _is_classes_selected(self):
        flg = False
        if self._cls_search_key in self._search_vars or self._cls_search_key in self._other_params:
            flg = True
        return flg

    def _get_filtered_classes(self):
        res = {}
        if not self._is_classes_selected():
            return res
        # must search in post and get request
        if self._request.args:
            for k, v in self._request.args.items():
                """"""
                if 0 == k.find(self._clspref_search_key):
                    nk = k.replace(self._clspref_search_key, '')
                    res[nk] = v
        if self._request.form:
            form_dict = self._request.form.to_dict(flat=False)
            for k, v in form_dict.items():
                """"""
                if 0 == k.find(self._clspref_search_key):
                    nk = k.replace(self._clspref_search_key, '')
                    res[nk] = v
        return res

    @staticmethod
    def __strip_tags(some_str, escape=[]):
        flg = False
        result = ''
        if -1 < some_str.find('&lt;') and -1 < some_str.find('&lt;'):
            flg = True
        soup = BeautifulSoup(some_str, features="lxml")
        result = soup.get_text()
        if flg:
            result = html.escape(result)
        return result

    def _mark_search_result(self, rec):
        _t = rec.split(self.breaker)
        _txt = _t[0]
        if '' != _txt:
            sc_ind = _txt.find(':')
            if -1 < sc_ind:
                _txt = _txt[sc_ind:]
        no_tags = self.__strip_tags(_txt)
        if len(no_tags)<len(_txt):
            return _t[0]+self.breaker+_t[1]
        for itx in self._result_struct['history']:
            tmpl = '<span style="background-color:yellow;">\g<1></span>'
            pat = '('+itx+')'
            rec = re.sub(pat,tmpl,_t[0], flags=re.I & re.U)+self.breaker+_t[1]

        return rec

    def read_request_args(self, request):
        """"""
        self._request = request
        _r = self._cls_search_key
        classes_list = []
        _class_filter = 'FILTER(?cl_lbl IN ('
        if request.args:
            for k, v in request.args.items():
                if 0 == k.find(self._clspref_search_key):
                    # значит мы читаем класс
                    # значений может быть много
                    if _r not in self._search_vars:
                        self._search_vars[_r] = _class_filter
                    classes_list.append('"' + unquote(v) + '"')
                    continue

                self._search_vars[k] = v
            if _r in self._search_vars:
                self._search_vars[_r] += ','.join(classes_list)
                self._search_vars[_r] += '))'
        if request.form:
            form_dict = request.form.to_dict(flat=False)
            classes_list = []
            for k, v in form_dict.items():
                if 0 == k.find(self._clspref_search_key):
                    # значит мы читаем класс
                    # значений может быть много
                    if _r not in self._search_vars:
                        self._other_params[_r] = _class_filter
                    classes_list.append('"' + unquote(v) + '"')
                    continue
                self._other_params[k] = v
            if _r in self._other_params:
                self._other_params[_r] += ','.join(classes_list)
                self._other_params[_r] += '))'

        #  но строка поиска может придти и постом
        if self._search_key not in self._search_vars or '' == self._search_vars[self._search_key]:
            if self._search_key in self._other_params and '' != self._other_params[self._search_key]:
                self._search_vars[self._search_key] = self._other_params[self._search_key]


        # обработаем строку поиска
        if '' != self._search_key and self._search_key in self._search_vars:
            if self._is_number(self._search_vars[self._search_key]):
                self._search_vars['parg'] = self._search_vars[self._search_key]
            else:
                self._search_vars['parg'] = '"' + self._search_vars[self._search_key] + '"'
            self._request_str = self._search_vars[self._search_key]
        # обработаем текущую страницу
        self._curr_page = 1
        if '' != self._page_key and self._page_key in self._search_vars:
            self._curr_page = int(self._search_vars[self._page_key])
        # определимся - является ли поиск поиском в найденом
        self._is_subsearch = False
        if '' != self._subsearch_key and self._subsearch_key in self._search_vars:
            self._is_subsearch = (1 == int(self._search_vars[self._subsearch_key]))
        # теперь определим код запроса - возможно его переопределили
        self._query_code = self._def_query_code
        if '' != self._qcode_key and self._qcode_key in self._search_vars:
            self._query_code = self._search_vars[self._qcode_key]
        # определим язык поиска
        if '' != self._lang_key and self._lang_key in self._search_vars:
            self._search_lang = self._search_vars[self._lang_key]
        # теперь наверно можно удалить из параметров код запроса, поиск в найденом, язык и страница ?

    @staticmethod
    def _is_number(some_val):
        flg = False
        try:
            float(some_val)
            flg = True
        except:
            flg = False
        return flg

    def _customize_result(self):
        html = []
        if self._res:
            a = ''
            txt = ''
            pt = '/>([^<]*)</'
            pt = '/(<a.*")>(.*)(<\/a>)/'
            resIdx = 0
            ffff = 0 # debug for
            for row in self._res:
                # print('row', row)
                ffff += 1
                txt = row['res']
                if not txt:
                    continue
                open_a_close = txt.find('>')
                # print('open_a_close', open_a_close)
                close_a_open = txt.find('</')
                # print('close_a_open', close_a_open)
                if -1 == open_a_close or \
                    -1 == close_a_open or \
                    close_a_open < open_a_close:
                    print('PortalSearch._customize_result: Can not select text for search item view: ' + txt)
                    continue
                link_open = txt[0:open_a_close+1]
                # print('link_open', link_open)
                link_close = txt[close_a_open:]
                # print('link_close', link_close)
                txt1 = txt[open_a_close+1:close_a_open]
                a = link_open + 'Ссылка' + link_close
                txt = txt1
                # интеллект )
                additional = ''
                if 'att_cl_lb' in row and '' != row['att_cl_lb'] and ''!= row['val']:
                    additional = '. <'+row['att_cl_lb']+'>: '+row['val']
                str_hash = self._str_to_hash(row['cl'])
                if str_hash not in self._result_struct['clsResult']:
                    self._result_struct['clsResult'][str_hash] = []
                resIdx = len(html)
                self._result_struct['clsResult'][str_hash].append(resIdx)
                if str_hash not in self._result_struct['classes']:
                    self._result_struct['classes'][str_hash] = {'name': row['cl'],'key': str_hash}
                html.append('&lt;'+row['cl']+'&gt;: '+txt+additional+self.breaker+'&nbsp;<br />('+a+')')
                #print('=============================================')
        return html

    def _save_search_result(self):
        file_path = self._get_search_result_file()
        file_store = DataSerializer()
        # print('==========', self._result_struct)
        file_store.dump(file_path, self._result_struct)

    def _read_search_result(self):
        file_path = self._get_search_result_file()
        file_store = DataSerializer()
        self._result_struct = file_store.restore(file_path)

    def _create_result_file(self):
        file_path = self._get_search_result_file()
        return CodeHelper.add_file(file_path)

    def _check_search_result(self):
        file_path = self._get_search_result_file()
        return CodeHelper.check_file(file_path)

    def _get_search_result_file(self):
        file_name = self._cook_result_filename()
        file_path = os.path.join(self._work_dir, file_name)
        return file_path

    def _cook_result_filename(self):
        return str(self._current_user) + '.' + self._file_ext

    def _cook_request_hash(self):
        """"""
        return self._str_to_hash(self._request_str)

    @staticmethod
    def _str_to_hash(some_str):
        from hashlib import sha1
        return sha1(some_str.encode('utf-8')).hexdigest()

    def _get_data(self):
        self._res = self._make_search_request(self._request_str)

    def set_current_user(self, current_user):
        if current_user is not None:
            self._current_user = current_user

    def _get_search_vars(self):
        return self._search_vars

    def _get_query_code(self):
        return self._query_code

    def _make_search_request(self, search_str):
        """"""
        # app_store = app.get_store_tool()
        # result = app_store.search(search_str)

        if '' == search_str:
            return [] # если пустая строка - возвращаем пустой результат

        _query_vars = []
        _query_vars = self._get_search_vars()
        _query_code = self._get_query_code()
        if '' == _query_code or not _query_vars:
            return [] # не падаем - возвращаем пустой результат
        try:
            _result = tsc_query(_query_code, _query_vars)
            if not _result and isinstance(_result, dict):
                _result = []
        except Exception as ex:
            _result = []
        return _result

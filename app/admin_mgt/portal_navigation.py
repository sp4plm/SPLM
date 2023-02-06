# -*- coding: utf-8 -*-
import os
import json

from app.admin_mgt.admin_conf import AdminConf
from app.admin_mgt.navigation_files import NavigationFiles
from app.utilites.code_helper import CodeHelper
from app import app_api


class PortalNavigation(NavigationFiles):
    _class_file = __file__
    _debug_name = 'PortalNavigation'
    # _register = 'navi_blocks.json'

    def __init__(self):
        super().__init__()
        _t = AdminConf.get_mod_path('data')
        self._files_path = os.path.join(_t, AdminConf.NAVI_DIR_NAME)
        self._mod_manager = app_api.get_mod_manager()
        self._map = []
        self.depricated_codes = ['admin_sections'] # список кодов навигационных блоков исключаемых из дерева
        self._navi_struct = self.get_all_navi()

    def get_section_by_code(self, code):
        current = None
        lst = self.get_sections()
        if lst:
            for sec in lst:
                if sec['code'] == code:
                    current = sec
                    break
        return current

    def get_sections(self):
        lst = []
        sections_file = self._register
        sections_path = os.path.join(self._files_path, sections_file)
        if CodeHelper.check_file(sections_path):
            lst = self._read_json_file(sections_path)
        return lst

    def get_sections_navi(self, section_code, user=None):
        lst = []
        sections_file = section_code + '.json'
        sections_path = os.path.join(self._files_path, sections_file)
        file_source = False
        if CodeHelper.check_file(sections_path):
            lst = self._read_json_file(sections_path)
            file_source = True
        else:
            """ выполняем поиск функциональности? которая вернет список ссылок для кода """
            lst = self._try_call_customs(section_code)
        if lst and user is not None:
            _t = []
            for _it in lst:
                """ требуется проверить роли пользователя и роли пункта меню """
                # отсеиваем не подходящее
                if not self._check_user_access(_it, user):
                    continue
                _t.append(_it)
            lst = _t
            if lst:
                _a = [lst]
                # print(self._debug_name + '._get_sections_navi.file_source', file_source)
                # print(self._debug_name + '._get_sections_navi.lst', lst)
                if file_source:
                    # параметры функции сортировки
                    _a.append('asc')
                    _a.append('srtid')  # если источник file то наверно специальная сортировка
                # print(self._debug_name + '._get_sections_navi._a', _a)
                lst = self._sort_items(*_a)
        return lst

    def _get_sections_navi(self, section_code):
        lst = []
        sections_file = section_code + '.json'
        sections_path = os.path.join(self._files_path, sections_file)
        file_source = False
        if CodeHelper.check_file(sections_path):
            lst = self._read_json_file(sections_path, [])
            file_source = True
        else:
            """ выполняем поиск функциональности? которая вернет список ссылок для кода """
            lst = self._try_call_customs(section_code)
        if lst:
            _a = [lst]
            # print(self._debug_name + '._get_sections_navi.file_source', file_source)
            # print(self._debug_name + '._get_sections_navi.lst', lst)
            if file_source:
                # параметры функции сортировки
                _a.append('asc')
                _a.append('srtid')  # если источник file то наверно специальная сортировка
            # print(self._debug_name + '._get_sections_navi._a', _a)
            lst = self._sort_items(*_a)
        return lst

    @staticmethod
    def _sort_items(_lst, ord='asc', attr='label'):
        sort_result = []
        sort_result = _lst
        revers = True if 'asc' != ord else False
        sort_result = sorted(sort_result, key=lambda x: x[attr], reverse=revers)
        return sort_result

    def _try_call_customs(self, sec_code):
        """
        Метод пытается из кода секции навигации создать имя метода на классе и выполнить его
        :param sec_code:
        :return:
        """
        _method_prefix = '_sch_' # section custom handler
        new_name = ''
        for l in sec_code:
            if l.isupper():
                l = '_' + l.lower()
            new_name += l
        new_name = _method_prefix + new_name.lstrip('_')
        res = []
        if hasattr(self, new_name) and callable(getattr(self, new_name)):
            try:
                res = getattr(self, new_name)()
            except Exception as ex:
                # print(ex)
                res = []
        return res

    def _check_user_access(self, point, user):
        flg = False
        if 'roles' not in point:
            flg = True
        else:
            if not point['roles']:
                flg = True
            else:
                _roles = point['roles'].split(',')
                for _r in _roles:
                    if not user.is_anonymous and user.has_role(_r):
                        flg = True
                        break
        return flg

    def get_tpl_path(self, mod_name, tpl_name):
        from app import app_api
        mod_path = app_api.get_mod_path(mod_name)
        search_path = os.path.join(mod_path, 'templates')
        _pth = ''
        for root, dirs, files in os.walk(search_path):
            if tpl_name in files:
                _pth = os.path.join(root, tpl_name)
                break
        if os.path.exists(_pth):
            _pth = _pth.replace(search_path, '').lstrip(os.path.sep)
        _pth = app_api.correct_template_path(_pth)
        return _pth

    def get_current_item(self, flask_request):
        _item = {}
        # требуется получить всю структуру навигации портала -> in constructor
        # получается три дерева с корнями: SiteSections, SiteTopNavi, SiteUserNavi

        # self._navi_struct = self.get_all_navi()
        # print(self._debug_name + '.get_current_item->_struct', _struct)
        if self._navi_struct:
            # print("flask_request.path", flask_request.path)
            # print("self._navi_struct", [_i['href'] for _i in self._navi_struct.values()])
            match = flask_request.path
            matched_lst = []
            for key, ptn in self._navi_struct.items():
                if '' == ptn['href']:
                    continue
                # print("ptn['href']", ptn['href'])
                """
                требуется добавить обработку когда и ссылка и запрошенный пункт меню имеют query string
                """
                if match.startswith(ptn['href']):
                    # print("ptn", ptn)
                    matched_lst.append(ptn)
                    _item = current = ptn
            # выносим работу с совпадениями отдельно для возможности уточнения
            if matched_lst:
                # отсортируем совпавшие по длинне ссылки самые длинные сначала, самые короткие в конце
                # такое решение позволит отсеч пункты меню с короткой сылкой
                matched_lst = self._sort_items(matched_lst, 'desc', 'href')
                # print("get_current_item->matched_lst", [_i['href'] for _i in matched_lst])
                for _i in matched_lst:
                    if match.startswith(_i['href']):
                        _item = current = _i
                        break
                # print("get_current_item->_item", _item)
        return _item

    def get_parent(self, current, _user=None):
        parent = None
        if self._navi_struct and 'parent' in current:
            if current['parent'] in self._navi_struct:
                parent = self._navi_struct[current['parent']]
        return parent

    def get_brothers(self, current, _user=None):
        _lst = []
        if self._navi_struct and 'parent' in current:
            _lst = self.get_sections_navi(current['parent'], _user)
        return _lst

    def is_section(self, item):
        flg = False
        if self._navi_struct:
            if 'href' in item and '' == item['href']:
                flg = True
            else:
                # href совпадает с ребенком
                for key, ptn in self._navi_struct.items():
                    if ptn['href'] == item['href'] and ptn['code'] != item['code']:
                        flg = True
                        break
        return flg

    def get_all_navi(self, start='', user=None):
        if '' == start:
            start = self._register.split('.')[0]
        _t = {}
        _ind = 1
        _indexed = []

        _use_accsess = user is not None

        def _snail(code):
            roots = self._get_sections_navi(code) if not _use_accsess else self.get_sections_navi(code, user)
            if roots:
                for root in roots:
                    key = root['code']
                    if key not in _indexed:
                        _indexed.append(key)
                    root['parid'] = _t[code]['id'] if code in _t else 0
                    _ind = _indexed.index(key)
                    root['id'] = _ind + 1
                    root['parent'] = code
                    if key not in _t:
                        _t[key] = root
                    _snail(key)

        _snail(start)
        return _t

    def check_url_access(self, check_url, user):
        flg = False
        urls_lst = self._mod_manager.get_registred_urls()
        for url in urls_lst:
            if check_url.startswith(url['href']):
                if not url['roles']:
                    flg = True
                else:
                    _t = url['roles'].split(',')
                    for _r in _t:
                        if user.has_role(_r):
                            flg = True
                break
        return flg

    def get_portal_index_url(self):
        _url = '/'
        _endpoint = self._mod_manager.get_start_url()
        from flask import url_for
        if isinstance(_endpoint, str) and '' != _endpoint:
            try:
                _url = url_for(_endpoint)
            except Exception as ex:
                print(self._debug_name + '.get_portal_index_url.Exception: ' + str(ex))
                _url = '/'
        return _url

    def get_portal_index_urls(self):
        _urls = []
        _cfg_enabled = self.get_portal_index_url()  #  выбираем по dublin.ttl
        # если вернулся корень, значит выбираем из всех имеющихся
        if '/' == _cfg_enabled:
            _endpoints = self._mod_manager.get_start_endpoints()
            from flask import url_for
            if _endpoints:
                for _endpoint in _endpoints:
                    try:
                        _url = url_for(_endpoint)
                        _urls.append(_url)
                    except Exception as ex:
                        print(self._debug_name + '.get_portal_index_url.Exception: ' + str(ex))
        else:
            _urls.append(_cfg_enabled)
        return _urls

    def get_portal_index_tpl_name(self):
        return 'index.html' # возможно надо брать из настроек???

# -*- coding: utf-8 -*-
import os
import json

from app.admin_mgt.admin_conf import AdminConf
from app.admin_mgt.navigation_files import NavigationFiles
from app.utilites.code_helper import CodeHelper
from app.utilites.some_config import SomeConfig
from app import mod_manager, app_api


class AdminNavigation(NavigationFiles):
    _class_file = __file__
    _debug_name = 'AdminNavigation'

    def __init__(self):
        super().__init__()
        self._files_path = os.path.join(AdminConf.get_mod_path('data'), AdminConf.NAVI_DIR_NAME)
        self.sections = []
        self.current_section = None
        self.section_navi = []
        self.current_section_navi = None
        self._map = []
        self._navi_struct = {}
        self._url_prefix = app_api.get_app_url_prefix()
        self.gen_map()
        self._navi_struct = self._get_structure()
        # print(self._debug_name + '.__init__: map', self._map)

    def get_section(self, code):
        """
        Метод собирает пункты меню для переданного кода секции
        :param code: str код секции
        :return: list список пунктов (ссылок) для перехода
        """
        lst = []
        # проверяем файл
        # если файла нет пытаемся вызвать метод для персональной обработки\
        lst = self._get_section_data(code)
        return lst

    def _get_section_data(self, code):
        """
        Метод пытается найти данные для указанного кода
        :param code: str
        :return: Any
        """
        data = None
        file_path = self._get_section_items_filename(code)
        try :
            data = self._read_json_file(file_path, [])
            file_source = True
        except Exception as ex:
            data = None
        if data is None:
            # вызываем метод катомного получения ссылок для секции навигации
            data = self._try_call_customs(code)
            file_source = False
        if not isinstance(data, list):
            data = []

        if data:
            _a = [data]
            if file_source:
                _a.append('asc')
                _a.append('srtid')  # если источник file то наверно специальная сортировка
            # сортировка по labels
            data = self._sort_items(_a)
            data = self.__add_url_prefix(data)
        return data

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

    def _sch_portal_settings(self):
        """
        Метод формирует список ссылок из встроенных модулей
        :return:
        """
        lst = []
        # требуется получить граф с описанием всех модулей
        d = mod_manager.get_available_modules()
        for _m in d:
            if mod_manager.is_external_module(_m):
                continue
            _m_urls = mod_manager.get_mod_admin_urls(_m)
            if _m_urls:
                for _m_url in _m_urls:
                    _tpl = self.get_link_tpl()
                    _tpl['label'] = _m_url['label']
                    _tpl['href'] = _m_url['href']
                    _tpl['roles'] = _m_url['roles']
                    _tpl['code'] = self._url2code(_m_url['href'])
                    lst.append(_tpl)
        if lst:
            _kt = 1
            for _k in range(0, len(lst)):
                lst[_k]['id'] = _kt
                lst[_k]['srtid'] = _kt
                _kt += 1
        return lst

    def _sch_modules_settings(self):
        """
        Метод формирует список ссылок из встроенных модулей
        :return:
        """
        lst = []
        # требуется получить граф с описанием всех модулей
        d = mod_manager.get_available_modules()
        for _m in d:
            if mod_manager.is_internal_module(_m):
                continue
            _m_urls = mod_manager.get_mod_admin_urls(_m)
            if _m_urls:
                for _m_url in _m_urls:
                    _tpl = self.get_link_tpl()
                    _tpl['label'] = _m_url['label']
                    _tpl['href'] = _m_url['href']
                    _tpl['roles'] = _m_url['roles']
                    _tpl['code'] = self._url2code(_m_url['href'])
                    lst.append(_tpl)
        if lst:
            _kt = 1
            for _k in range(0, len(lst)):
                lst[_k]['id'] = _kt
                lst[_k]['srtid'] = _kt
                _kt += 1
        return lst

    @staticmethod
    def _url2code(_url):
        code = ''
        _t = _url.split('/')
        for _it in _t:
            if not _it:
                continue
            code += _it.lower().capitalize()
        return code

    @staticmethod
    def _get_section_items_filename(code):
        """
        Метод возвращает реальный путь к файлу
        :param str code: код секции навигации
        :return: путь к файлу
        :rtype str:
        """
        file_name = code + '.json'
        file_path = os.path.join(AdminConf.get_mod_path('data'), AdminConf.NAVI_DIR_NAME, file_name)
        return file_path

    def has_block_file(self, code):
        _pth = self._get_section_items_filename(code)
        return os.path.exists(_pth) and os.path.isfile(_pth)

    def get_block_filepath(self, code):
        _pth = self._get_section_items_filename(code)
        return _pth

    def get_section_by_code(self, code):
        current = None
        lst = self.get_sections()
        if lst:
            for sec in lst:
                if sec['code'] == code:
                    current = sec
                    break
        return current

    def _tree_snail(self, code):
        roots = self.get_sections_navi(code)
        _t = []
        _like_parent = False
        if roots:
            for root in roots:
                key = root['code']
                _like_parent = (code == key)
                #  предупреждаем зацикленность в одном блоке
                if not _like_parent:
                    leafs = self._tree_snail(key)
                root['childs'] = leafs
                _t.append(root)
        return _t

    def gen_map(self, start=''):
        _t = self._register.split('.')[0]
        if '' == start:
            start = _t
        _a = self._tree_snail(start)
        if _a:
            for _i in _a:
                self._map.append(_i)

    def get_map(self):
        if not self._map:
            self.gen_map()
        return self._map

    def _get_structure(self):
        start = self._register.split('.')[0]
        _t = {}
        _ind = 1
        _indexed = []

        def _snail(code):
            roots = self.get_sections_navi(code)
            if roots:
                _like_parent = False
                for root in roots:
                    _is_indexed = False
                    key = root['code']
                    _like_parent = (code == key)
                    _is_indexed = (key in _indexed)
                    if not _is_indexed:
                        _indexed.append(key)
                    root['parid'] = _t[code]['id'] if code in _t else 0
                    _ind = _indexed.index(key)
                    root['id'] = _ind + 1
                    root['parent'] = code
                    if key not in _t:
                        _t[key] = root
                    #  предупреждаем зацикленность
                    if not _is_indexed and not _like_parent:
                        _snail(key)

        _snail(start)
        return _t

    def get_current_section(self, flask_request):
        current = None
        # надо собрать карту из секций и разделов
        # по подразделам или разделам определить
        # какая секция и какая подсекция
        # if not self._map:
        #     self.gen_map()
        # if self._map:
        if self._navi_struct:
            #print(self._debug_name + ".get_current_section->flask_request.path", flask_request.path)
            match = flask_request.path
            for key, ptn in self._navi_struct.items():
                # print(self._debug_name + ".get_current_section->ptn['href']", ptn['href'])
                if '' == ptn['href']:
                    continue
                _test_href = ptn['href']
                if self._url_prefix and not _test_href.startswith(self._url_prefix):
                    _test_href = self._url_prefix.rstrip('/') + '/' + _test_href.lstrip('/')
                if match.startswith(_test_href):
                    # print(self._debug_name + ".get_current_section->ptn", ptn)
                    if 0 == ptn['parid']:
                        current = ptn
                    else:
                        current = self._navi_struct[ptn['parent']]
                    #print(self._debug_name + ".get_current_section->current", current)
                    break
        return current

    def get_current_subitem(self, flask_request):
        current = None
        # надо собрать карту из секций и разделов
        # по подразделам или разделам определить
        # какая секция и какая подсекция
        # if not self._map:
        #     self.gen_map()
        # if self._map:
        if self._navi_struct:
            # print(self._debug_name + ".get_current_subitem->flask_request.path", flask_request.path)
            match = flask_request.path
            for key, ptn in self._navi_struct.items():
                # print(self._debug_name + ".get_current_subitem->ptn", ptn)
                # print(self._debug_name + ".get_current_subitem->ptn['href']", ptn['href'])
                if '' == ptn['href']:
                    continue
                _test_href = ptn['href']
                if self._url_prefix and not _test_href.startswith(self._url_prefix):
                    _test_href = self._url_prefix.rstrip('/') + '/' + _test_href.lstrip('/')
                # print(self._debug_name + ".get_current_subitem->_test_href", _test_href)
                if match.startswith(_test_href) and 0 < ptn['id']:
                    # print(self._debug_name + ".get_current_subitem->ptn", ptn)
                    current = ptn
                    break
        return current

    def get_sections(self):
        lst = []
        _t = 'admin_sections'
        lst = self.get_sections_navi(_t)
        return lst

    def get_sections_navi(self, section_code):
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
            # print(self._debug_name + '.get_sections_navi.file_source', file_source)
            if file_source:
                _a.append('asc')
                _a.append('srtid') # если источник file то наверно специальная сортировка
            # print(self._debug_name + '.get_sections_navi._a', _a)
            lst = self._sort_items(*_a)
            lst = self.__add_url_prefix(lst)
        return lst

    def __add_url_prefix(self, _lst):
        """
        Метод добавляет к ссылкам url префикс для приложения
        :param list _lst: список элементов навигации
        :return: список элементов навигации
        :rtype list:
        """
        if self._url_prefix:
            def _up_d(x):
                if not x['href']:
                    return x
                if not x['href'].startswith(self._url_prefix):
                    x['href'] = self._url_prefix.rstrip('/') + '/' + x['href'].lstrip('/')
                return x

            _lst = map(_up_d, _lst)
            _lst = list(_lst)
        return _lst

    def get_default_blocks(self):
        """
        Метод возвращает список блоков поумолчанию
        :return:
        """
        ocfg = None
        _path = AdminConf.get_mod_path(AdminConf.INIT_DIR_NAME)
        _path = os.path.join(_path, AdminConf.CONF_DIR_NAME)
        def_config = SomeConfig(_path)
        def_blocks = []
        def_blocks = list((def_config.get('navi.Codes')).values())
        return def_blocks

    def get_navi_blocks(self):
        lst = []
        lst = self.get_file_source()
        return lst

    def remove_navi_item(self, code): pass

    @staticmethod
    def get_link_tpl():
        tpl = {}
        tpl = {"id": 0, "label": "", "rules": "", "href": "", "parid": 0, "srtid": 1,
               "page": [], "icon": "", "thumb": "", "descr": "",
               "url_func": "", "code": "", "roles": ""}
        return tpl

    def is_admin_url(self, search_path):
        flg = False
        lst = []
        # получаем список модулей
        mods_lst = mod_manager.get_available_modules()
        if mods_lst:
            for modx in mods_lst:
                _lst = mod_manager.get_mod_admin_urls(modx)
                lst += _lst
        if lst:
            # print('search_path', search_path)
            _url_prefix = self._url_prefix.rstrip('/')
            for io in lst:
                # print("io['href']", io['href'])
                _to_test = io['href'].rstrip('/') + '/' # добавим slash для правильной части пути
                if _url_prefix and not _to_test.startswith(_url_prefix):
                    _to_test = _url_prefix.rstrip('/') + '/' + _to_test.lstrip('/')
                if search_path.startswith(_to_test):
                    flg = True
                    break
        return flg

    def check_url_access(self, check_url, user):
        flg = False
        urls_lst = mod_manager.get_registred_urls()
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

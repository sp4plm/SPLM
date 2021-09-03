# -*- coding: utf-8 -*-
import os
import json

from app.admin_mgt.admin_conf import AdminConf
from app.utilites.code_helper import CodeHelper
from app import mod_manager


class AdminNavigation(AdminConf):
    _class_file = __file__
    _debug_name = 'AdminNavigation'

    def __init__(self):
        self._files_path = os.path.join(AdminConf.DATA_PATH, 'navi')
        self.sections = []
        self.current_section = None
        self.section_navi = []
        self.current_section_navi = None
        self._map = []
        self.gen_map()

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
        except Exception as ex:
            data = None
        if data is None:
            # вызываем метод катомного получения ссылок для секции навигации
            data = self._try_call_customs(code)
        if not isinstance(data, list):
            data = []

        if data:
            # сортировка по labels
            data = self._sort_items(data)
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
        file_name = code + '.json'
        file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
        return file_path

    def get_section_by_code(self, code):
        current = None
        lst = self.get_sections()
        if lst:
            for sec in lst:
                if sec['code'] == code:
                    current = sec
                    break
        return current

    def gen_map(self):
        lst = self.get_sections()
        if lst:
            _id = 0
            for sec in lst:
                code = sec['code']
                navi = self.get_sections_navi(code)
                _id += 1
                sec['id'] = _id
                sec['mapid'] = _id-1
                sec['parid'] = -1
                self._map.append(sec)
                if navi:
                    for ni in navi:
                        _id += 1
                        ni['id'] = _id
                        ni['mapid'] = _id-1
                        ni['parid'] = sec['mapid']
                        self._map.append(ni)

    def get_current_section(self, flask_request):
        current = None
        # надо собрать карту из секций и разделов
        # по подразделам или разделам определить
        # какая секция и какая подсекция
        if not self._map:
            self.gen_map()
        if self._map:
            #print("flask_request.path", flask_request.path)
            match = flask_request.path
            for ptn in self._map:
                #print("ptn['href']", ptn['href'])
                if match.startswith(ptn['href']):
                    #print("ptn", ptn)
                    if -1 == ptn['parid']:
                        current = ptn
                    else:
                        current = self._map[ptn['parid']]
                    #print("current", current)
                    break
        return current

    def get_current_subitem(self, flask_request):
        current = None
        # надо собрать карту из секций и разделов
        # по подразделам или разделам определить
        # какая секция и какая подсекция
        if not self._map:
            self.gen_map()
        if self._map:
            # print("flask_request.path", flask_request.path)
            match = flask_request.path
            for ptn in self._map:
                # print("ptn['href']", ptn['href'])
                if match.startswith(ptn['href']) and 0 < ptn['mapid']:
                    # print("ptn", ptn)
                    current = ptn
                    break
        return current

    def get_sections(self):
        lst = []
        sections_file = 'admin_sections.json'
        sections_path = os.path.join(self._files_path, sections_file)
        if CodeHelper.check_file(sections_path):
            lst = self._read_json_file(sections_path, [])
        return lst

    def get_sections_navi(self, section_code):
        lst = []
        sections_file = section_code + '.json'
        sections_path = os.path.join(self._files_path, sections_file)
        if CodeHelper.check_file(sections_path):
            lst = self._read_json_file(sections_path, [])
        else:
            """ выполняем поиск функциональности? которая вернет список ссылок для кода """
            lst = self._try_call_customs(section_code)
        if lst:
            lst = self._sort_items(lst)
        return lst

    def get_navi_blocks(self):
        lst = []
        sections_file = 'navi_blocks.json'
        sections_path = os.path.join(self._files_path, sections_file)
        if CodeHelper.check_file(sections_path):
            lst = self._read_json_file(sections_path, [])
        return lst

    def _read_json_file(self, file_path, default=''):
        data = None
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf8') as fp:
                _cont = fp.read()
                if _cont:
                    try:
                        data = json.loads(_cont)
                    except Exception as ex:
                        raise Exception(self._debug_name + '._read_json_file.Exception: {}'.format(str(ex)))
        if data is None:
            data = default
        return data

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
            print('search_path', search_path)
            for io in lst:
                print("io['href']", io['href'])
                if search_path.startswith(io['href']):
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

# -*- coding: utf-8 -*-:
import os
import rdflib

from datetime import datetime

from app.utilites.code_helper import CodeHelper


class Manager:
    _class_file=__file__
    _debug_name='ModuleManager'
    _description_file = 'dublin.ttl'

    def __init__(self, flask_app=None):
        from time import time
        _t = time()
        # print(self._debug_name + '.__init__', _t)
        if flask_app is not None:
            self._init_flask_app(flask_app)
        # теперь надо посомтреть файл кеша созданный при запуске системы
        # если файл есть то его пытаемся загрузить в _modules
        # надо определить требуется ли восстанавливаться из кеша
        if self._check_cache_file():
            if 'modules_ttl' in self._current_app.config and 0 == len(self._current_app.config['modules_ttl']):
                self._restore_cache()
        self._work_g = None # временное хранение графа - части общего описания всех модулей
        self._web_handlers_file = 'views.py'
        self._web_handlers_var = 'mod'

    def _init_flask_app(self, flask_app):
        self._current_app = flask_app

        class _SingletonState:
            _class_file = __file__
            _debug_name = 'ModuleManagerState'

            def __init__(self, module_manager):
                self.module_manager = module_manager

        self._current_app.extensions['SPLMModuleManager'] = _SingletonState(self)

    def _get_mod_name(self):
        SELF_PATH = os.path.dirname(self._class_file)
        MOD_NAME = os.path.basename(SELF_PATH)
        return MOD_NAME

    def get_modules_register(self):
        _reg = []
        _inf0 = self._current_app.config['modules_ttl']
        if 0 < len(_inf0):
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _mods = _inf0.subjects(predicate=rdflib.RDF.type, object=OSPLM.Module)
            for _t in _mods:
                mod_row = {}
                mod_row['name'] = _t.split('#')[1]
                mod_row['title'] = self._parse_rdflib_gen(_inf0.objects(subject=_t, predicate=rdflib.DC.title))
                mod_row['description'] = self._parse_rdflib_gen(_inf0.objects(subject=_t, predicate=rdflib.DC.description))
                mod_row['label'] = self._parse_rdflib_gen(_inf0.objects(subject=_t, predicate=rdflib.RDFS.label))
                mod_row['lic'] = self._parse_rdflib_gen(_inf0.objects(subject=_t, predicate=rdflib.DC.rights))
                _mod_v = self._parse_rdflib_gen(_inf0.objects(subject=_t, predicate=OSPLM.versionInfo))
                _vers = self.__parse_mod_version(_mod_v)
                mod_row['version'] = _vers['number']
                _reg.append(mod_row)
        return _reg

    def __parse_mod_version(self, _v_str):
        _vers = None
        # example: $Id: 0.0.0 0 0000-00-00 00:00:00Z $
        _norm = str(_v_str)
        _norm = _norm.strip('$')
        _norm = _norm[4:].strip()
        _t = _norm.split(' ')
        _len_t = len(_t)
        _vers = {}
        _vers['number'] = _t[0]
        _vers['inumber'] = '0'
        _vers['date'] = '0000-00-00'
        _vers['time'] = '00:00:00Z'
        if 1 < _len_t:
            if 10 == len(_t[1]) and '-' == _t[1][4] and '-' == _t[1][7]:
                _vers['date'] = _t[1]
            else:
                _vers['inumber'] = _t[1]
        if 2 < _len_t:
            _vers['date'] = _t[2]
        if 3 < _len_t:
            _vers['time'] = _t[3]
        return _vers

    def load_modules_http_handlers(self):
        mods_list = self._current_app.config['modules_list']
        if mods_list:
            for _mod in mods_list:
                if self.is_internal_module(_mod):
                    continue
                # по идее тут можно выбрать из описания модулей информацию о том что загружать
                load_flag = self.load_module_http_handler(_mod)
                if not load_flag:
                    print(self._debug_name + '.load_modules_http_handlers: Web handlers are not loaded for {}'.format(_mod))

    def get_mod_blueprint(self, mod_name):
        _blue_print = None
        if not self.module_exists(mod_name):
            return _blue_print
        _inf0 = self._current_app.config['modules_ttl']
        if 0 < len(_inf0):
            mod_uri = self._get_mod_uri(mod_name)
            mod_uri = mod_uri.lstrip('<').rstrip('>')
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _mod_http = _inf0.triples((rdflib.URIRef(mod_uri), OSPLM.httpEnabled, rdflib.URIRef(str(rdflib.namespace.XSD) + 'true')))
            load_http_mod = None
            if 0 < len([_r for _r in _mod_http]):
                try:
                    load_http_mod = self.__dyn_load_mod_file(mod_name, self._web_handlers_file)
                except Exception as ex:
                    print(self._debug_name + '.get_mod_blueprint: {}' . format(str(ex)))
                    load_http_mod = None
            if load_http_mod is not None:
                try:
                    _blue_print = getattr(load_http_mod, self._web_handlers_var)
                except KeyError as e:
                    # можно также присвоить значение по умолчанию вместо бросания исключения
                    # raise ValueError(self._debug_name + '.load_module_http_handler: No web module var: {}'.format(e.args[0]))
                    print(self._debug_name + '.get_mod_blueprint: No web module var: {}'.format(str(e)))
        return _blue_print

    def load_module_http_handler(self, mod_name):
        flg = False
        # if not self.module_exists(mod_name):
        #     return flg
        _http = None
        try:
            _http = self.get_mod_blueprint(mod_name)
        except Exception as ex:
            print(self._debug_name + '.load_module_http_handler.Exception: {}'.format(str(ex)))
            _http = None
        if _http is None:
            return flg
        # _inf0 = self._current_app.config['modules_ttl']
        # if 0 < len(_inf0):
        #     mod_uri = self._get_mod_uri(mod_name)
        #     mod_uri = mod_uri.lstrip('<').rstrip('>')
        #     OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
        #     _mod_http = _inf0.triples((rdflib.URIRef(mod_uri), OSPLM.httpEnabled, rdflib.URIRef(str(rdflib.namespace.XSD) + 'true')))
        #     load_http_mod = None
        #     if 0 < len([_r for _r in _mod_http]):
        #         try:
        #             load_http_mod = self.__dyn_load_mod_file(mod_name, self._web_handlers_file)
        #         except Exception as ex:
        #             print(self._debug_name + '.load_module_http_handler: {}' . format(str(ex)))
        #             load_http_mod = None
        if _http is not None:
            # try:
            #     views_mod = getattr(load_http_mod, self._web_handlers_var)
            # except KeyError as e:
            #     # можно также присвоить значение по умолчанию вместо бросания исключения
            #     # raise ValueError(self._debug_name + '.load_module_http_handler: No web module var: {}'.format(e.args[0]))
            #     print(self._debug_name + '.load_module_http_handler: No web module var: {}'.format(str(e)))
            # call app.register_blueprint(views_mod)
            try:
                self._current_app.register_blueprint(_http)
                flg = True
            except Exception as ex:
                # можно также присвоить значение по умолчанию вместо бросания исключения
                # raise ValueError('Undefined component: {}'.format(e.args[0]))
                print(self._debug_name + '.load_module_http_handler: Error on module web register action:', str(ex))
        return flg

    def compile_modules_info(self):
        from flask import Flask
        if not isinstance(self._current_app, Flask):
            return
        mods_list = {}
        mods_list = self. _get_app_modules()
        # собираем граф о всех модулях системы
        self._current_app.config['modules_ttl'] = rdflib.Graph()
        # собираем информацию о всех модулях системы? нужную для системы
        self._current_app.config['modules_info'] = {}
        if mods_list:
            for mn, mt in mods_list.items():
                self._current_app.config['modules_ttl'] = self._current_app.config['modules_ttl'].parse(data=mt, format="n3")
            # нужно сделать дамп
            self._current_app.config['modules_list'] = list(mods_list.keys())
            # требуется создать файл для кеширования данных о модулях приложения
            self._dump_cache()

    def get_described_roles(self):
        """
        Метод возвращает список ролей из описания модулей проекта
        :return:
        """
        lst = []
        _inf0 = self._current_app.config['modules_ttl']
        if 0 < len(_inf0):
            # osplm:hasAccessRight
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _q = """
            PREFIX osplm: <%s>
            SELECT ?m ?r WHERE {
                ?u osplm:hasAccessRight ?r .
                ?m osplm:hasURL ?u .
            }
            """ % self._get_app_uri()
            # mods_roles = _inf0.query(_q)
            # _t = []
            # for _r in mods_roles:
            #     _t = _r.asdict()
            #     _mod = str(_t['m']).replace(str(OSPLM), '').strip()
            #     lst.append([_mod, str(_t['r'])])
            # print(self._debug_name + '.get_described_roles: lst', lst)
            lst = []
            mods_roles = _inf0.subject_objects(predicate=OSPLM.hasAccessRight)
            lst = [it[1] for it in mods_roles]
            pass
        return lst

    def module_exists(self, mod_name):
        return True if mod_name in self._current_app.config['modules_list'] else False

    def is_external_module(self, mod_name):
        flg = False
        flg = self.module_exists(mod_name)
        if flg:
            flg = mod_name.startswith('mod_')
        return flg

    def is_internal_module(self, mod_name):
        flg = False
        flg = not self.is_external_module(mod_name)
        return flg

    def get_mod_api(self, modname):
        """
        Функция форвращает экземпляр класса ModApi модуля modname описанного в файле mod_api
         расположеного в корне модуля modname
        :param modname: string имя модуля
        :return: None или экземпляр класса ModApi
        """
        from time import sleep
        if not self.module_exists(modname):
            raise ModuleNotFoundError('Undefined component: {}'.format(modname))
        api_mod_ext = 'py'
        api_mod_name = 'mod_api'
        comp_mod = self.__dyn_load_mod_file(modname, api_mod_name + '.' + api_mod_ext)
        try:
            obj_comp = getattr(comp_mod, 'ModApi')()
        except AttributeError as e:
            # можно также присвоить значение по умолчанию вместо бросания исключения
            obj_comp = self._get_empty_api()()
            # raise ValueError('Undefined component: {}'.format(e.args[0]))
        return obj_comp

    def __dyn_load_mod_file(self, import_mod: str, file_name=None):
        if file_name is None:
            file_name = import_mod + '.py' # may be use __init__.py
        mod_path = os.path.join(self._get_mods_path(), import_mod)
        if not os.path.exists(mod_path) or not os.path.isdir(mod_path):
            raise ModuleNotFoundError(self._debug_name + '.__dyn_load_mod_file: Undefined module: {}'.format(import_mod))
        load_path = os.path.join(mod_path, file_name)
        from importlib import invalidate_caches, import_module, util as impmod_utils

        if not os.path.exists(load_path) or not os.path.isfile(load_path):
            return None
        mod_not_found = False
        if impmod_utils.find_spec(import_mod) is None:
            mod_not_found = True
        try:
            invalidate_caches()
            if not mod_not_found:
                comp_mod = import_module(import_mod)
            else:
                _fname = os.path.basename(file_name)
                _fname = _fname[:_fname.rfind('.')]
                load_name = os.path.basename(os.path.dirname(mod_path)) + '.' + import_mod + '.' + _fname
                module_spec = impmod_utils.spec_from_file_location(load_name, load_path)
                comp_mod = impmod_utils.module_from_spec(module_spec)
                module_spec.loader.exec_module(comp_mod)

        except Exception as ex:
            from traceback import format_exc
            print(self._debug_name + '.__dyn_load_mod_file.LoadFileEx: format_exc()-> {}'.format(format_exc()))
            raise ModuleNotFoundError(self._debug_name + '.__dyn_load_mod_file.LoadFileEx: {}'.format(ex.args))
        return comp_mod

    def _get_empty_api(self):

        class ModEmptyApi:
            _class_file = __file__
            _debug_name = 'ModManager.ModEmptyApi'
        return ModEmptyApi

    def get_mod_decscription(self, mod_name):
        """
        Функция возвращает описание модуля с именем mod_name, хранящееся в dublin.ttl модуля
        :param mod_name: string: Имя модуля для получения описания - dublin.ttl
        :return: None или rdflib.Graph() Если модуля нет то None, если модуль есть то rdflib.Graph()
        rdflib.Graph() - может оказаться пустым, если модуль есть а dublin.ttl отсутствует
        """
        mod_root = os.path.join(self._get_mods_path(), mod_name)
        mod_descr = None
        if not os.path.exists(mod_root) or not os.path.isdir(mod_root):
            return mod_descr
        try_mod = os.path.join(mod_root, self._description_file)
        mod_descr = rdflib.Graph()
        if not os.path.exists(try_mod) and not os.path.isfile(try_mod):
            return mod_descr
        # теперь читаем
        with open(try_mod, 'r', encoding='utf8') as fp:
            mod_descr.parse(file=fp, format="n3") # load(fp, format="n3") - deprecated fron 6.0
        return mod_descr

    def _get_graph_namespaces(self, graph):
        nss = {}
        lst_ns = graph.namespace_manager.namespaces()
        for ns in lst_ns:
            short = ''
            short = str(ns[0])
            long = ''
            long = str(ns[1].toPython())
            cns = {'short': short, 'long': long}
            nss[short] = cns
        return nss

    def _resolve_graph_ns(self, graph, short_ns):
        lst_ns = self._get_graph_namespaces(graph)
        resolved = None
        if lst_ns:
            if short_ns in lst_ns:
                cns = lst_ns[short_ns]
                resolved = rdflib.Namespace(cns['long'])
        if resolved is None and 'osplm' == short_ns:
            resolved = rdflib.Namespace('http://splm.portal.web/osplm')
        return resolved

    def get_mod_open_urls(self, mod_name):
        """
        Метод возвращает список URL модуля, доступных для указания в меню портала различного уровня.
        :param mod_name:  string: имя модуля - имя директории в директории приложения
        :return: список URL модуля, доступных для указания в меню портала
        """
        opened = []
        # _inf0 = self.get_mod_decscription(mod_name) # читать напрямую ttl файл модуля
        _inf0 = self._current_app.config['modules_ttl']
        self._work_g = _inf0
        if 0 < len(_inf0):
            mod_uri = self._get_mod_uri(mod_name)
            mod_uri = mod_uri.lstrip('<').rstrip('>')
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _mod_urls = _inf0.objects(subject=rdflib.URIRef(mod_uri), predicate=OSPLM.hasURL)
            mod_urls = [url for url in _mod_urls]
            _urls = _inf0.subjects(predicate=OSPLM.shallBeShownInMenu, object=rdflib.URIRef(str(rdflib.namespace.XSD) + 'true'))
            open_urls = [url for url in _urls]
            if 0 == len(open_urls):
                XS = rdflib.Namespace(str(rdflib.namespace.XSD))
                _urls = _inf0.subjects(predicate=OSPLM.shallBeShownInMenu, object=rdflib.URIRef(str(XS) + 'true'))
                open_urls = [url for url in _urls]
            _urls = [_u for _u in open_urls if _u in mod_urls] # оставляем только URL указанного модуля
            opened = self._compile_mod_urls(_urls)
        return opened

    def get_mod_admin_urls(self, mod_name):
        """
        Метод созвращает список URL  модуля, предназначенных для административного интерфейса
        :param mod_name: string: имя модуля - имя директории в директории приложения
        :return: список URL модуля для административного интерфейса
        """
        # print(self._debug_name + '.get_mod_admin_urls: call')
        res = []
        _inf0 = self._current_app.config['modules_ttl']
        self._work_g = _inf0
        if 0 < len(_inf0):
            mod_uri = self._get_mod_uri(mod_name)
            mod_uri = mod_uri.lstrip('<').rstrip('>')
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _mod_urls = _inf0.objects(subject=rdflib.URIRef(mod_uri), predicate=OSPLM.hasURL)
            mod_urls = [url for url in _mod_urls]
            _urls = _inf0.subjects(predicate=OSPLM.forAdminPurpose, object=rdflib.URIRef(str(rdflib.namespace.XSD) + 'true'))
            adm_urls = [url for url in _urls]
            if 0 == len(adm_urls):
                XS = rdflib.Namespace(str(rdflib.namespace.XSD))
                _urls = _inf0.subjects(predicate=OSPLM.forAdminPurpose, object=rdflib.URIRef(str(XS) + 'true'))
                adm_urls = [url for url in _urls]
            _urls = [_u for _u in adm_urls if _u in mod_urls] # оставляем только URL указанного модуля
            res = self._compile_mod_urls(_urls)
        return res

    def get_registred_urls(self):
        res = []
        _inf0 = self._current_app.config['modules_ttl']
        self._work_g = _inf0
        if 0 < len(_inf0):
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _urls = _inf0.subjects(predicate=rdflib.namespace.RDF.type, object=OSPLM.URL)
            list_urls = [url for url in _urls]
            if list_urls:
                res = self._compile_mod_urls(_urls)
        return res

    def get_start_url(self):
        _url = ''
        _inf0 = self._current_app.config['modules_ttl']
        self._work_g = _inf0
        # print(self._debug_name + '.get_start_urls->START')
        if 0 < len(_inf0):
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _q = """SELECT ?mod ?url WHERE {
                ?mod <%s> ?ourl .
                ?ourl <%s> xsd:true .
                ?ourl rdfs:label ?url .
            }""" % (OSPLM.hasStartURL, OSPLM.isActive)
            _urls_info = _inf0.query(_q)
            _t = []
            for _r in _urls_info:
                _t = list(_r)
                break  # only first
            if _t:
                _mod = ''
                _met = ''
                _mod = str(_t[0]).replace(str(OSPLM), '').strip()
                _met = str(_t[1])
                # модуль является папкой и может не являться загруженным модулем Blueprint!
                _http = self.get_mod_blueprint(_mod)
                if _http is not None:
                    _mod = _http.name
                _url = _mod + '.' + _met
        # print(self._debug_name + '.get_start_urls->END')
        return _url

    def __get_registred_blueprints(self):
        _lst = []
        if self._current_app and hasattr(self._current_app, 'blueprints'):
            for name in self._current_app.blueprints:
                _lst.append(self._current_app.blueprints[name])
        return _lst

    def __get_app_mods_blueprints(self):
        _lst_blue = self.__get_registred_blueprints()
        _appmods_blues = {}
        for _blue in _lst_blue:
            blue_name = _blue.name
            appmod_name = os.path.basename(_blue.root_path)
            _appmods_blues[appmod_name] = blue_name
        return _appmods_blues

    def get_start_endpoints(self):
        _ends = []
        _inf0 = self._current_app.config['modules_ttl']
        self._work_g = _inf0
        # print(self._debug_name + '.get_start_urls->START')
        if 0 < len(_inf0):
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _q = """SELECT ?mod ?url WHERE {
                ?mod <%s> ?ourl .
                ?ourl rdfs:label ?url .
            }""" % (OSPLM.hasStartURL)
            _urls_info = _inf0.query(_q)
            _t = []
            for _r in _urls_info:
                _t.append(list(_r))
            if _t:
                # self._current_app.blueprints #
                _app_mods_blues = self.__get_app_mods_blueprints()
                for _u in _t:
                    _url = ''
                    if 2 == len(str(_u[1]).split('.')):
                        _url = str(_u[1])
                    else:
                        _mod = ''
                        _met = ''
                        _mod = str(_u[0]).replace(str(OSPLM), '').strip()
                        # модуль является папкой и может не являться загруженным модулем Blueprint!
                        _mod = self.get_real_mod_webname(_mod)
                        _met = str(_u[1])
                        _url = _mod + '.' + _met
                    if _url:
                        _ends.append(_url)
        # print(self._debug_name + '.get_start_urls->END')
        return _ends

    def get_real_mod_webname(self, app_mod_name):
        """
        Метод возвращает имя модуля blueprint (зарегистрированного) для указанного модуля приложения app_mod_name
        :param app_mod_mname: имя модуля приложения
        :return: имя модуля(зарегистрированного) blueprint
        """
        _name = ''
        _app_mods_blues = self.__get_app_mods_blueprints()
        if _app_mods_blues:
            _name = _app_mods_blues[app_mod_name]
        else:
            # значит пытаемся загрузить
            _http = self.get_mod_blueprint(app_mod_name)
            if _http is not None:
                _name = _http.name
        return _name

    def _compile_mod_urls(self, urls):
        res = []
        OSPLM = self._resolve_graph_ns(self._work_g, 'osplm')
        for url in urls:
            _url = {'href': '', 'label': '', 'roles': []}
            _url['href'] = self._parse_rdflib_gen(self._work_g.objects(subject=url, predicate=OSPLM.value))
            if not isinstance(_url['href'], str):
                _url['href'] = str(_url['href'])
            _url['label'] = self._parse_rdflib_gen(self._work_g.objects(subject=url, predicate=rdflib.namespace.RDFS.label))
            if not isinstance(_url['label'], str):
                _url['label'] = str(_url['label'])
            _roles = self._work_g.objects(subject=url, predicate=OSPLM.hasAccessRight)
            if _roles:
                for _role in _roles:
                    code = _role
                    if isinstance(code, str):
                        _url['roles'].append(str(code))
                    if isinstance(code, list):
                        _url['roles'] += code
            res.append(_url)
        return res

    def _parse_rdflib_gen(self, rdflib_gen):
        res = None
        _t = []
        for it in rdflib_gen:
            _t.append(str(it))
        if 1 == len(_t):
            _t = _t[0]
        return _t

    def _get_app_modules(self, mod=0):
        """
        Функция возвращает словарь где ключь имя модуля, а значение - содержание файла dublin.ttl модуля.
        Существует три режима работы функции mod:
        0 - (режим по умолчанию) - возвращает описание всех модулей приложения;
        -1 - возвращает описание внутренних модулей;
        1 - возвращает описание сторонних модулей (имя модуля начинается с "mod_").
        :param mod: int: - режим работы функции
        :return: dict: словарь с описанием модулей
        """
        mods_list = {}
        mods_path = self._get_mods_path()
        pak_list = os.scandir(mods_path)
        for item in pak_list:

            if not item.is_dir():
                continue
            if 0 !=mod:
                # -1 только внутренние
                # 1 только сторонние
                if -1 == mod and item.name.startswith('mod_'):
                    continue
                if 1 == mod and not item.name.startswith('mod_'):
                    continue
            mod_root = os.path.join(mods_path, item.name)
            try_mod = os.path.join(mod_root, self._description_file)
            if not os.path.exists(try_mod) and not os.path.isfile(try_mod):
                continue
            # теперь читаем
            mod_uri = self._get_mod_uri(item.name)
            with open(try_mod, 'r', encoding='utf8') as fp:
                graph_descr = rdflib.Graph()
                graph_descr.parse(file=fp, format="n3") # load(fp, format="n3") - deprecated fron 6.0
                qres = []
                if 0 < len(graph_descr):
                    qres = graph_descr.query(
                        'SELECT ?label WHERE { ' + mod_uri + ' rdfs:label ?label . }')
                if qres:
                    # чтобы файл не оказался пустым
                    # https://stackoverflow.com/questions/24570066/calculate-md5-from-werkzeug-datastructures-filestorage-without-saving-the-object
                    fp.seek(0)
                    mods_list[item.name] = fp.read()
        return mods_list

    def _get_mod_uri(self, mod_name):
        app_uri = self._get_app_uri()
        uri = '<{}{}>' . format(app_uri, mod_name)
        return uri

    @staticmethod
    def _get_app_uri():
        uri = 'http://splm.portal.web/osplm#'
        return uri

    def get_available_modules(self):
        return self._current_app.config['modules_list']

    def get_drivers_modules(self):
        # print(self._debug_name + '.get_drivers_modules->START')
        _lst = []
        _inf0 = self._current_app.config['modules_ttl']
        self._work_g = _inf0
        if 0 < len(_inf0):
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _k = 'mod'
            _q = """SELECT ?%s WHERE {
                ?mod <%s> ?type . FILTER (?type="driver")
            }""" % (_k, str(OSPLM.type))
            # print(self._debug_name + '.get_drivers_modules->_q', _q)
            _urls_info = _inf0.query(_q)
            for _r in _urls_info:
                _t = _r.asdict().get(_k, '')
                if not _t:
                    continue
                mod = str(_t).replace(str(OSPLM), '')
                _lst.append(mod)
        return _lst

    def get_drivers_by_subj(self, _subj):
        # print(self._debug_name + '.get_drivers_by_subj->START')
        _lst = []
        _drivers = self.get_drivers_modules()
        #  ожидаем список строк
        _inf0 = self._current_app.config['modules_ttl']
        self._work_g = _inf0
        if 0 < len(_inf0) and _drivers:
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _filter_var = '?mod'
            _filter = ' || ' . join([_filter_var + '=<' + str(OSPLM[_m]) + '>' for _m in _drivers])
            _filter = 'FILTER (' + _filter + ')'
            _k = _filter_var.lstrip('?')
            _q = """SELECT ?%s WHERE {
                ?%s rdf:type <%s> . %s
                ?%s dc:subject ?subj . FILTER (?subj="%s")
            }""" % (_k, _k, str(OSPLM.Module), _filter, _k, str(_subj))
            # print(self._debug_name + '.get_drivers_by_subj->_q', _q)
            _urls_info = _inf0.query(_q)
            for _r in _urls_info:
                _t = _r.asdict().get(_k, '')
                if not _t:
                    continue
                mod = str(_t).replace(str(OSPLM), '')
                _lst.append(mod)
        return _lst

    def query(self, _txt):
        _res = None
        _inf0 = self._current_app.config['modules_ttl']
        if 0 < len(_inf0):
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            try:
                _t = _inf0.query(_txt)
                _res = []
                for _r in _t:
                    _tr = _r.asdict()
                    _res.append(_tr)
            except Exception as ex:
                raise Exception(ex)
        return _res

    def _dump_cache(self):
        """"""
        # формируем имя файла кеша
        cache_file = ''
        cache_file = self._get_cache_file()
        if self._check_cache_file():
            os.unlink(cache_file)
        # print('cache_file', cache_file)
        # print(self._debug_name + '._dump_cache.modules:', self._current_app.config['modules_list'])
        # сохраняем собранную информацию в файл кеша
        self._current_app.config['modules_ttl'].serialize(destination=cache_file, format="turtle")

    def _restore_cache(self):
        """"""
        cache_file = self._get_cache_file()
        with open(cache_file, 'r', encoding='utf8') as fp:
            self._current_app.config['modules_ttl'] = rdflib.Graph()
            self._current_app.config['modules_ttl'].parse(file=fp, format="n3") # load(fp, format="n3") - deprecated fron 6.0
            # по идее надо восстановить содержание и modules_list и modules_info ??!
            if 0 < len(self._current_app.config['modules_ttl']):
                OSPLM = self._resolve_graph_ns(self._current_app.config['modules_ttl'], 'osplm')
                if OSPLM is None:
                    OSPLM = rdflib.Namespace('http://splm.portal.web/osplm')
                mods = self._current_app.config['modules_ttl'].subjects(rdflib.namespace.RDF.type, OSPLM.Module)
                lst = self._parse_rdflib_gen(mods)
                app_uri = self._get_app_uri()
                self._current_app.config['modules_list'] = [m.replace(app_uri, '') for m in lst]
                self._current_app.config['modules_info'] = {}

    def _check_cache_file(self):
        """"""
        return os.path.exists(self._get_cache_file())

    def _get_cache_file(self):
        cache_file = ''
        cache_file = os.path.join(self._get_data_path(), self._gen_cache_filename())
        return cache_file

    def _get_mods_path(self):
        pth = os.path.join(self._current_app.config['APP_ROOT'], 'app')
        return pth

    def _get_data_path(self):
        from app import app_api
        # pth = os.path.join(os.path.dirname(self._class_file), 'data')
        pth = app_api.get_mod_data_path(self._get_mod_name())
        if not os.path.exists(pth):
            os.mkdir(pth)
        return pth

    def _gen_cache_filename(self):
        # нужно переделать с применением ключа приложения
        app_instance_key = self._current_app.secret_key
        file_name = 'cache_' + CodeHelper.str_to_hash('cache_file_' + app_instance_key)
        return file_name

    def _to_log(self, msg, _point=''):
        if not os.path.exists(_point):
            if hasattr(self, '__log'):
                _point = getattr(self, '__log')
            else:
                _point = os.path.join(os.path.dirname(__file__), 'debug.log')
        if not os.path.exists(_point):
            with open(_point, 'w', encoding='utf-8') as fp:
                fp.write('')
        time_point = datetime.now().strftime("%Y%m%d %H-%M-%S")
        msg = '[{}] {}'.format(time_point, msg)
        with open(_point, 'a', encoding='utf-8') as fp:
            fp.write(msg + "\n")

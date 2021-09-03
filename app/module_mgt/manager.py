# -*- coding: utf-8 -*-:
import os
import rdflib

from app.utilites.code_helper import CodeHelper


class Manager:
    _class_file=__file__
    _debug_name='ModuleManager'
    _description_file = 'dublin.ttl'

    def __init__(self, flask_app=None):
        if flask_app is not None:
            self._init_flask_app(flask_app)
        # теперь надо посомтреть файл кеша созданный при запуске системы
        # если файл есть то его пытаемся загрузить в _modules
        # надо определить требуется ли восстанавливаться из кеша
        if self._check_cache_file():
            self._restore_cache()
            # compile_modules_info - перезапишет все данные из кеша
        self._work_g = None # временное хранение графа - части общего описания всех модулей

    def _init_flask_app(self, flask_app):
        self._current_app = flask_app

        class _SingletonState:
            _class_file = __file__
            _debug_name = 'ModuleManagerState'

            def __init__(self, module_manager):
                self.module_manager = module_manager

        self._current_app.extensions['SPLMModuleManager'] = _SingletonState(self)

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
                # print('mn', mn)
                # print('mt', mt)
                self._current_app.config['modules_ttl'] = self._current_app.config['modules_ttl'].parse(data=mt, format="n3")
            # нужно сделать дамп
            self._current_app.config['modules_list'] = mods_list.keys()

            # print(self._current_app.config['modules_ttl'].serialize(destination='output.txt', format="turtle"))

            # требуется создать файл для кеширования данных о модулях приложения
            self._dump_cache()

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
        if not self.module_exists(modname):
            raise ModuleNotFoundError('Undefined component: {}'.format(modname))
        api_mod_ext = 'py'
        api_mod_name = 'mod_api'
        mod_path = os.path.join(self._get_mods_path(), modname)
        if not os.path.exists(mod_path) or not os.path.isdir(mod_path):
            return None
        load_path = os.path.join(mod_path, api_mod_name + '.' + api_mod_ext)
        spec_path = 'app.' + modname + '.' + api_mod_name
        from importlib import invalidate_caches, import_module, util as impmod_utils
        if not os.path.exists(load_path) or not os.path.isfile(load_path):
            return None
        try:
            invalidate_caches()
            module_spec = impmod_utils.spec_from_file_location(
                api_mod_name, load_path
            )
            comp_mod = impmod_utils.module_from_spec(module_spec)
            module_spec.loader.exec_module(comp_mod)
        except ModuleNotFoundError as ex:
            raise ModuleNotFoundError('Undefined component: {}'.format(ex.args[0]))
        try:
            obj_comp = getattr(comp_mod, 'ModApi')()
        except AttributeError as e:
            # можно также присвоить значение по умолчанию вместо бросания исключения
            obj_comp = self._get_empty_api()()
            # raise ValueError('Undefined component: {}'.format(e.args[0]))
        return obj_comp

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
            mod_descr.load(fp, format="n3")
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
            _urls = _inf0.subjects(predicate=OSPLM.shallBeShownInMenu, object=rdflib.namespace.XSD.true)
            _urls = [_u for _u in _urls if _u in mod_urls] # оставляем только URL указанного модуля
            opened = self._compile_mod_urls(_urls)
        return opened

    def get_mod_admin_urls(self, mod_name):
        """"""
        res = []
        _inf0 = self._current_app.config['modules_ttl']
        self._work_g = _inf0
        if 0 < len(_inf0):
            mod_uri = self._get_mod_uri(mod_name)
            mod_uri = mod_uri.lstrip('<').rstrip('>')
            OSPLM = self._resolve_graph_ns(_inf0, 'osplm')
            _mod_urls = _inf0.objects(subject=rdflib.URIRef(mod_uri), predicate=OSPLM.hasURL)
            mod_urls = [url for url in _mod_urls]
            _urls = _inf0.subjects(predicate=OSPLM.forAdminPurpose, object=rdflib.namespace.XSD.true)
            _urls = [_u for _u in _urls if _u in mod_urls] # оставляем только URL указанного модуля
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
                    # code = self._parse_rdflib_gen(self._work_g.objects(subject=_role, predicate=rdflib.namespace.RDFS.label))
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
                graph_descr.load(fp, format="n3")
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
        # self._restore_cache() # при создании экземпляра восстанавливаемся из кеша
        return self._current_app.config['modules_list']

    def _dump_cache(self):
        """"""
        # формируем имя файла кеша
        cache_file = ''
        cache_file = self._get_cache_file()
        # print('cache_file', cache_file)
        # сохраняем собранную информацию в файл кеша
        self._current_app.config['modules_ttl'].serialize(destination=cache_file, format="turtle")

    def _restore_cache(self):
        """"""
        cache_file = self._get_cache_file()
        with open(cache_file, 'r', encoding='utf8') as fp:
            self._current_app.config['modules_ttl'] = rdflib.Graph()
            self._current_app.config['modules_ttl'].load(fp, format="n3")
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
        pth = os.path.join(os.path.dirname(self._class_file), 'data')
        if not os.path.exists(pth):
            os.mkdir(pth)
        return pth

    def _gen_cache_filename(self):
        # нужно переделать с применением ключа приложения
        app_instance_key = self._current_app.secret_key
        file_name = 'cache_' + CodeHelper.str_to_hash('cache_file_' + app_instance_key)
        return file_name

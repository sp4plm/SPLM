# -*- coding: utf-8 -*-:
import os
from requests import get, post

from .utilites import Utilites
from app import app_api


class DataUploadManager:
    _class_file=__file__
    _debug_name='DataUploadManager'
    _upload_file_name = 'files[]' # customize for storage - this one to Fuseki
    _graph_name_prefix = 'graph' # Неиспользуется
    _graph_name_prefix_iri = 'http://splm.portal.web/osplm/graph#' # Неиспользуется

    def __init__(self):
        self._app_cfg = app_api.get_app_config()
        self._upload_list = [] # список файлов для загрузки
        self._update_list = [] # список файлов для обновления данных
        self._storage_driver = None # инструмент загрузки файлов в хранилище
        self._use_named_graphs = False # флаг использования именных графов при загрузке файлов
        self._upload_results = {} # результат загрузки
        self._upload_errors = {} # ошибки при загрузке
        self._log_function = None # инструмент записи действий в файл
        self._use_store_auth = False # использовать для измененя хранилища авторизацию
        self._store_user = ''
        self._store_secret = ''
        self._debug_mode = False
        self._last_downloaded = ''
        self._init_storage_driver()

    def update(self):
        """ Ожидаем словарь с """
        if self._update_list:
            # вызываем инструмент загрузки файлов
            if not self._check_storage_driver():
                self._init_storage_driver()
            self._storage_driver.use_named_graphs = self._use_named_graphs

    def upload(self):
        """ Ожидаем список полных имен файлов для загрузки """
        if self._upload_list:
            # вызываем инструмент загрузки файлов
            if not self._check_storage_driver():
                self._init_storage_driver()
            self._storage_driver.use_named_graphs = self._use_named_graphs
            for fi in self._upload_list:
                up_flg = self._upload_func(fi)
                file_name = self._get_file_name(fi)
                if up_flg:
                    self._upload_results[file_name] = fi
                else:
                    self._upload_errors[file_name] = fi

    def _upload_func(self, file_path):
        flg = False
        if self._check_storage_driver():
            flg = self._storage_driver.upload_file(file_path)
        else:
            self._to_log('_upload_func: Storage driver is not defined!')
        return flg

    def upload_file(self, file_path):
        return self._upload_func(file_path)

    def clear_named_graph_data(self, graph_name):
        """ clear named graph """
        graph_name = graph_name.lstrip('<').rstrip('>')
        query = 'DELETE { GRAPH <' + graph_name + '> { ?s ?p ?o } } WHERE { ?s ?p ?o . }'
        self._to_log(self._debug_name + '.clear_named_graph_data: try send clear graph request!')
        self._to_log(self._debug_name + '.clear_named_graph_data: request is ->' + query)
        return self.exec_query(query)

    def cook_graph_name(self, item):
        g_name = ''
        g_name = self._storage_driver.cook_graph_name(item)
        return g_name

    def exec_query(self, query, endpoint=''):
        """ send a query to the triple store """
        if self._storage_driver is None:
            return None
        return self._storage_driver.query(query)

    def _init_storage_driver(self):
        _store_cred = ''
        try:
            self._storage_driver = Utilites.get_storage_driver()
            if self._storage_driver is not None:
                self._storage_driver.set_portal_onto_uri(app_api.get_portal_onto_uri())
            _store_cred = self._app_cfg.get('data_storages.Accounts.main')
        except Exception as ex:
            self._to_log('_init_storage_driver: Can not get storage driver - Exception: ' + str(ex))
        if '' != _store_cred:
            _use_store_auth = True  # использовать для измененя хранилища авторизацию
            parsed_cred = self._get_parsed_store_credential(_store_cred)
            _store_user = parsed_cred[0]
            _store_secret = parsed_cred[1]
            if self._storage_driver is not None:
                self._storage_driver.use_auth_admin = _use_store_auth
                self._storage_driver.set_auth_credential(_store_user, _store_secret)

    def call_after_modify_storage_triggers(self):
        if self._storage_driver is not None:
            try:
                self._storage_driver.call_after_modify_storage_triggers()
            except Exception as ex:
                raise ex

    def set_storage_driver(self, _driver):
        if _driver is not None:
            self._storage_driver = _driver

    def _check_storage_driver(self):
        return self._storage_driver is not None

    def get_upload_result(self):
        return self._upload_results

    def get_upload_errors(self):
        return self._upload_errors

    @staticmethod
    def _get_file_name(file_path):
        name = ''
        if '' != file_path:
            name = os.path.basename(file_path)
        return name

    def clear_upload_list(self):
        self._upload_list = []

    def set_upload_list(self, lst):
        flg = False
        _t = []
        if lst:
            for _i in lst:
                if not os.path.exists(_i):
                    continue
                _t.append(_i)
        if _t:
            self._upload_list = _t
        return flg

    def update_upload_list(self, file_path):
        flg = False
        if os.path.exists(file_path):
            if file_path not in self._upload_list:
                self._upload_list.append(file_path)
                flg = True
        return flg

    def _to_log(self, msg):
        msg = self._debug_name + '.' + msg
        if callable(self._log_function):
            self._log_function(msg)
        else:
            print(msg)

    def set_log_function(self, log_function):
        if callable(log_function):
            self._log_function = log_function

    @staticmethod
    def _get_parsed_store_credential(to_parse):
        parsed = []
        semi_ind = to_parse.find(':')
        uname = to_parse[0:semi_ind]
        usecret = to_parse[semi_ind+1:]
        parsed.append(uname)
        parsed.append(usecret)
        return parsed

    def download_file(self, target_file):
        flg = False
        if self._storage_driver is not None:
            flg = self._storage_driver.backup_to_file(target_file)
            if flg:
                """ надо сохранить полученый файл """
                self._last_downloaded = self._storage_driver.get_last_downloaded_file()
        return flg

    def get_last_downloaded_file(self):
        return self._last_downloaded

    @property
    def use_named_graph(self):
        return self._use_named_graph

    @use_named_graph.setter
    def use_named_graph(self, flg):
        self._use_named_graph = bool(flg)
        if self._storage_driver is not None:
            self._storage_driver.use_named_graph = bool(flg)

    def clear_storage(self):
        """ """
        query = '''DELETE { ?s ?p ?o } WHERE { ?s ?p ?o . }'''
        return self.exec_query(query)

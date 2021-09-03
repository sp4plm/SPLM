# -*- coding: utf-8 -*-

import os

from app import app_api
from app.utilites.data_upload_manager import DataUploadManager
from .module_conf import PublishModConf

from app.publish_mgt.files_managment import FilesManagment


class DataManager(PublishModConf):
    """ """
    _class_file = __file__
    _debug_name = 'PublishDataManager'

    def __init__(self):
        self._log_func = None
        self._timer_file = ''
        self._app_cfg = app_api.get_app_config()
        self._meta = FilesManagment()
        self._use_named_graph = False
        self._use_store_auth = False # использовать для измененя хранилища авторизацию
        self._last_downloaded = ''
        self._app_data_manager = None
        self._init_app_data_manager()

    def _init_app_data_manager(self):
        if self._app_data_manager is None:
            self._app_data_manager = DataUploadManager()

    def set_log_func(self, trigger):
        """"""
        if callable(trigger):
            self._log_func = trigger

    def to_log(self, msg):
        if callable(self._log_func):
            self._log_func(self._debug_name +': {}' . format(msg))
        #print(msg)

    def clear_named_graph_data(self, graph_name):
        """ clear named graph """
        return self._app_data_manager.clear_named_graph_data(graph_name)

    def cook_graph_name(self, item):
        g_name = ''
        g_name = self._app_data_manager.cook_graph_name(item)
        return g_name

    def _download_file(self, target_file):
        flg = False
        if self._app_data_manager is not None:
            flg = self._app_data_manager.download_file(target_file)
            if flg:
                """ надо сохранить полученый файл """
                self._last_downloaded = self._app_data_manager.get_last_downloaded_file()
                print(self._debug_name +'._download_file.last_downloaded', self._last_downloaded)
            self.to_log('Try make backup to file {} result: {}'.format(target_file, flg))
        return flg

    def get_last_downloaded_file(self):
        return self._last_downloaded

    @property
    def use_named_graph(self):
        return self._use_named_graph

    @use_named_graph.setter
    def use_named_graph(self, flg):
        self._use_named_graph = bool(flg)
        if self._app_data_manager is not None:
            self._app_data_manager.use_named_graph = bool(flg)

    def _exec_query(self, query, endpoint=''):
        """ send a query to the triple store """
        # TODO: вызов через query_mgt!
        if self._app_data_manager is None:
            return None
        return self._app_data_manager.exec_query(query)

    def _upload_file2(self, file_path, url=''):
        """ """
        flg = False
        # теперь передадим управление драйверу хранилища
        if self._app_data_manager is not None:
            flg = self._app_data_manager.upload_file(file_path)
        return flg

    def _clear_storage(self):
        """ """
        return self._app_data_manager.clear_storage()

# -*- coding: utf-8 -*-

import os
from time import time, strftime, localtime

from .data_manager import DataManager


class DataBackuper(DataManager):
    """ """
    _class_file = __file__

    def __init__(self):
        super().__init__()

    def to_log(self, msg):
        if callable(self._log_func):
            self._log_func('DataBackuper: {}' . format(msg))
        #print(msg)

    def create(self, file_name):
        """ """
        flg = False
        flg = self._download_file(file_name)
        return flg

    def restore(self, file_name):
        """ """
        flg = False
        if os.path.exists(file_name) and os.path.isfile(file_name):
            # сперва очищаем хранилище
            self._clear_storage()
            # потом загружаем файл
            # хак для разворачивания резервной копии выключаем режим именнованных графов
            last_named_graphs = self.use_named_graph
            self.use_named_graph = False
            flg = self._upload_file2(file_name)
            self.use_named_graph = last_named_graphs
        return flg

    @staticmethod
    def generate_filename():
        return 'backup_' + strftime("%Y%m%d_%H-%M-%S", localtime(time())) + '-' + '.ttl';

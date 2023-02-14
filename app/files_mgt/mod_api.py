# -*- coding: utf-8 -*-
import os


class ModApi:
    _class_file = __file__
    _debug_name = 'FilesMgtModApi'

    def get_util(self):
        """
        Функция возвращает ......

        :return:
        :rtype:
        """
        from .data_files import DataFiles
        return DataFiles

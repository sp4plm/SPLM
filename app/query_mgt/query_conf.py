# -*- coding: utf-8 -*-
import os
from app import app_api

class QueryConf:
    _class_file = __file__
    _debug_name = 'QueryConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/query'

    DESCRIPTION_FILE = os.path.join(SELF_PATH, 'dublin.ttl')
    SPARQT_DATA_PATH = os.path.join(SELF_PATH, 'sparqt')


    @staticmethod
    def get_web_tpl_path():
        """
        Метод отдает путь до html шаблонов (templates) для текущего модуля

        :return: абсолютный путь до templates
        :rtype: str
        """
        pth = QueryConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_web_static_path():
        """
        Метод отдает путь до статических файлов (static) для текущего модуля

        :return: абсолютный путь до static
        :rtype: str
        """
        pth = QueryConf.get_mod_path('static')
        return pth

    @staticmethod
    def get_mod_path(relative):
        """
        Метод отдает абсолютный путь до папок текущего модуля

        :param str relative: относительный путь внутри самого модуля.
        :return: абсолютный путь до relative
        :rtype: str
        """
        pth = os.path.join(QueryConf.SELF_PATH, relative.lstrip(os.path.sep))
        return pth

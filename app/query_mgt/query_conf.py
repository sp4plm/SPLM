# -*- coding: utf-8 -*-
import os
from app import app_api

class QueryConf:
    _class_file = __file__
    _debug_name = 'QueryConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/portal/manager'

    DESCRIPTION_FILE = os.path.join(SELF_PATH, 'dublin.ttl')
    SPARQT_DATA_PATH = os.path.join(SELF_PATH, 'sparqt')


    @staticmethod
    def get_web_tpl_path():
        pth = QueryConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_web_static_path():
        pth = QueryConf.get_mod_path('static')
        return pth

    @staticmethod
    def get_mod_path(relative):
        pth = os.path.join(QueryConf.SELF_PATH, relative.lstrip(os.path.sep))
        return pth

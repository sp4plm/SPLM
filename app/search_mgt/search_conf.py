# -*- coding: utf-8 -*-
import os

class SearchConf:
    _class_file = __file__
    _debug_name = 'SearchConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/' + MOD_NAME

    DESCRIPTION_FILE = os.path.join(SELF_PATH, 'dublin.ttl')

    SEARCH_BY_CODE_QUERY = 'query_mgt.app.search_by_code'
    SEARCH_BY_CODE_VAR = 'CODE'
    OBJECT_VIEW = 'splm_nav.uri_class'


    @staticmethod
    def get_mod_tpl_path():
        pth = SearchConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_mod_data_path():
        pth = SearchConf.get_mod_path('data')
        return pth

    @staticmethod
    def get_mod_static_path():
        pth = SearchConf.get_mod_path('static')
        return pth

    @staticmethod
    def get_mod_path(relative):
        pth = os.path.join(SearchConf.SELF_PATH, relative.lstrip(os.path.sep))
        return pth

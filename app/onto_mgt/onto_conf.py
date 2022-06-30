# -*- coding: utf-8 -*-
import os
from app import app_api

class OntoConf:
    _class_file = __file__
    _debug_name = 'OntoConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/onto'

    # DATA_PATH = os.path.join(SELF_PATH, 'data')
    DESCRIPTION_FILE = os.path.join(SELF_PATH, 'dublin.ttl')

    @staticmethod
    def get_web_tpl_path():
        pth = OntoConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_mod_path(relative):
        relative = relative.lstrip(os.path.sep)
        pth = os.path.join(OntoConf.SELF_PATH, relative)
        _k = 'data'
        if relative.startswith(_k):
            from app import app_api
            d_pth = app_api.get_mod_data_path(OntoConf.MOD_NAME)
            pth = os.path.join(d_pth, relative.replace(_k + os.path.sep, ''))
        return pth

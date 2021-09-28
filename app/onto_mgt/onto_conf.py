# -*- coding: utf-8 -*-
import os
from app import app_api

class OntoConf:
    _class_file = __file__
    _debug_name = 'OntoConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/onto'

    DATA_PATH = os.path.join(SELF_PATH, 'data')
    DESCRIPTION_FILE = os.path.join(DATA_PATH, 'dublin.ttl')

    @staticmethod
    def get_web_tpl_path():
        pth = OntoConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_mod_path(relative):
        pth = os.path.join(OntoConf.SELF_PATH, relative.lstrip(os.path.sep))
        return pth

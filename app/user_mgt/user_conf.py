# -*- coding: utf-8 -*-
import os
from app import app_api


class UserConf:
    _class_file = __file__
    _debug_name = 'UserConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/users'

    DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/mod_models')
    LOG_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/logs')

    @staticmethod
    def get_web_tpl_path():
        pth = UserConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_web_static_path():
        pth = UserConf.get_mod_path('static')
        return pth

    @staticmethod
    def get_mod_path(relative):
        pth = os.path.join(UserConf.SELF_PATH, relative.lstrip(os.path.sep))
        return pth
# -*- coding: utf-8 -*-
import os


class PublishModConf:
    _class_file = __file__
    _debug_name = 'PublishModConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)

    MOD_WEB_ROOT = '/publisher'

    DATA_PATH = os.path.join(SELF_PATH, 'data')

    @staticmethod
    def get_root_tpl():
        pth = 'publisher_index.html'
        return pth

    @staticmethod
    def get_web_tpl_path():
        pth = PublishModConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_web_static_path():
        pth = PublishModConf.get_mod_path('static')
        return pth

    @staticmethod
    def get_mod_path(relative):
        pth = os.path.join(PublishModConf.SELF_PATH, relative.lstrip(os.path.sep))
        return pth

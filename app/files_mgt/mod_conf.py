# -*- coding: utf-8 -*-
import os


class ModConf:
    _class_file = __file__
    _debug_name = 'ModConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/mediadata'

    _MAX_FILE_SIZE = 1024 * 1024 * 50
    _ALLOWED_EXTENSIONS = ('jpg', 'jpeg', 'xml', 'png', 'gif', 'mp4', 'docx', 'doc',
                           'pdf', 'ttl', 'xls', 'xlsx', 'dotm', 'dot', 'm4v', 'rq', 'xlsm')

    @staticmethod
    def get_web_tpl_path():
        pth = ModConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_web_static_path():
        pth = ModConf.get_mod_path('static')
        return pth

    @staticmethod
    def get_mod_path(relative):
        relative = relative.lstrip(os.path.sep)
        pth = os.path.join(ModConf.SELF_PATH, relative)
        _k = 'data'
        if relative.startswith(_k):
            from app import app_api
            d_pth = app_api.get_mod_data_path(ModConf.MOD_NAME)
            pth = os.path.join(d_pth , relative.replace(_k, '').lstrip(os.path.sep))
        return pth

# -*- coding: utf-8 -*-
import os


class ModConf:
    _class_file = __file__
    _debug_name = 'ModConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/mediadata'

    _MAX_FILE_SIZE = 1024 * 1024 + 50
    _ALLOWED_EXTENSIONS = ('jpg', 'jpeg', 'xml', 'png', 'gif', 'docx', 'doc', 'pdf', 'ttl', 'xls', 'xlsx')

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
        pth = os.path.join(ModConf.SELF_PATH, relative.lstrip(os.path.sep))
        return pth

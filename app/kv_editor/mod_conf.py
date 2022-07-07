# -*- coding: utf-8 -*-
import os


class ModConf:
    _class_file = __file__
    _debug_name = 'KVEditorConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/' + MOD_NAME

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

    @staticmethod
    def get_editor_tpl():
        return os.path.join(ModConf.MOD_NAME, 'edit_form.html')

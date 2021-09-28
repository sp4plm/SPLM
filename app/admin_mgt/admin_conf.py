# -*- coding: utf-8 -*-
import os

class AdminConf:
    _class_file = __file__
    _debug_name = 'AdminConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/portal'

    INIT_DIR_NAME = 'defaults'
    DATA_DIR_NAME = 'data'
    CONF_DIR_NAME = 'cfg'
    NAVI_DIR_NAME = 'navi'
    DATA_PATH = os.path.join(SELF_PATH, DATA_DIR_NAME)
    CONFIGS_PATH = os.path.join(DATA_PATH, CONF_DIR_NAME)
    DESCRIPTION_FILE = os.path.join(DATA_PATH, 'dublin.ttl')

    ADMIN_NAVI_BLOCK_CODE = 'admin_sections'
    PORTAL_NAVI_BLOCK_CODE = 'navi_blocks'

    @staticmethod
    def get_root_tpl():
        pth = 'admin_mgt-base.html'
        return pth

    @staticmethod
    def get_web_tpl_path():
        pth = AdminConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_web_static_path():
        pth = AdminConf.get_mod_path('static')
        return pth

    @staticmethod
    def get_mod_path(relative):
        pth = os.path.join(AdminConf.SELF_PATH, relative.lstrip(os.path.sep))
        return pth

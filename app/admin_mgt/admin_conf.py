# -*- coding: utf-8 -*-
import os
from app import app_api

class AdminConf:
    _class_file = __file__
    _debug_name = 'AdminConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/portal/management'

    DATA_PATH = os.path.join(SELF_PATH, 'data')
    CONFIGS_PATH = os.path.join(DATA_PATH, 'cfg')
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

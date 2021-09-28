# -*- coding: utf-8 -*-
from .some_config import SomeConfig
from app.admin_mgt.admin_conf import AdminConf
from app.admin_mgt.portal_navigation import PortalNavigation


class PortalNavi:
    _class_file = __file__
    _debug_name = 'PortalNavi'

    @staticmethod
    def get_portal_navi(code, user=None):
        """"""
        data = []
        portal_navi = PortalNavigation()
        section = portal_navi.get_section_by_code(code)
        if section:
            data = portal_navi.get_sections_navi(code, user)
        if data:
            data = PortalNavi.sort_obj_lst(data)
        return data

    @staticmethod
    def get_main_navi(user):
        """"""
        data = {}
        code = 'navi.Codes.main_navi'
        data = PortalNavi._get_navi_block_links(code, user)
        return data

    @staticmethod
    def get_top_navi(user):
        """"""
        data = {}
        code = 'navi.Codes.top_navi'
        data = PortalNavi._get_navi_block_links(code, user)
        return data

    @staticmethod
    def get_user_custom_navi(user):
        """"""
        data = {}
        code = 'navi.Codes.user_navi'
        data = PortalNavi._get_navi_block_links(code, user)
        return data

    @staticmethod
    def _get_navi_block_links(conf_key, user):
        try:
            app_cfg = PortalNavi._get_app_conf()
            block_code = app_cfg.get(conf_key)
            data = PortalNavi.get_portal_navi(block_code, user)
        except Exception as ex:
            print(PortalNavi._debug_name + '._get_navi_block_links.Exception: ', ex)
            data = []
        return data

    @staticmethod
    def _get_app_conf():
        app_cfg = SomeConfig(AdminConf.CONFIGS_PATH)
        return app_cfg

    @staticmethod
    def sort_obj_lst(_lst, ord='asc', attr='srtid'):
        sort_result = []
        sort_result = _lst
        revers = True if 'asc' != ord else False
        sort_result = sorted(sort_result, key=lambda x: x[attr], reverse=revers)
        return sort_result

    @staticmethod
    def get_admin_endpoint():
        return 'admin_mgt.index'
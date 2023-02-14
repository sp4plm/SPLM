# -*- coding: utf-8 -*-
from .some_config import SomeConfig
from app.admin_mgt.admin_conf import AdminConf
from app.admin_mgt.portal_navigation import PortalNavigation

import re
from flask import url_for, request

class PortalNavi:
    _class_file = __file__
    _debug_name = 'PortalNavi'

    @staticmethod
    def get_portal_navi(code, user=None):
        """
        Метод возвращает содержимое секции по коду

        :param code:
        :param user:
        :return:
        """
        data = []
        portal_navi = PortalNavigation()
        section = portal_navi.get_section_by_code(code)
        if section:
            data = portal_navi.get_sections_navi(code, user)
        if data:
            data = PortalNavi.sort_obj_lst(data)
        return data

    @staticmethod
    def get_current_navi_item():
        _item = None
        from flask import request
        if request is not None:
            portal_navi = PortalNavigation()
            _item = portal_navi.get_current_item(request)
        return _item

    @staticmethod
    def get_brothers(navi_item, user):
        _lst = []
        portal_navi = PortalNavigation()
        _lst = portal_navi.get_brothers(navi_item, user)
        return _lst

    @staticmethod
    def navi_item_is_section(navi_item):
        _flg = False
        portal_navi = PortalNavigation()
        _flg = portal_navi.is_section(navi_item)
        return _flg

    @staticmethod
    def get_main_navi(user):
        """"""
        data = {}
        code = 'navi.Codes.main_navi'
        data = PortalNavi._get_navi_block_links(code, user)
        if data:
            for _i in range(0, len(data)):
                # если отключили принудительно отображать детей в выпадающем меню
                if 'DisDropdown' in data[_i] and 1==data[_i]['DisDropdown']:
                    continue
                _childs = PortalNavi.get_portal_navi(data[_i]['code'], user)
                if _childs:
                    data[_i]['childs'] = _childs
        return data

    @staticmethod
    def get_navi_map(user):
        """
        Метод возвращает все пункты навигации начиная с разделов сайта в виде одноуровневого словаря.
        Ключи словаря - коды пунктов навигации, а значения - сами пункты навигации.
        Все пункты навигации связаны между собой спомощью двух пар ключей: id-parid и code-parent.
        Пункты собираются с учетов указанного пользователя - user

        :param user: пользователь для проверки доступа к пунктам навигации
        :return: одноуровневый словарь: ключ - код пункта навигации, значение - пункт навигации
        """
        _map = {}
        portal_navi = PortalNavigation()
        app_cfg = PortalNavi._get_app_conf()
        navi_code = app_cfg.get('navi.Codes.main_navi')
        _map = portal_navi.get_all_navi(navi_code, user)
        return _map

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
        app_cfg = SomeConfig(AdminConf.get_configs_path())
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

    @staticmethod
    def get_mod_tpl_path(mod_name, tpl_name):
        if False == tpl_name.find('.'):
            tpl_name += '.html'
        portal_navi = PortalNavigation()
        return portal_navi.get_tpl_path(mod_name, tpl_name)

    @staticmethod
    def get_start_url():
        url = '/'
        portal_navi = PortalNavigation()
        _cfg = PortalNavi._get_app_conf()
        try:
            _t = _cfg.get('main.Info.mainpage')
            url = _t
            _url = portal_navi.get_portal_index_url()
            if '/' == url and _url and '/' != _url:
                url = _url
        except Exception as ex:

            print(PortalNavi._debug_name + '.get_start_url.Exception: ', ex)
            url = '/'
        return url

    @staticmethod
    def get_start_urls():
        urls = []
        portal_navi = PortalNavigation()
        try:
            urls = portal_navi.get_portal_index_urls()
        except Exception as ex:
            print(PortalNavi._debug_name + '.get_start_urls.Exception: ', ex)
            urls = []
        return urls

    @staticmethod
    def get_start_tpl():
        _tpl = ''
        portal_navi = PortalNavigation()
        _cfg = PortalNavi._get_app_conf()
        try:
            # имя шаблона получать из настроек
            # _t = _cfg.get('main.Info.mainpage')
            _tpl = portal_navi.get_portal_index_tpl_name()
        except Exception as ex:
            print(PortalNavi._debug_name + '.get_start_tpl.Exception: ', ex)
            _tpl = 'index.html'
        return _tpl

    @staticmethod
    def _cook_navi_url(item):
        if 'url_func' in item and "" != item['url_func']:

            try:
                url = item['url_func'].split("?")
                params = {}

                # разбор параметров url
                if len(url) > 1:
                    for param in url[1].split("&"):
                        values = param.split("=")
                        params[values[0]] = values[1]

                url = url_for(url[0], **params)

            except:
                url = item['href']

        else:
            url = item['href']

        return url
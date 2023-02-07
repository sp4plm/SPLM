# -*- coding: utf-8 -*-
import os

class AdminConf:
    """
    Класс описывающий конфигурацию административного модуля портала
    """
    _class_file = __file__
    _debug_name = 'AdminConf'

    SELF_PATH = os.path.dirname(_class_file)
    MOD_NAME = os.path.basename(SELF_PATH)
    MOD_WEB_ROOT = '/portal'

    INIT_DIR_NAME = 'defaults'
    DATA_DIR_NAME = 'data'
    CONF_DIR_NAME = 'cfg'
    NAVI_DIR_NAME = 'navi'
    # DATA_PATH = os.path.join(SELF_PATH, DATA_DIR_NAME)
    # CONFIGS_PATH = get_mod_path(DATA_DIR_NAME + os.path.sep + CONF_DIR_NAME)  # os.path.join(DATA_PATH, CONF_DIR_NAME)
    DESCRIPTION_FILE = os.path.join(SELF_PATH, 'dublin.ttl')

    ADMIN_NAVI_BLOCK_CODE = 'admin_sections'
    PORTAL_NAVI_BLOCK_CODE = 'navi_blocks'
    BUILD_FILE_NAME="build_v"

    @staticmethod
    def get_root_tpl():
        """
        Метод возвращает путь к базовому шаблону административного модуля в директории шаблонов модуля
        :return: путь к базовому шаблону модуля
        :rtype str:
        """
        pth = os.path.join(AdminConf.MOD_NAME, 'admin_mgt-base.html')
        pth = AdminConf.__correct_template_path(pth)
        return pth

    @staticmethod
    def get_web_tpl_path():
        """
        Метод возвращает абсолютный путь до templates директории модуля
        :return: абсолютный путь
        :rtype str:
        """
        pth = AdminConf.get_mod_path('templates')
        return pth

    @staticmethod
    def get_web_static_path():
        """
        Метод возвращает абсолютный путь до static директории модуля
        :return: абсолютный путь
        :rtype str:
        """
        pth = AdminConf.get_mod_path('static')
        return pth

    @staticmethod
    def get_mod_path(relative):
        """
        Метод возвращает абсолютный путь для переданного относительного relative
        :param str relative: относительный путь (внутри модуля)
        :return: абсолютный путь
        :rtype str:
        """
        relative = relative.lstrip(os.path.sep)
        pth = os.path.join(AdminConf.SELF_PATH, relative)
        _k = 'data'
        if relative.startswith(_k):
            from app import app_api
            d_pth = app_api.get_mod_data_path(AdminConf.MOD_NAME)
            relative = relative.replace(_k, '')
            pth = os.path.join(d_pth , relative.lstrip(os.path.sep))
        return pth

    @staticmethod
    def get_configs_path():
        """
        Метод возвращает путь до директории с конфигурационными файлами
        :return: путь к директории
        :rtype str:
        """
        return AdminConf.get_mod_path(AdminConf.INIT_DIR_NAME + os.path.sep + AdminConf.CONF_DIR_NAME)

    @staticmethod
    def __correct_template_path(_tmpl):
        """
        Функция предназначена для коректировки пути шаблонов
        :param str _tmpl: относительный путь к html шаблону
        :return: скорректированный путь
        :rtype str:
        """
        from sys import platform
        from os import path
        if "win32" == platform:
            # так как
            # from flak_themes2/__init__.py return render_template("_themes/%s/%s" % (theme, template_name), **context)
            # преобразуем путь к соответствующему шаблону
            _tmpl = _tmpl.replace(path.sep, path.altsep)
        return _tmpl

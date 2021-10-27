# -*- coding: utf-8 -*-
from app.admin_mgt.admin_conf import os, AdminConf


class ConfiguratorUtils(AdminConf):
    _class_file = __file__
    _debug_name = 'ConfiguratorUtils'

    @staticmethod
    def get_webeditor_endpoint():
        return 'portal_configurator.edit_settings_view'

    @staticmethod
    def get_configurator_navi():
        lst = []
        conf_list = ConfiguratorUtils.get_configs_list()
        for ci in conf_list:
            tpl = {}
            tpl['label'] = ci
            tpl['href'] = ci
            tpl['roles'] = []
            tpl['code'] = 'Config_' + ci
            lst.append(tpl)
        return lst

    @staticmethod
    def check_config(conf_name):
        conf_list = ConfiguratorUtils.get_configs_list()
        return conf_name in conf_list

    @staticmethod
    def get_conf_file(conf_name):
        work_dir = AdminConf.CONFIGS_PATH
        files_list = ConfiguratorUtils.get_configs_files()
        pth = ''
        for fi in files_list:
            lp = fi.rfind('.')
            if fi[:lp] == conf_name:
                pth = os.path.join(work_dir, fi)
        return pth

    @staticmethod
    def get_configs_list():
        lst = []
        files_list = ConfiguratorUtils.get_configs_files()
        for fi in files_list:
            lp = fi.rfind('.')
            lst.append(fi[:lp])
        return lst

    @staticmethod
    def get_configs_files():
        work_dir = AdminConf.CONFIGS_PATH
        files_list = [fi.name for fi in os.scandir(work_dir)]
        return files_list

    @staticmethod
    def is_default_conf(config_name):
        _defaults = ConfiguratorUtils.get_default_configs()
        return config_name in _defaults

    @staticmethod
    def get_default_configs():
        lst = []
        _path = AdminConf.get_mod_path(AdminConf.INIT_DIR_NAME)
        _path = os.path.join(_path, AdminConf.CONF_DIR_NAME)
        files_list = [fi.name for fi in os.scandir(_path)]
        for fi in files_list:
            lp = fi.rfind('.')
            lst.append(fi[:lp])
        return lst

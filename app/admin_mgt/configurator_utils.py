# -*- coding: utf-8 -*-
from app.utilites.some_config import SomeConfig
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
        _cfg = None
        try:
            _cfg = ConfiguratorUtils._read_configs()
        except Exception as ex:
            print(ConfiguratorUtils._debug_name +'.get_configurator_navi: ', ex.args[0])
            _cfg = None
        for ci in conf_list:
            tpl = {}
            _lbl = ci
            if _cfg is not None:
                try:
                    _k = 'prj_labels.SettingFiles.' + ci
                    _lbl = _cfg.get(_k)
                except Exception as ex:
                    # print(ConfiguratorUtils._debug_name +'.get_configurator_navi: ', ex.args[0])
                    _lbl = ci
            tpl['label'] = _lbl
            tpl['href'] = ci
            tpl['roles'] = []
            tpl['code'] = 'Config_' + ci
            lst.append(tpl)
        if lst:
            lst = sorted(lst, key=lambda x: x['label'])
        return lst

    @staticmethod
    def check_config(conf_name):
        conf_list = ConfiguratorUtils.get_configs_list()
        return conf_name in conf_list

    @staticmethod
    def get_conf_file(conf_name):
        work_dir = ConfiguratorUtils._get_mod_configs_path()  # AdminConf.CONFIGS_PATH
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
        work_dir = ConfiguratorUtils._get_mod_configs_path()  # AdminConf.CONFIGS_PATH
        _available = ConfiguratorUtils._get_available_files_ext()
        files_list = []
        for fi in os.scandir(work_dir):
            if not fi.is_file():
                continue
            fi_ext = fi.name[fi.name.rfind('.')+1:]
            if fi_ext not in _available:
                continue
            files_list.append(fi.name)
        if files_list:
            files_list = sorted(files_list)
        return files_list

    @staticmethod
    def _get_available_files_ext():
        lst = []
        _str = 'ini, json'
        try:
            _cfg = ConfiguratorUtils._read_configs()
            _str = _cfg.get('main.Info.SettingFiles')
        except Exception as ex:
            print(ConfiguratorUtils._debug_name +'._get_available_files_ext: ', ex.args[0])
            _str = 'ini, json'
        lst = list(map(str.strip, _str.split(',')))
        return lst

    @staticmethod
    def is_default_conf(config_name):
        _defaults = ConfiguratorUtils.get_default_configs()
        return config_name in _defaults

    @staticmethod
    def get_default_configs():
        lst = []
        _path = ConfiguratorUtils._get_mod_configs_path()
        files_list = [fi.name for fi in os.scandir(_path)]
        for fi in files_list:
            lp = fi.rfind('.')
            lst.append(fi[:lp])
        return lst

    @staticmethod
    def _read_configs():
        _cfg = None
        _path = ConfiguratorUtils._get_mod_configs_path()
        _cfg = SomeConfig(_path)
        return _cfg

    @staticmethod
    def _get_configs_path():
        return ConfiguratorUtils._get_mod_configs_path()
        # _has_files = False
        # _path = AdminConf.CONFIGS_PATH
        # if os.path.exists(_path):
        #     files_list = [fi.name for fi in os.scandir(_path)]
        #     if 0 < len(files_list):
        #         _has_files = True
        # if not _has_files:
        #     _path = AdminConf.get_mod_path(AdminConf.INIT_DIR_NAME)
        #     _path = os.path.join(_path, AdminConf.CONF_DIR_NAME)
        #     files_list = [fi.name for fi in os.scandir(_path)]
        #     if 0 == len(files_list):
        #         raise Exception('Отсутствуют первичные файлы конфигурации!')
        # return _path

    @staticmethod
    def _get_mod_configs_path():
        _pth = ConfiguratorUtils.get_mod_path(ConfiguratorUtils.INIT_DIR_NAME)
        _pth = os.path.join(_pth, ConfiguratorUtils.CONF_DIR_NAME)
        return _pth

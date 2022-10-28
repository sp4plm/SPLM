# -*- coding: utf-8 -*-
import os
import json
import configparser

from app.utilites.code_helper import CodeHelper
from app import app_api
from app.admin_mgt.admin_conf import AdminConf
from app.admin_mgt.admin_navigation import AdminNavigation
from app.admin_mgt.users_auth_logger import UsersAuthLogger
from app.admin_mgt.auth_provider import AuthProvider
from app.module_mgt.manager import Manager


class AdminUtils(AdminConf):
    _class_file = __file__
    _debug_name = 'AdminUtils'

    # @staticmethod
    # def get_current_sectionin_tpl(flask_request):
    #     lst = {}
    #     admin_navi = AdminNavigation()
    #     lst = admin_navi.get_current_section(flask_request)
    #     return lst

    # @staticmethod
    # def get_current_subitem_tpl(flask_request):
    #     lst = {}
    #     admin_navi = AdminNavigation()
    #     lst = admin_navi.get_current_subitem(flask_request)
    #     return lst

    # @staticmethod
    # def get_admin_current_section(code):
    #     lst = []
    #     current = {}
    #     admin_navi = AdminNavigation()
    #     lst = admin_navi.get_sections()
    #     if lst:
    #         for blk in lst:
    #             if blk['code'] == code:
    #                 current = blk
    #                 break
    #     return current

    # @staticmethod
    # def get_admin_section_navi(code):
    #     lst = []
    #     admin_navi = AdminNavigation()
    #     lst = admin_navi.get_sections_navi(code)
    #     return lst

    @staticmethod
    def get_build_version():
        _app_pth = AdminUtils.__get_app_path()
        _build_file = os.path.join(_app_pth, AdminConf.BUILD_FILE_NAME)
        _v = 'splm-00000000'
        if os.path.exists(_build_file):
            with open(_build_file, 'r', encoding='utf-8') as _fp:
                _v = _fp.read().strip("\n\r")
        return _v


    @staticmethod
    def _get_navi_path():
        pth = ''
        pth = AdminConf.get_mod_path(os.path.join('default', 'navi'))
        if not os.path.exists(pth):
            os.mkdir(pth)
        return pth

    @staticmethod
    def _get_navi_block_content(code):
        items = []
        file_name = code + '.json'
        # получаем настоящий путь к файлу
        file_path = app_api.get_meta_path('admin_mgt', os.path.join('navi', file_name)) # os.path.join(AdminUtils._get_navi_path(), file_name)
        if os.path.exists(file_path):
            content = CodeHelper.read_file(file_path)
            if content:
                items = json.loads(content)
        return items

    @staticmethod
    def _get_navi_block_info(code):
        block = {}
        blocks = AdminUtils.get_portal_sections()
        if blocks:
            for blk in blocks:
                if blk['code'] == code:
                    block = blk
                    break
        return block

    @staticmethod
    def get_navi_block(code):
        block = {}
        block = AdminUtils._get_navi_block_info(code)
        if 'code' in block and '' != block['code']:
            block['items'] = AdminUtils._get_navi_block_content(code)
        return block

    @staticmethod
    def get_site_all_navi():
        res = []
        # получаем все блоки навигации для портала
        portal_navis = AdminUtils.get_portal_sections()
        if portal_navis:
            for blk in portal_navis:
                """"""
                compile_blk = blk
                compile_blk = AdminUtils._compile_navi_block(compile_blk['code'])
                res.append(compile_blk)
        return res

    @staticmethod
    def _compile_navi_block(code):
        blk = {}
        blk = AdminUtils.get_navi_block(code)
        if blk['items']:
            _t = []
            for _i in blk['items']:
                _blk = AdminUtils._compile_navi_block(_i['code'])
                _t.append(_blk)
            if _t:
                blk['items'] = _t
        return blk

    # @staticmethod
    # def get_admin_sections():
    #     lst = []
    #     admin_navi = AdminNavigation()
    #     lst = admin_navi.get_sections()
    #     return lst

    @staticmethod
    def get_portal_sections():
        lst = []
        lst = AdminUtils._get_navi_block_content(AdminConf.PORTAL_NAVI_BLOCK_CODE)
        return lst

    @staticmethod
    def get_auth_logger():
        _logger = None

        # $accessLog = new
        # PortalLog(portalApp::getInstance()->getSetting('main.Info.userAccLogName'));
        # _conf_path = ''
        # _conf_path = AdminConf.CONFIGS_PATH
        # if os.path.exists(_conf_path):
        #     app_cfg = app_api.get_config_util()(_conf_path)
        # else:
        #     _path = os.path.join(AdminConf.SELF_PATH, AdminConf.INIT_DIR_NAME, AdminConf.CONF_DIR_NAME)
        #     app_cfg = app_api.get_config_util()(_path)
        app_cfg = AdminUtils.get_default_config()
        # relative_logs = app_cfg.get('main.Info.logDir')
        # logs_dir = os.path.join(app_api.get_app_root_dir(), relative_logs)
        # if not os.path.exists(logs_dir):
        #     os.mkdir(logs_dir)
        # file_name = app_cfg.get('main.Info.userAccLogName') + '.log'
        # file_path = os.path.join(logs_dir, file_name)
        logs_dir = app_api.get_logs_path()
        _logger = UsersAuthLogger(logs_dir, app_cfg.get('main.Info.userAccLogName'))
        return _logger

    @staticmethod
    def get_auth_provider():
        provider = None
        # из настроек портала получитт драйвер авторизации
        provider = AuthProvider()
        return provider

    @staticmethod
    def get_portal_config():
        ocfg = None
        # ocfg = app_api.get_config_util()(AdminConf.CONFIGS_PATH)
        ocfg = AdminUtils.get_default_config()
        return ocfg

    @staticmethod
    def get_default_config():
        ocfg = None
        _path = AdminConf.get_mod_path(AdminConf.INIT_DIR_NAME)
        _path = os.path.join(_path, AdminConf.CONF_DIR_NAME)
        ocfg = app_api.get_config_util()(_path)
        return ocfg

    @staticmethod
    def get_dbg_now():
        return AdminUtils.get_now().strftime("%Y%m%d_%H-%M-%S")

    @staticmethod
    def get_now():
        from datetime import datetime
        return datetime.now()

    @staticmethod
    def read_json_file(file_path):
        data = None
        if os.path.exists(file_path):
            file_path = AdminUtils.__get_real_filepath(file_path)
            with open(file_path, 'r', encoding='utf8') as fp:
                _cont = fp.read()
                if _cont:
                    try:
                        data = json.loads(_cont)
                    except Exception as ex:
                        raise Exception(AdminUtils._debug_name + '.read_json_file.Exception: {}'.format(str(ex)))
        return data

    @staticmethod
    def ini2dict(file_path):
        data = None
        if os.path.exists(file_path) and os.path.isfile(file_path):
            file_path = AdminUtils.__get_real_filepath(file_path)
            base_name = os.path.basename(file_path)
            _parser = configparser.ConfigParser()
            # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
            _parser.optionxform = str
            _parser.read(file_path, encoding='utf8')
            data = {}
            for section in _parser:
                # ConfigParser add DEFAULT section
                # if DEFAULT -> continue
                if 'DEFAULT' == section:
                    continue
                data[section] = AdminUtils._section_to_dict(_parser[section])
        return data

    @staticmethod
    def dict2ini(file_path, data: dict):
        flg = False
        if os.path.exists(file_path) and os.path.isfile(file_path):
            file_path = AdminUtils.__get_conf_save_path(file_path)
            _ini_text = AdminUtils._dict2ini_text(data)
            _parser = configparser.ConfigParser(strict=False, allow_no_value=True)
            # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
            # _parser.optionxform = str
            # _parser.read_dict(data)
            with open(file_path, 'w', encoding='utf8') as fp:
                # _parser.write(fp)
                fp.write(_ini_text)
                flg = True
        return flg

    @staticmethod
    def __get_conf_save_path(file_path):
        _res_path = file_path
        _root_pth = AdminUtils.__get_app_path()
        _app_conf_pth = _root_pth + os.path.sep + 'cfg'
        if os.path.exists(_app_conf_pth):
            _pth_mod = os.path.dirname(AdminUtils._class_file)
            _s = file_path.replace(os.path.dirname(_pth_mod), '').lstrip(os.path.sep).split(os.path.sep)
            _t = _app_conf_pth
            for _st in _s:
                if _st == _s[-1]:
                    break # file
                #  считаем что все остальное директории
                _t = os.path.join(_t, _st)
                if not os.path.exists(_t):
                    os.mkdir(_t)
            _res_path = os.path.join(_app_conf_pth, *_s)
        return _res_path

    @staticmethod
    def _dict2ini_text(dt):
        ini = ''
        # первый уровень ключи секций
        for sec, content in dt.items():
            ini += '[' + sec + ']' + "\n"
            if not isinstance(content, dict):
                ini += "\n"
                continue
            if content:
                for parK, parV in content.items():
                    if isinstance(parV, dict):
                        for mvk, mvd in parV.items():
                            ini += parK + '[' + mvk + ']' + '=' + str(mvd) + "\n"
                    elif isinstance(parV, list):
                        _ind = 0
                        for mvd in parV:
                            ini += parK + '[' + str(_ind) + ']' + '=' + str(mvd) + "\n"
                            _ind += 1
                    else:
                        ini += parK + '=' + str(parV) + "\n"
            ini += "\n"
        return ini

    @staticmethod
    def _section_to_dict(section):
        d = {}
        for k in section:
            if AdminUtils._option_is_section(k):
                ssk = AdminUtils._parse_section_key(k)
                if ssk[0] not in d:
                    d[ssk[0]] = {}
                if ssk[1] not in d[ssk[0]]:
                    d[ssk[0]][ssk[1]] = {}
                d[ssk[0]][ssk[1]] = section[k]
            else:
                d[k] = section[k]
        return d

    @staticmethod
    def _option_is_section(name):
        return -1 < name.find('[') and name.endswith(']')

    @staticmethod
    def _parse_section_key(section_key):
        ssk = section_key.split('[')
        ssk[1] = ssk[1].rstrip(']')
        return ssk

    @staticmethod
    def is_admin_url(search_path):
        flg = False
        admin_navi = AdminNavigation()
        flg = admin_navi.is_admin_url(search_path)
        return flg

    @staticmethod
    def can_access_to_url(search_path, access_for):
        flg = False
        admin_navi = AdminNavigation()
        flg = admin_navi.check_url_access(search_path, access_for)
        return flg

    @staticmethod
    def __get_real_filepath(req_file):
        _root_pth = AdminUtils.__get_app_path()
        # рассматриваем файлы внутри приложения
        if req_file.startswith(_root_pth):
            _app_conf_pth = _root_pth + os.path.sep + 'cfg'
            # если запрошенный файл находится вне конфигурационной директории приложения
            if not req_file.startswith(_app_conf_pth):
                # определяем в какой поддиректории приложения ищется файл
                relative = req_file.replace(_root_pth, '')
                # считаем что данная директория модуль
                _mod_name = relative.lstrip(os.path.sep).split(os.path.sep)[0]
                # если конфигурационная директория существует
                if os.path.exists(_app_conf_pth):
                    _t = os.path.join(_app_conf_pth, _mod_name)
                    # если существует директория модуля в конфигурационной директории
                    if os.path.exists(_t):
                        _t = os.path.join(_app_conf_pth, relative.lstrip(os.path.sep))
                        # существует ли указанный конфигурационный файл
                        if os.path.exists(_t):
                            req_file = _t
        return req_file

    @staticmethod
    def __get_app_path():
        """
        Метод вычисляет путь директории приложения - это отсчетная точка для модулей
        :return: None
        """
        _pth_mod = os.path.dirname(AdminUtils._class_file)
        return os.path.dirname(_pth_mod)

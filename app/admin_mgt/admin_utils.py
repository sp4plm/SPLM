# -*- coding: utf-8 -*-
import os
import json
import configparser

from app.utilites.code_helper import CodeHelper
from app import app_api, mod_manager
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
    def _get_navi_path():
        pth = ''
        pth = AdminConf.get_mod_path('navi')
        if not os.path.exists(pth):
            os.mkdir(pth)
        return pth

    @staticmethod
    def _get_navi_block_content(code):
        items = []
        file_name = code + '.json'
        file_path = os.path.join(AdminUtils._get_navi_path(), file_name)
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
        if os.path.exists(AdminConf.CONFIGS_PATH):
            app_cfg = app_api.get_config_util()(AdminConf.CONFIGS_PATH)
        else:
            _path = os.path.join(AdminConf.SELF_PATH, AdminConf.INIT_DIR_NAME, AdminConf.CONF_DIR_NAME)
            app_cfg = app_api.get_config_util()(_path)
        relative_logs = app_cfg.get('main.Info.logDir')
        logs_dir = os.path.join(app_api.get_app_root_dir(), relative_logs)
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)
        file_name = app_cfg.get('main.Info.userAccLogName') + '.log'
        file_path = os.path.join(logs_dir, file_name)
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
        ocfg = app_api.get_config_util()(AdminConf.CONFIGS_PATH)
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

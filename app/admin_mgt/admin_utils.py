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
    """
    Класс вспомогательного функционала для внутренних нужд модуля
    """
    _class_file = __file__
    _debug_name = 'AdminUtils'

    @staticmethod
    def get_build_version():
        """
        Метод возвращает версию сборки портала
        :return: версия сборки портала
        :rtype str:
        """
        _app_pth = AdminUtils.__get_app_path()
        _build_file = os.path.join(_app_pth, AdminConf.BUILD_FILE_NAME)
        _v = 'splm-00000000'
        if os.path.exists(_build_file):
            with open(_build_file, 'r', encoding='utf-8') as _fp:
                _v = _fp.read().strip("\n\r")
        return _v


    @staticmethod
    def _get_navi_path():
        """
        Метод возвращает абсолютный путь к директории с файлами навигации
        :return: путь к директории с файлами навигации
        :rtype str:
        """
        pth = ''
        pth = AdminConf.get_mod_path(os.path.join('default', 'navi'))
        if not os.path.exists(pth):
            try: os.mkdir(pth)
            except: pass
        return pth

    @staticmethod
    def _get_navi_block_content(code):
        """
        Метод возвращает список ссылок для навигационного блока с кодом code.
        :param str code: код блока навигации
        :return: список ссылок блока навигации
        :rtype list:
        """
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
        """
        Метод возвращает информацию о навигационном блоке с кодом code.
        :param str code: код навигационного блока
        :return: информация о навигационном блоке
        :rtype dict:
        """
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
        """
        Метод возвращает информацию о навигационном блоке с кодом code, дополняя ее список ссылок соответствующих
         данному блоку, при наличии.
        :param str code: код навигационного блока
        :return: информация о навигационном блоке
        :rtype dict:
        """
        block = {}
        block = AdminUtils._get_navi_block_info(code)
        if 'code' in block and '' != block['code']:
            block['items'] = AdminUtils._get_navi_block_content(code)
        return block

    @staticmethod
    def get_site_all_navi():
        """
        Метод возвращает список всех навигационных блоков портала с учетом вложенности.
        :return: список из навигационных блоков
        :rtype list:
        """
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
        """
        Метод возвращает информацию о навигационном блоке с кодом code с учетом вложенности.
        :param str code: код навигационного блока
        :return: информация о навигационном блоке
        :rtype dict:
        """
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

    @staticmethod
    def get_portal_sections():
        """
        Метод возвращает список навигационных секций портала: Разделы административного интерфейса; Список ссылок
         пользователя; Разделы портала; Блок верхней навигации.
        :return: список навигационных секций
        :rtype list:
        """
        lst = []
        lst = AdminUtils._get_navi_block_content(AdminConf.PORTAL_NAVI_BLOCK_CODE)
        return lst

    @staticmethod
    def get_auth_logger():
        """
        Метод возвращает объект для управления логом аторизации пользователей
        :return: объект управления логом
        :rtype UsersAuthLogger:
        """
        _logger = None
        app_cfg = AdminUtils.get_default_config()
        logs_dir = app_api.get_logs_path()
        _logger = UsersAuthLogger(logs_dir, app_cfg.get('main.Info.userAccLogName'))
        return _logger

    @staticmethod
    def get_auth_provider():
        """
        Метод возвращает объект отвечающий за авторизацию пользователя на портале на основе настроек портала
        :return: объект отвечающий за авторизацию на портале
        :rtype AuthProvider:
        """
        provider = None
        # из настроек портала получитт драйвер авторизации
        provider = AuthProvider()
        return provider

    @staticmethod
    def get_portal_config():
        """
        Метод возвращает объект для чтения настроек портала
        :return: объект для чтения настроек портала
        :rtype object:
        """
        ocfg = None
        # ocfg = app_api.get_config_util()(AdminConf.CONFIGS_PATH)
        ocfg = AdminUtils.get_default_config()
        return ocfg

    @staticmethod
    def get_default_config():
        """
        Метод возвращает объект для чтения настроек по-умолчаниею портала
        :return: объект для чтения настроек портала
        :rtype object:
        """
        ocfg = None
        _path = AdminConf.get_mod_path(AdminConf.INIT_DIR_NAME)
        _path = os.path.join(_path, AdminConf.CONF_DIR_NAME)
        ocfg = app_api.get_config_util()(_path)
        return ocfg

    @staticmethod
    def get_dbg_now():
        """
        Вспомогательный метод возвращающий текущую метку времени в формате Ymd_H-M-S
        :return: метка времени в формате Ymd_H-M-S
        :rtype str:
        """
        return AdminUtils.get_now().strftime("%Y%m%d_%H-%M-%S")

    @staticmethod
    def get_now():
        """
        Метод возвращает текущую метку времени в формате timestamp - колличество секунд с 1.01.1970
        ( результат функции - datetime.now() )
        :return: timestamp - колличество секунд с 1.01.1970
        :rtype int:
        """
        from datetime import datetime
        return datetime.now()

    @staticmethod
    def read_json_file(file_path):
        """
        Метод возвращает содержимое файла file_path в виде словаря
        :param str file_path: путь к файлу с содержимым в формате JSON
        :return: результат функции json.loads  или None
        :rtype object:
        """
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
        """
        Метод возвращает содержимое файла file_path в виде словаря
        :param str file_path: путь к файлу формата INI
        :return: словарь из содержимого файла
        :rtype dict:
        """
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
        """
        Метод создает из словаря data файл file_path формата INI
        :param str file_path: путь к файлу в который требуется сохранить словарь data в формате INI
        :param dict data: словарь который требуется сохранить в файл file_path
        :return: возвращает флаг результата: True при успешном сохранении словаря в файл, в противном случае False
        :rtype bool:
        """
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
        """
        Метод определяет путь по которому требуется сохранить изменения файла file_path настроек
        :param str file_path: предположительный путь к файлу, который требуется сохранить
        :return: абсолютный путь по которому надо сохранить файл
        :rtype str:
        """
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
                    try: os.mkdir(_t)
                    except: pass
            _res_path = os.path.join(_app_conf_pth, *_s)
        return _res_path

    @staticmethod
    def _dict2ini_text(dt):
        """
        Метод создает из словаря dt содержимое для INI файла, с учетом вложенности
        :param dict dt: словарь для преобразования в INI
        :return: многострочный текст в формате файла INI
        :rtype str:
        """
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
        """
        Метод создает из section многоуровневый словарь, с учетом использования описания для списков
        :param dict section: словарь, результат разбора configparser
        :return: словарь значений секции
        :rtype dict:
        """
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
        """
        Метод проверяет является ли переданная строка name именем секции из файла INI
        :param str name: проверяемая строка
        :return: возвращает флаг является True или не является False
        :rtype bool:
        """
        return -1 < name.find('[') and name.endswith(']')

    @staticmethod
    def _parse_section_key(section_key):
        """
        Метод разбирает строку search_key, которая предположительно является строкой из INI файла с описанием имени
        секции.
        :param str section_key: строка из INI файла с именем секции
        :return: имя секции
        :rtype str:
        """
        ssk = section_key.split('[')
        ssk[1] = ssk[1].rstrip(']')
        return ssk

    @staticmethod
    def get_private_prefixes():
        _lst = []
        _url_prefix = app_api.get_app_url_prefix()
        _lst.append(_url_prefix.rstrip('/') + '/' + AdminConf.MOD_WEB_ROOT.lstrip('/'))
        _lst.append(_url_prefix.rstrip('/') + '/' + AdminConf.MOD_WEB_ROOT.lstrip('/') + '/installer')
        _lst.append(_url_prefix.rstrip('/') + '/' + AdminConf.MOD_WEB_ROOT.lstrip('/') + '/management')
        _lst.append(_url_prefix.rstrip('/') + '/' + AdminConf.MOD_WEB_ROOT.lstrip('/') + '/configurator')
        _lst.append(_url_prefix.rstrip('/') + '/appmodules')
        _lst.append(_url_prefix.rstrip('/') + '/themesmgt')
        _lst.append(_url_prefix.rstrip('/') + '/mediadata')
        # print('ADminUtils.get_private_prefixes->_lst', _lst)
        return _lst

    @staticmethod
    def is_admin_url(search_path):
        """
        Метод определяет используется ли url search_path для административного интерфейса или нет.
        :param str search_path: проверяемый url
        :return: возвращает флаг является True или не является False
        :rtype bool:
        """
        flg = False
        admin_navi = AdminNavigation()
        flg = admin_navi.is_admin_url(search_path)
        if not flg:
            _app_prefix = app_api.get_app_url_prefix().rstrip('/')
            _lst_prefs = AdminUtils.get_private_prefixes()
            _start_with_p = search_path.startswith(_app_prefix)
            # print('AdminUtils.is_admin_url->_app_prefix:', _app_prefix)
            # print('AdminUtils.is_admin_url->search_path:', search_path)
            for _pref in _lst_prefs:
                _check_pth = _app_prefix + _pref if not _start_with_p else _pref
                # print('AdminUtils.is_admin_url->_pref:', _pref)
                # print('AdminUtils.is_admin_url->_check_pth:', _check_pth)
                if search_path.startswith(_check_pth):
                    flg = True
                    break
        # print('AdminUtils.is_admin_url->result:', flg)
        return flg

    @staticmethod
    def can_access_to_url(search_path, access_for):
        """
        Метод определяет доступен ли url search_path  для пользователя access_for
        :param str search_path: относительный url для проверки доступа
        :param object access_for: объект пользователя для проверки доступа
        :return: возвращает флаг доступен True или не доступен False
        :rtype bool:
        """
        flg = False
        admin_navi = AdminNavigation()
        flg = admin_navi.check_url_access(search_path, access_for)
        return flg

    @staticmethod
    def __get_real_filepath(req_file):
        """
        Метод возвращает реальный путь к указаннаму файлу req_file. Данный метод предназначен для работы с настроечными
        файлами портала или модулей, поддерживая концепцию: есть первичный файл, содержимое которого может изменить
        администратор портала, измененная через интерфейс копия сохраняется в cfg директории проекта. Соответственно,
        данный метод и определяет какой путь брать.
        :param str req_file: имя файла
        :return: абсолютный путь файла
        :rtype str:
        """
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
        :return: абсолютный путь директории приложения(портала)
        :rtype str:
        """
        _pth_mod = os.path.dirname(AdminUtils._class_file)
        return os.path.dirname(_pth_mod)

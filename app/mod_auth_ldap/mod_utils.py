# -*- coding: utf-8 -*-
import os
from datetime import datetime
from shutil import copyfile

from time import time, strftime, localtime


class ModUtils():
    _class_file=__file__
    _debug_name='LDAPAuthModUtils'

    def init(self):
        _t = self.__get_mod_relative_conf_path()
        if not os.path.exists(_t):
            try: os.mkdir(_t)
            except: pass

    def get_server_file(self, name):
        _file = ''
        """
        Сперва получаем директорию где хранятся файлы с описанием серверов
        если в директории ничего нет или нет файла ini с указанным именем то
        получаем путь к внутренней директории серверов и вытаскиваем файл ненастроенного сервера
        если файл с именем имееется то возвращаем его путь
        """
        _file = ''
        _files = self.get_available_servers()  # получили список имеющихся файлов
        if _files:
            _tpl = name + '.ini'
            for _fi in _files:
                _n = os.path.basename(_fi)
                if _n == _tpl:
                    _file = _fi
                    break
        if not os.path.exists(_file) or '' == _file:
            _ext_pth = self.get_mod_servers_path()
            _time = str(datetime.now().timestamp())
            _new_name = 'server_' + _time.split('.')[0]
            _file = os.path.join(_ext_pth, _new_name + '.ini')
        return _file

    def get_server_template(self):
        _default_file = 'default.ini'
        _conf_pth = self.get_mod_conf_path()
        _t = os.path.join(_conf_pth, 'servers', _default_file)
        return _t

    def get_server_template_data(self):
        _d = {}
        _file = self.get_server_template()
        _d = self.__ini2dict(_file)
        return _d

    def is_default_server(self, file):
        _conf_pth = self.get_mod_conf_path()
        _t = os.path.join(_conf_pth, 'servers')
        return _t == os.path.dirname(file)

    def is_default_conf(self, config_name):
        _defaults = self.get_default_configs()
        return config_name in _defaults

    def get_default_configs(self):
        _pth = self.get_mod_conf_path()
        lst = []
        files_list = [fi.name for fi in os.scandir(_pth)]
        for fi in files_list:
            _t = os.path.join(_pth, fi)
            if not os.path.isfile(_t):
                continue
            if not fi.endswith('.ini'):
                continue
            lp = fi.rfind('.')
            lst.append(fi[:lp])
        return lst

    def get_servers(self):
        servers = []
        _lst = self.get_available_servers()
        if _lst:
            for _fi in _lst:
                try:
                    srv_conf = self.__ini2dict(_fi)
                    srv_conf['Info']['source'] = _fi
                    if isinstance(srv_conf, dict):
                        servers.append(srv_conf)
                except Exception as ex:
                    print(self._debug_name + '.get_servers.Exception: ', str(ex))
                    # что-то не так с файлом конфигурации сервера
                    continue
        # _pth = self.get_mod_servers_path()
        # if os.path.exists(_pth) \
        #     and os.path.isdir(_pth):
        #     files = os.scandir(_pth)
        #     for fI in files:
        #         try:
        #             srv_conf = self.ini2dict(os.path.join(_pth, fI.name))
        #             srv_conf['Info']['source'] = os.path.join(_pth, fI.name)
        #             servers.append(srv_conf)
        #         except:
        #             # что-то не так с файлом конфигурации сервера
        #             continue
        #         pass
        return servers

    def get_navi_servers_lst(self):
        _lst = self.get_available_servers()
        # print(self._debug_name + '.get_navi_servers_lst->_lst: ', _lst)
        _navi = []
        _i = 0
        _web_pref = self.get_mod_web_prefix()
        for _sf in _lst:
            _srv_conf = self.ini2dict(_sf)
            _item = {'href': '', 'label': '', 'code': '', 'id':0}
            _item['code'] = os.path.basename(_sf)
            _item['id'] = _i
            _i += 1
            _item['label'] = _srv_conf['Info']['Host']

            lp = _item['code'].rfind('.')
            _item['href'] = _web_pref + '/server/' + str(_item['code'])[:lp]
            _navi.append(_item)
        return _navi

    def get_available_servers(self):
        """
        Метод возвращает список доступных для редактирования файлов конфигураций серверов
        :return: список файлов
        """
        _lst = []
        """
        Файлы серверов могут нахотиться в двух директориях:
        - внутри модуля - app/[mod_name]
        - в директории хранения кофигурационных файлов приложения - app/cfg/[mod_name]
        """
        # поскольку пути различаются а измененне файлы имеют теже имена что и встроенные
        # то используем проверку
        _added = []
        # теперь обработаем внешнее хранилище
        _pth = self.get_mod_servers_path()
        if os.path.exists(_pth) and os.path.isdir(_pth):
            files = os.scandir(_pth)
            for fI in files:
                _t = os.path.join(_pth, fI)
                if not os.path.isfile(_t) or not fI.name.endswith('.ini'):
                    continue
                _added.append(fI.name)
                _lst.append(_t)
        # обработаем внутренние описания (преднастроенные)
        _conf_pth = self.get_mod_conf_path()
        _pth = os.path.join(_conf_pth, 'servers')
        if os.path.exists(_pth) and os.path.isdir(_pth):
            files = os.scandir(_pth)
            for fI in files:
                _t = os.path.join(_pth, fI)
                if not os.path.isfile(_t) or not fI.name.endswith('.ini'):
                    continue
                if fI.name in _added:
                    continue
                _lst.insert(0, _t)  # всегда преднастроенное вставляем в начало списка
        return _lst

    def get_mod_servers_path(self):
        _pth = self.__get_mod_relative_conf_path()
        _pth = os.path.join(_pth, 'cfg')
        if not os.path.exists(_pth):
            try: os.mkdir(_pth)
            except: pass
        _pth = os.path.join(_pth, 'servers')
        if not os.path.exists(_pth):
            try: os.mkdir(_pth)
            except: pass
        return _pth

    def __get_mod_relative_conf_path(self):
        _mod_name = self.get_mod_name()
        from app import app_api
        _app_conf_pth = app_api.get_app_cfg_path()
        _t = os.path.join(_app_conf_pth, _mod_name)
        return _t

    def get_config_file(self):
        _pth = self.get_mod_conf_path()
        _file = os.path.join(_pth, 'main.ini')
        return _file

    def get_mod_conf_path(self):
        _pth = self.get_mod_path()
        _pth = os.path.join(_pth, 'cfg')
        return _pth

    def get_mod_web_prefix(self):
        _p = '/' + self.get_mod_name()
        return _p

    def get_mod_web_prefix(self):
        _p = '/' + self.get_mod_name()
        return _p

    def get_mod_templates_path(self):
        _pth = self.get_mod_path()
        _pth = os.path.join(_pth, 'templates')
        return _pth

    def get_mod_static_path(self):
        _pth = self.get_mod_path()
        _pth = os.path.join(_pth, 'static')
        return _pth

    def get_mod_name(self):
        _pth = self.get_mod_path()
        _name = os.path.basename(_pth)
        return _name

    def get_mod_path(self):
        _pth = os.path.dirname(__file__)
        return _pth

    def dict2ini(self, file_path, data: dict):
        flg = False
        if os.path.exists(file_path) and os.path.isfile(file_path):
            file_path = self.__get_conf_save_path(file_path)
            _ini_text = self._dict2ini_text(data)
            import configparser
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

    def ini2dict(self, file_path):
        data = None
        if os.path.exists(file_path) and os.path.isfile(file_path):
            file_path = self.__get_real_filepath(file_path)
            base_name = os.path.basename(file_path)
            data = self.__ini2dict(file_path)
        return data

    def __ini2dict(self, file_path):
        data = None
        if os.path.exists(file_path) and os.path.isfile(file_path):
            import configparser
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
                data[section] = self._section_to_dict(_parser[section])
        return data

    def _section_to_dict(self, section):
        d = {}
        for k in section:
            if self._option_is_section(k):
                ssk = self._parse_section_key(k)
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
    def __get_real_filepath(req_file):
        _root_pth = ModUtils.get_app_path()
        # рассматриваем файлы внутри приложения
        if req_file.startswith(_root_pth):
            from app import app_api
            _app_conf_pth = app_api.get_app_cfg_path()
            _app_data_pth = app_api.get_app_data_path()
            # если запрошенный файл находится вне конфигурационной директории приложения
            if not req_file.startswith(_app_conf_pth) and not req_file.startswith(_app_data_pth):
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
    def __get_conf_save_path(file_path):
        _res_path = file_path
        _root_pth = ModUtils.get_app_path()
        from app import app_api
        _app_conf_pth = app_api.get_app_cfg_path()
        if os.path.exists(_app_conf_pth):
            _s = file_path.replace(_root_pth, '').lstrip(os.path.sep).split(os.path.sep)
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
    def get_app_path():
        """
        Метод вычисляет путь директории приложения - это отсчетная точка для модулей
        :return: None
        """
        from app import app_api
        return app_api.get_app_root_dir()

    def formated_time_mark(self, _tpl='%Y%m%d_%H-%M-%S'):
        return strftime(_tpl, localtime(time()))

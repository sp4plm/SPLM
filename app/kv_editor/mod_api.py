# -*- coding: utf-8 -*-
import os.path
from .mod_conf import ModConf


class ModApi(ModConf):
    _class_file = __file__
    _debug_name = 'KVEditorModApi'

    def render_page(self, base, _vars=None):
        """
        Функция формирует страницу портала по шаблону

        :param base:
        :param _vars:
        :return: page
        :rtype: html
        """

        _tpl_name = ''
        _tpl_vars = {}
        _file_name = 'new_config_1'
        _can_remove = False
        relative = ''
        work_mod = ''
        if isinstance(_vars, dict):
            _tpl_vars = _vars
            if 'source_name' in _vars:
                relative = _vars['source_name']
                _file_name = os.path.basename(relative).split('.')[0]
            if 'mod_name' in _vars:
                work_mod = _vars['mod_name']
        if '' != work_mod and '' != relative:
            _can_remove = self.can_remove_file(work_mod, relative)
        _tpl_name = self.get_editor_tpl()
        _tpl_vars['to_extend'] = base
        _tpl_vars['js_base_url'] = self.MOD_WEB_ROOT
        _tpl_vars['edit_name'] = _file_name
        _tpl_vars['can_remove'] = _can_remove
        from app import app_api
        return app_api.render_page(_tpl_name, **_tpl_vars)

    def __get_full_file_path(self, mod, relative):
        _pth = ''
        _app_path = self.get_app_path()
        if relative.startswith(_app_path) and -1 < relative.find(os.path.sep + mod + os.path.sep):
            # значит путь уже полный и мы можем обмануть систему
            _t = relative.split(mod)
            relative = _t[-1]
        if '' != mod and '' != relative:
            relative = relative.lstrip(os.path.sep)
            if relative.startswith(mod):
                relative = relative.replace(mod, '').lstrip(os.path.sep)
            _pth = os.path.join(_app_path, mod, relative)
        return _pth

    def can_remove_file(self, mod_name, _file_pth):
        """
        Функция проверяет наличие файла

        :param str mod_name:
        :param str _file_pth:
        :return: флаг
        :rtype: bool
        """

        flg = False
        from app import app_api
        _app_conf_pth = app_api.get_app_cfg_path()
        _app_data_pth = app_api.get_app_data_path()
        _read_path = ''
        # можно указывать полные пути только для файлов в директориях app/cfg и app/data
        if _file_pth.startswith(_app_conf_pth) or _file_pth.startswith(_app_data_pth):
            # редактируем только настройки файлов как данные
            _read_path = _file_pth
        else:
            # если же путь начинается с чегото другого - считаем это относительный путь
            _file_path = self.__get_full_file_path(mod_name, _file_pth)
            _read_path = self.__get_real_filepath(_file_path)
        # редактирование файла настроечного
        if _read_path.startswith(_app_conf_pth):
            flg = True
        # редактирования файла данных
        if not flg and _read_path.startswith(_app_data_pth):
            flg = True
        if flg:
            # если вдруг файл редактировать можно, но он еще не создан
            flg = os.path.exists(_read_path)
        return flg

    def remove_file(self, mod_name, _file_pth):
        """
        Функция удаляет указанный в параметре файл

        :param str mod_name: имя удаляемого файла
        :param str _file_pth: полный путь к удаляемому файлу
        :return: флаг
        :rtype: bool
        """

        flg = False
        if self.can_remove_file(mod_name, _file_pth):
            from app import app_api
            _app_conf_pth = app_api.get_app_cfg_path()
            _app_data_pth = app_api.get_app_data_path()
            _to_remove = ''
            # можно указывать полные пути только для файлов в директориях app/cfg и app/data
            if _file_pth.startswith(_app_conf_pth) or _file_pth.startswith(_app_data_pth):
                # редактируем только настройки файлов как данные
                _to_remove = _file_pth
            else:
                _file_path = self.__get_full_file_path(mod_name, _file_pth)
                _to_remove = self.__get_conf_save_path(_file_path)
            os.unlink(_to_remove)
            flg = not os.path.exists(_to_remove)
        return flg

    def dict2ini(self, file_path, data: dict):
        """
        Функция .....

        :param str file_path:
        :param dict data:
        :return:
        :rtype:
        """

        flg = False
        # if os.path.exists(file_path) and os.path.isfile(file_path):
        file_path = self.__get_conf_save_path(file_path)
        # print(self._debug_name + '.dict2ini-> save path: ', file_path)
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

    def ini2dict(self, file_path, curent_file=False):
        """
        Функция .....

        :param str file_path: полный путь до файла
        :param bool current_file: флаг
        :return:
        :rtype:
        """
        data = None
        if os.path.exists(file_path) and os.path.isfile(file_path):
            if not curent_file:
                file_path = self.__get_real_filepath(file_path)
            base_name = os.path.basename(file_path)
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
        _root_pth = ModApi.get_app_path()
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
        _root_pth = ModApi.get_app_path()
        from app import app_api
        _app_conf_pth = app_api.get_app_cfg_path()
        if os.path.exists(_app_conf_pth):
            _s = file_path.replace(_root_pth, '').lstrip(os.path.sep).split(os.path.sep)
            if file_path.startswith(_app_conf_pth):
                # значит мы редактируем новый файл сразу в конфигурационной папки
                _s = file_path.replace(_app_conf_pth, '').lstrip(os.path.sep).split(os.path.sep)
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
    def get_app_path():
        """
        Функция вычисляет путь директории приложения - это отсчетная точка для модулей

        :return: app_root_dir
        :rtype: str
        """
        from app import app_api
        return app_api.get_app_root_dir()

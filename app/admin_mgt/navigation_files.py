# -*- coding: utf-8 -*-
import os
import json

# from app.admin_mgt.admin_utils import AdminConf


class NavigationFiles():
    _class_file = __file__
    _debug_name = 'NavigationFiles'
    _def_register = 'navi_blocks.json'

    def __init__(self, files_path=''):
        self._register = self._def_register
        self._files_path = ''
        self.set_work_dir(files_path)

    def get_file_source(self, code=''):
        if '' == code:
            code = self._register.split('.')[0]
        _path = self._get_file_path_by_code(code)
        src = self._read_json_file(_path, [])
        return src

    def get_list(self):
        lst = []
        if os.path.exists(self._files_path) and os.path.isdir(self._files_path):
            _files = os.scandir(self._files_path)
            if _files:
                lst = [it.name for it in _files]
        return lst

    def save_file(self, name, content):
        flg = False
        _path = self._get_file_path_by_code(name)
        if content is None:
            content = []
        flg = self._save_json_file(_path, content)
        return flg

    def add_file(self, name, content=None):
        flg = False
        flg = self.save_file(name, content)
        return flg

    def remove_file(self, name):
        _path = self._get_file_path_by_code(name)
        flg = False
        if os.path.exists(_path) and os.path.isfile(_path):
            os.unlink(_path)
            flg = not os.path.exists(_path)
        return flg

    def rename_file(self, name, new_name):
        _path = self._get_file_path_by_code(name)
        _new_path = self._get_file_path_by_code(new_name)
        flg = False
        if os.path.exists(_path) and os.path.isfile(_path):
            os.rename(_path, _new_path)
            flg = not os.path.exists(_path)
        return flg

    def exists(self, name):
        _path = self._get_file_path_by_code(name)
        return os.path.exists(_path) and os.path.isfile(_path)

    def is_empty(self, name):
        data = self.get_file_source(name)
        return 0 < len(data)

    def set_work_dir(self, dir_path):
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            self._files_path = dir_path

    def _get_file_path_by_code(self, code):
        file_name = code + '.json'
        _path = os.path.join(self._files_path, file_name)
        return _path

    def _save_json_file(self, _path, content):
        flg = False
        if not os.path.exists(_path):
            pass # оставляем для ???
        # _path = self.__get_real_save_path(_path)
        with open(_path, 'w', encoding='utf8') as fp:
            try:
                data = json.dumps(content)
            except Exception as ex:
                raise Exception(self._debug_name + '._save_json_file.Exception: {}'.format(str(ex)))
            if isinstance(data, str):
                fp.write(data)
                flg = True
        return flg

    def __get_real_save_path(self, _path):
        _root_pth = self.__get_app_path()
        _app_conf_pth = _root_pth + os.path.sep + 'cfg'
        _res_pth = _path
        if os.path.exists(_app_conf_pth):
            _pth_mod = os.path.dirname(self._class_file)
            # _t = os.path.join(_app_conf_pth, os.path.basename(_pth_mod))
            # if not os.path.exists(_t):
            #     os.mkdir(_t)
            _s = _path.replace(os.path.dirname(_pth_mod), '').lstrip(os.path.sep).split(os.path.sep)
            _t = _app_conf_pth
            for _st in _s:
                if _st == _s[-1]:
                    break # file
                #  считаем что все остальное директории
                _t = os.path.join(_t, _st)
                if not os.path.exists(_t):
                    os.mkdir(_t)
            _res_pth = os.path.join(_app_conf_pth, *_s)
        return _res_pth

    def _read_json_file(self, file_path, default=''):
        data = None
        # file_path = self.__get_real_read_path(file_path)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf8') as fp:
                _cont = fp.read()
                if _cont:
                    try:
                        data = json.loads(_cont)
                    except Exception as ex:
                        raise Exception(self._debug_name + '._read_json_file.Exception: {}'.format(str(ex)))
        if data is None:
            data = default
        return data

    def __get_real_read_path(self, _file_path):
        _pth = self.__get_real_filepath(_file_path)
        return _pth

    def __get_real_filepath(self, req_file):
        _root_pth = self.__get_app_path()
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

    def __get_app_path(self):
        """
        Метод вычисляет путь директории приложения - это отсчетная точка для модулей
        :return: None
        """
        _pth_mod = os.path.dirname(self._class_file)
        return os.path.dirname(_pth_mod)

    def is_block_exists(self, code):
        _path = self._get_file_path_by_code(code)
        return os.path.exists(_path)

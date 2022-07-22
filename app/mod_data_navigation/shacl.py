# -*- coding: utf-8 -*-
import os

class Shacl:
    format_file = ".ttl"
    MOD_CFG_PATH = ""

    def __init__(self):
        
        self.MOD_CFG_PATH = os.path.join(os.path.dirname(__file__), "shacl")


    def __get_real_qfile(self, file_path):
        _pth = file_path
        _root = self.__get_app_root_dir()
        mod_name = file_path.replace(_root, '').lstrip(os.path.sep).split(os.path.sep)[0]
        _conf_path = self.__get_app_conf_dir()
        if not file_path.startswith(_conf_path):
            _t = os.path.join(_conf_path, mod_name)
            if os.path.exists(_t):
                relative = file_path.replace(_root, '').lstrip(os.path.sep).replace(mod_name, '').lstrip(os.path.sep)
                _rp = os.path.join(_t, relative)
                if os.path.exists(_rp):
                    _pth = _rp
        return _pth

    def __get_app_conf_dir(self):
        """
        Метод возвращает полный путь до директории приложения с измененными конфигурационными файлами модулей (cfg)
        :return: путь до директории конфигурационных файлов
        """
        from app.app_api import get_app_cfg_path
        return get_app_cfg_path()

    def __get_app_root_dir(self):
        """
        Метод возвращает полный путь директории приложения
        :return: путь директории приложения
        """
        from app.app_api import get_app_root_dir
        return get_app_root_dir()


    def get_full_file_path(self, file):
        """
        Метод возвращает абсолютный путь файла
        :param file: string
        :return: path
        """
        _pth = os.path.join(self.MOD_CFG_PATH, file)
        _pth = self.__get_real_qfile(_pth)
        return _pth

    def get_list_shacl(self):
        files = []
        for file in os.listdir(self.MOD_CFG_PATH):
            if os.path.isfile(os.path.join(self.MOD_CFG_PATH, file)):
                files.append(file)
        files.sort()
        return files

    def can_remove(self, file):
        """
        Метод проверяет можно ли удалять файл - то есть изначальный файл был отредактирован пользователем
        :param file:
        :return:
        """
        _flg = False
        _pth = self.get_full_file_path(file)
        _conf_path = self.__get_app_conf_dir()
        if _pth.startswith(_conf_path):
            _flg = True
        return _flg

    def get_file(self, file):
        data = ""
        if not file:
            return data

        with open(self.get_full_file_path(file), "r", encoding="utf-8") as f:
            data = f.read()

        return data

    def edit_file(self, file, data):
        # согласно новой концепции сохранять редактируемый файл требуется в директорию общего конфига
        _conf_path = self.__get_app_conf_dir()  # директория конфигураций приложения
        _pth = self.get_full_file_path(file)
        if not _pth.startswith(_conf_path):
            _root_path = self.__get_app_root_dir()
            relative = _pth.replace(_root_path, '').lstrip(os.path.sep).split(os.path.sep)
            #  принудительно заменяем путь сохранения
            _t = _conf_path
            for _s in relative:
                if _s == relative[-1]:
                    break
                _t += os.path.sep + _s
                if not os.path.exists(_t):
                    os.mkdir(_t)
            _pth = os.path.join(_t, relative[-1])
        with open(_pth, "w", encoding="utf-8") as f:
            data = data.replace('\\n', '\n').replace('\\r', '')
            f.write(data)


    def delete_file(self, file):
        if os.path.exists(self.get_full_file_path(file)):
            os.remove(self.get_full_file_path(file))


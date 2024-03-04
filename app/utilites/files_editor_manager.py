# -*- coding: utf-8 -*-

import os
from app import app_api
from flask import request, redirect, url_for


class FilesEditorManager:
    """
    Создание менеджера редактирования файлов
    """

    MOD_CFG_PATH = ""

    def __init__(self, cfg_path):
        self.MOD_CFG_PATH = cfg_path

    @staticmethod
    def _get_app_conf_dir():
        """
        Метод возвращает полный путь до директории приложения с измененными конфигурационными файлами модулей (cfg)
        :return: путь до директории конфигурационных файлов
        """
        from app.app_api import get_app_cfg_path
        return get_app_cfg_path()

    @staticmethod
    def _get_app_root_dir():
        """
        Метод возвращает полный путь директории приложения
        :return: путь директории приложения
        """
        from app.app_api import get_app_root_dir
        return get_app_root_dir()

    def _get_real_qfile(self, file_path):
        """
        Метод возвращает путь до файла.
        Если файл редактируется впервые, то берется из ядра модуля.
        Если файл уже редактировался, то берется из cfg для пользователя

        :return _pth: фактический путь до sparqt-файла
        :rtype: str
        """
        _pth = file_path
        _root = self._get_app_root_dir()
        mod_name = file_path.replace(_root, '').lstrip(os.path.sep).split(os.path.sep)[0]
        _conf_path = self._get_app_conf_dir()
        if not file_path.startswith(_conf_path):
            _t = os.path.join(_conf_path, mod_name)
            if os.path.exists(_t):
                relative = file_path.replace(_root, '').lstrip(os.path.sep).replace(mod_name, '').lstrip(os.path.sep)
                _rp = os.path.join(_t, relative)
                if os.path.exists(_rp):
                    _pth = _rp
        return _pth

    def get_full_file_path(self, file):
        """
        Метод возвращает абсолютный путь файла

        :param str file: путь до указанного файла
        :return: path
        """
        _pth = os.path.join(self.MOD_CFG_PATH, file)
        _pth = self._get_real_qfile(_pth)
        return _pth

    def get_files(self):
        files = []
        for file in os.listdir(self.MOD_CFG_PATH):
            if os.path.isfile(os.path.join(self.MOD_CFG_PATH, file)):
                files.append(file)
        files.sort()
        return files

    def can_remove(self, file):
        """
        Метод проверяет можно ли удалять файл - то есть изначальный файл был отредактирован пользователем

        :param str file:
        :return: результат проверки
        :rtype: bool
        """
        _flg = False
        _pth = self.get_full_file_path(file)
        _conf_path = self._get_app_conf_dir()
        if _pth.startswith(_conf_path):
            _flg = True
        return _flg

    def get_file(self, file):
        """"""
        data = ""
        if not file:
            return data

        with open(self.get_full_file_path(file), "r", encoding="utf-8") as f:
            data = f.read()

        return data

    def edit_file(self, file, data):
        """Функция сохраняет редактируемый файл в директорию общего конфига

        :param str file: имя файла
        :param str data: содержание файла
        """
        _conf_path = self._get_app_conf_dir()  # директория конфигураций приложения
        _pth = self.get_full_file_path(file)
        if not _pth.startswith(_conf_path):
            _root_path = self._get_app_root_dir()
            relative = _pth.replace(_root_path, '').lstrip(os.path.sep).split(os.path.sep)
            #  принудительно заменяем путь сохранения
            _t = _conf_path
            for _s in relative:
                if _s == relative[-1]:
                    break
                _t += os.path.sep + _s
                if not os.path.exists(_t):
                    try:
                        os.mkdir(_t)
                    except:
                        pass
            _pth = os.path.join(_t, relative[-1])
        with open(_pth, "w", encoding="utf-8") as f:
            data = data.replace('\\n', '\n').replace('\\r', '')
            f.write(data)

    def delete_file(self, file):
        if os.path.exists(self.get_full_file_path(file)):
            os.remove(self.get_full_file_path(file))

    @staticmethod
    def check_before_save(*args, **kwargs):
        """ Проверка по умолчанию всегда True """
        return True

    def create(self, url, blueprint_mod, check_before_save=None):
        """"""
        _auth_decorator = app_api.get_auth_decorator()
        mod_name = blueprint_mod.name

        if callable(check_before_save):
            self.check_before_save = check_before_save

        _params = {
            "module": mod_name,
            "title": "Редактор файлов",
            "editor_format": "sparql"  # "javascript"
        }

        @blueprint_mod.route(url, methods=['GET', 'POST'])
        @_auth_decorator
        def _list():
            return app_api.render_page('/utilites/list.html', **_params, files=self.get_files())

        @blueprint_mod.route(url + "/<file>", methods=["GET", "POST"])
        @_auth_decorator
        def _editor(file=''):
            _template = '/utilites/editor.html'
            _render_data = {**_params, **{
                "file": file,
                "can_remove": self.can_remove(file),
            }}

            if 'save' in request.form:
                if os.path.exists(self.get_full_file_path(file)):
                    # Проверка данных и сохранение
                    save_status = self.check_before_save(request.form['data'])
                    if save_status is True:
                        self.edit_file(file, request.form['data'])
                    else:
                        # Если проверка данных не прошла, то возвращаемся обратно в форму
                        return app_api.render_page(_template, **_render_data, data=request.form['data'], error=save_status)
                else:
                    return app_api.render_page(_template, **_render_data, data=request.form['data'])

                return redirect(url_for(mod_name + '._list'))

            elif 'delete' in request.form:
                self.delete_file(file)
                return redirect(url_for(mod_name + '._list'))

            else:
                return app_api.render_page(_template, **_render_data, data=self.get_file(file))

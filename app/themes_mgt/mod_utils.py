# -*- coding: utf-8 -*-
import os
import json
import shutil
from datetime import datetime

from app.utilites.code_helper import CodeHelper

from .mod_conf import ModConf


class ModUtils(ModConf):
    _class_file = __file__
    _debug_name = 'ThemesMgtUtils'

    def __init__(self):
        self._last_uploaded_file = ''
        self._oper_errors = []

    def get_list(self):
        try:
            _man = self.get_manager()
            lst = [_theme.name for _theme in _man.list_themes()]
        except Exception as ex:
            print(self._debug_name + '.get_list->Не удалось получить список тем портала. Ошибка: {}'.format(str(ex.args)))
            lst = []
        return lst

    def get_id_by_name(self, name):
        _id = ''
        try:
            _man = self.get_manager()
            for _theme in _man.list_themes():
                if name == _theme.name:
                    _id = _theme.identifier
        except Exception as ex:
            print(self._debug_name + '.get_id_by_name->Не удалось получить идентификатор темы. Ошибка: {}'.format(str(ex.args)))
        return _id

    def get_path_by_name(self, name):
        _pth = ''
        try:
            _id = self.get_id_by_name(name)
            _wp = self.get_work_path()
            _t = os.path.join(_wp, _id)
            if os.path.exists(_t):
                _pth = _t
        except Exception as ex:
            print(self._debug_name + '.get_path_by_name->Не удалось удалить тему {}. Ошибка: {}'.format(name, str(ex.args)))
        return _pth

    def get_default_list(self):
        _lst = []
        _root = self.get_defaults_path()
        _lst = [_t.name for _t in os.scandir(_root) if _t.is_dir()]
        return _lst

    def reset_to_defaults(self):
        flg = False
        _default_themes = self.get_default_list()
        _src_path = self.get_defaults_path()
        _trgt_path = self.get_work_path()
        _c = 0
        _n = len(_default_themes)
        for _dt in _default_themes:
            _ts = os.path.join(_src_path, _dt)
            if not os.path.exists(_ts) or not os.path.isdir(_ts):
                _n -= 1
                continue
            _tp = os.path.join(_trgt_path, _dt)
            if os.path.exists(_tp):
                self.__rmt(_tp)  # удаляем старую папку темы
            self.__cpr(_ts, _tp)
            if os.path.exists(_tp):
                _c += 1
        if _c == _n:
            flg = True
        return flg

    def add_new(self, zip_file):
        """
        Метод добавляет новую тему портала из файла-архива zip_file
        :param zip_file: путь к файлу архиву в формате zip
        :return:
        """
        flg = False
        # если файл не существует то выходим
        if not os.path.exists(zip_file) or not os.path.isfile(zip_file):
            _msg = 'Файл "{}" не создан!' . format(zip_file)
            self.__add_error(_msg)
            return flg
        # создаем временную директорию
        root_dir = self.get_mod_path('data')
        extract_dir = os.path.join(root_dir, 'extract_t' + str(datetime.now()))
        os.mkdir(extract_dir)
        # разархивируем архив во временную директорию
        unpack_flg = CodeHelper.make_unpack(zip_file, extract_dir)
        if not unpack_flg:
            # наверно надо вынести это в лог ошибок
            _msg = 'Не удалось распаковать файл "{}"!' . format(zip_file)
            self.__add_error(_msg)
            return flg # неудалось распаковать
        # во временной директории должна появиться одна директория темы
        _src_theme = self.__get_subdirs(extract_dir)[0]
        _work_path = self.get_work_path()
        _work_path = os.path.join(_work_path, _src_theme)
        _src_theme = os.path.join(extract_dir, _src_theme)
        # копируем директорию темы в директорию хранения тем проекта/портала
        if os.path.exists(_src_theme) and os.path.isdir(_src_theme):
            _copy_res = self.__cpr(_src_theme, _work_path)
            flg = os.path.exists(_work_path)
            if not flg:
                _msg = 'Не удалось скопировать директорию темы {} в специализированную директорию!'.format(_src_theme)
                self.__add_error(_msg)
        # удаляем диреторию в которую распаковывали
        self.__rmt(extract_dir)
        return flg

    @staticmethod
    def __cpr(_src, _tgt):
        # https://stackoverflow.com/questions/15034151/copy-directory-contents-into-a-directory-with-python
        res = shutil.copytree(_src, _tgt, dirs_exist_ok=True)
        return res

    @staticmethod
    def __rmt(_tgt):
        res = shutil.rmtree(_tgt, ignore_errors=True)
        return res

    @staticmethod
    def __get_subdirs(_root):
        lst = []
        if os.path.exists(_root) and os.path.isdir(_root):
            lst = [_it.name for _it in os.scandir(_root) if _it.is_dir()]
        return lst

    def save_uploaded_file(self, http_file):
        if http_file and self.__is_correct_file(http_file.filename):
            filename = self.__secure_file_name(http_file.filename)
            # всегда сохраняем файл в директорию данных модуля
            dirname = self.get_mod_path('data')
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            work_file = os.path.join(dirname, filename)
            if os.path.exists(work_file.encode('utf-8')):
                os.unlink(work_file)
            with open(work_file.encode('utf-8'), 'wb') as fp:
                http_file.save(fp)
            self._last_uploaded_file = work_file
            return work_file
        else:
            raise Exception('Is not a correct file type!')

    @staticmethod
    def __is_correct_file(file_path) -> bool:
        flg = False
        _allowed = ['zip']
        flg = '.' in file_path and \
              file_path.rsplit('.', 1)[1] in _allowed
        return flg

    @staticmethod
    def __secure_file_name(file_name):
        a = ''
        a = file_name.strip()
        a = a.replace(' ', '_')
        a = a.replace('\\', '_')
        a = a.replace('/', '_')
        a = a.replace(':', '_')
        a = a.replace('*', '_')
        a = a.replace('?', '_')
        a = a.replace('"', '')
        a = a.replace('<', '_')
        a = a.replace('>', '_')
        a = a.replace('|', '_')
        a = a.replace('+', '_')
        a = a.replace('%', '_')
        a = a.replace('!', '_')
        a = a.replace('@', '_')
        return a

    def get_max_filesize(self):
        return 1024 * 1024 + 50

    def get_view_table_columns(self):
        _cols = []
        _cols.append({"label": "", "index": "Toolbar", "name": "Toolbar", "width": 40, "sortable": False, "search": False})
        _cols.append({"label": "Активная", "index": "Enabled", "name": "Enabled", "width": 40, "sortable": False, "search": False, 'align':'center'})
        _cols.append({"label": "Название", "index": "Name", "name": "Name", "width": 90, "search": False, "stype": 'text',
              "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
            })
        _cols.append({"label": "Описание", "index": "Description", "name": "Description", "width": 200, "search": False, "stype": 'text',
              "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
            })
        _cols.append({"label": "Преднастроенная", "index": "IsDefault", "name": "IsDefault", "width": 40, "sortable": False, "search": False, 'align':'center'})
        return _cols

    def get_manager(self):
        from app import app
        _mg = None
        if hasattr(app, 'theme_manager'):
            _mg = app.theme_manager
        return _mg

    def get_defaults_path(self):
        _pth = ''
        _pth = self.DEFAULTS_PATH
        return _pth

    def get_work_path(self):
        from app import app, app_api
        _def_pth = app_api.get_app_cfg_path()
        # просто известно где расположена и как нывается директория с темами для flask-themes2
        _def_pth = os.path.join(_def_pth, 'themes')
        try:
            _t = app.config['THEME_PATHS']
            _def_pth = _t
        except Exception as ex:
            _msg = self._debug_name + \
                   '.get_work_path: Не удалось получить из конфигурации путь к директории тем!'.format(str(ex.args))
            self.__add_error(_msg)
            print(_msg)
        return _def_pth

    def get_last_uploaded(self):
        return self._last_uploaded_file

    def __add_error(self, msg):
        self._oper_errors.append(msg)

    def get_last_error(self):
        return self._oper_errors[-1]

    def get_errors(self):
        return self._oper_errors

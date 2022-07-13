# -*- coding: utf-8 -*-

import os
from datetime import datetime
from json import loads, dumps

from .mod_utils import ModUtils


class FilesManagement(object):
    _class_file = __file__
    _debug_name = 'PortaldataFilesManagement'
    _register_name = 'register'

    def __init__(self, _work_path):
        if not os.path.exists(_work_path) or not os.path.join(_work_path):
            raise NotADirectoryError
        _utils = ModUtils()
        self._mod_conf = _utils.get_config()
        self._register_name = self._mod_conf['Main']['register_name']
        self._work_path = _work_path
        self.__init_struct()
        self.__init_content_stop_lst()

    def __init_struct(self):
        # проверяем наличие директорий и файлов соглассно настройкам
        # в корне должны быть директории:
        # - res -  директория загрузки файлов данных для публикации
        # - backups - директория резервных копий
        # и файл register.json - для хранения описания и правдоступа к директориям

        _root_name = self._mod_conf['Main']['root_directory_name']
        if not self._work_path.rstrip(os.path.sep).endswith(_root_name):
            self._work_path = os.path.join(self._work_path.rstrip(os.path.sep), _root_name)
            if not os.path.exists(self._work_path):
                os.mkdir(self._work_path)
        _sections_lst = self._mod_conf['Main']['work_sections'].split(',')

        if _sections_lst:
            for _sec in _sections_lst:
                _sec = _sec.strip()
                if not self._mod_conf.has_section(_sec):
                    continue
                _t = os.path.join(self._work_path, _sec)
                if not os.path.exists(_t):
                    os.mkdir(_t)
                if 'use_register' in self._mod_conf[_sec] and 1 == self._mod_conf[_sec]['use_register']:
                    pass

    def get_section_path(self, name):
        _pth = None
        if name in self._mod_conf:
            _pth = os.path.join(self._work_path, name)
        return _pth

    def get_section_inf(self, _sec):
        _inf = None
        if _sec in self._mod_conf:
            _inf = self._mod_conf[_sec]
            _inf['path'] = os.path.join(self._work_path, _sec)
        return _inf

    def __normalize_filter(self, _sec, filter):
        if filter is not None and filter:
            filters = loads(filter)
            if 'rules' in filters:
                filters = filters['rules']
                #  теперь нужно заменить колонки в правилах согласно карте
                _c_map = self.__get_columns_map(_sec)
                _t2 = []
                for _r in filters:
                    _r['field'] = _c_map[_r['field']]
                    _t2.append(_r)
                filter = _t2
                _t2 = None
        return filter

    def get_section_content(self, _sec, filters=None, **kwargs):
        _files = []
        _inf = self.get_section_inf(_sec)
        if _inf:
            _register = None
            _register = self.get_section_register(_sec)
            if _register is not None:
                # print(self._debug_name + '.get_section_content->section filter', filters)
                if filters is not None:
                    filters = self.__normalize_filter(_sec, filters)
                if kwargs:
                    # print(self._debug_name + '.get_section_content->kwargs', kwargs)
                    if 'count' in kwargs:
                        kwargs['limit'] = kwargs['count']
                        del kwargs['count']
                    if 'start' in kwargs:
                        kwargs['offset'] = kwargs['start']
                        del kwargs['start']
                _files = _register.get_records(filter=filters, **kwargs)
        return _files

    def count_section_content(self, _sec, filters=None):
        _cnt = 0
        _inf = self.get_section_inf(_sec)
        if _inf:
            _register = None
            _register = self.get_section_register(_sec)
            if _register is not None:
                if filters is not None:
                    filters = self.__normalize_filter(_sec, filters)
                _cnt = _register.count_records(filters)
        return _cnt

    def get_section_files(self, _sec):
        """
        Возвращает список файлов для указанной секции, где каждый элемент списка - полный путь к файлу.
        :param _sec: имя секции
        :return: список файлов
        """
        _pth = self.get_section_path(_sec)
        files = []
        if os.path.exists(_pth):
            _inf = self.get_section_inf(_sec)
            list_items = os.scandir(_pth)
            if list_items:
                # теперь уберем файлы которые не относятся к секции
                _files_ext = []
                if 'upload_files' in _inf:
                    _files_ext = str(_inf['upload_files']).split(',')
                # print('get_dir_content catch files')
                _stop_lst = self._content_stop_lst
                for item in list_items:
                    if item.name in _stop_lst:
                        continue
                    _w = os.path.join(_pth, item.name)
                    _fext = item.name.split('.')[-1]
                    if _files_ext and _fext not in _files_ext:
                        continue
                    files.append(_w)
        return files

    def remove_section_file(self, _sec, _file_name):
        _flg = False
        _pth = self.get_section_path(_sec)
        if os.path.exists(_pth):
            _t = os.path.join(_pth, _file_name)
            if os.path.exists(_t):
                os.unlink(_t)
                _flg = os.path.exists(_t)
                if not _flg:
                    # получим информацию о секции
                    _inf = self.get_section_inf(_sec)
                    # теперь требуется получить реестр секции
                    _reg = self.get_section_register(_sec)
                    _reg.remove_record(_file_name)
                    _flg = True # теперь честно говорим что удалили
        return _flg

    def add_section_file(self, _sec, _file):
        _flg = False
        _pth = self.get_section_path(_sec)
        if os.path.exists(_pth):
            _recs = []
            _recs.append(self.__create_section_record(_sec, os.path.basename(_file)))
            _flg = self.__add_section_records(_sec, _recs)
        return _flg

    def update_section_file(self, _sec, _file_name, _new_data):
        _flg = False
        _pth = self.get_section_path(_sec)
        if os.path.exists(_pth):
            _data = {}
            _data[os.path.basename(_file_name)] = _new_data
            # print(self._debug_name + '.update_section_file -> _data', _data)
            _flg = self.__update_section_records(_sec, _data)
        return _flg

    def __update_section_records(self, _sec, _files_data):
        _flg = False
        _reg = self.get_section_register(_sec)
        if _reg is not None:
            # print(self._debug_name + '.__update_section_records -> _files_data', _files_data)
            _flg = _reg.update_records(_files_data)
        return _flg

    def sync_section_content(self, _sec):
        """
        Метод производит соответствие между реестром и файлами в директории секции
        Первичны файлы, сам реестр вторичен
        :param _sec: имя секции
        :return:
        """
        _pth = self.get_section_path(_sec)
        if os.path.exists(_pth):
            # получим список файлов секции
            _sec_files = self.get_section_files(_sec)
            # получим информацию о секции
            _inf = self.get_section_inf(_sec)
            # теперь требуется получить реестр секции
            _reg = self.get_section_register(_sec)
            _records = []
            if _reg is not None:
                _records = _reg.get_records()

            if 0 == len(_sec_files) and 0 == len(_records):
                """ физически файлов нет и нет записей в реестре -> выходим """
                # print(self._debug_name + '.sync_section_content:', """ физически файлов нет и нет записей в реестре -> выходим """)
                return

            _2_add = []
            _2_delete = []
            if 0 == len(_sec_files) and 0 < len(_records):
                """ физически файлов нет, значит надо почистить реестр """
                # print(self._debug_name + '.sync_section_content:', """ физически файлов нет, значит надо почистить реестр """)
                _2_delete = _records

            if 0 < len(_sec_files) and 0 < len(_records):
                """ надо произвести сравнение """
                # print(self._debug_name + '.sync_section_content:', """ надо произвести сравнение """)
                _processed = []
                for _ri in _records:
                    _full_name = os.path.join(_inf['path'], _ri['name'])
                    # если в реестре есть запись а файла такого нет - то складываем на удаление
                    if _full_name not in _sec_files:
                        _2_delete.append(_ri)
                        continue
                    _processed.append(_full_name)

                # теперь требуется получить новые файлы если такие есть и добавить их
                if _processed:
                    _diff = [_fi for _fi in _sec_files if _fi not in _processed]
                    if _diff:
                        for _fi in _diff:
                            _new_rec = {}
                            # требуется создать запись - то есть сформировать словарь
                            _new_rec = self.__create_section_record(_sec, os.path.basename(_fi))
                            _2_add.append(_new_rec)

            if 0 < len(_sec_files) and 0 == len(_records):
                """ заполняем реестр новыми значениями """
                # print(self._debug_name + '.sync_section_content:', """ заполняем реестр новыми значениями """)
                for _fi in _sec_files:
                    _new_rec = {}
                    # требуется создать запись - то есть сформировать словарь
                    _new_rec = self.__create_section_record(_sec, os.path.basename(_fi))
                    _2_add.append(_new_rec)

            # print(self._debug_name + '.sync_section_content->_2_add', _2_add)
            # print(self._debug_name + '.sync_section_content->_2_delete', _2_delete)

            # сперва обрабатываем записи на удаление
            if _2_delete:
                self.__delete_section_records(_sec, _2_delete)

            # обрабатываем записи на вставку
            if _2_add:
                self.__add_section_records(_sec, _2_add)

    def __delete_section_records(self, _sec, _recs):
        _flg = False
        _reg = self.get_section_register(_sec)
        if _reg is not None:
            _lst = [_r['name'] for _r in _recs]
            _flg = _reg.remove_records(_lst)
        return _flg

    def __add_section_records(self, _sec, _recs):
        _flg = False
        _reg = self.get_section_register(_sec)
        if _reg is not None:
            _flg = _reg.add_records(_recs)
        return _flg

    def __init_content_stop_lst(self):
        self._content_stop_lst = ['_register.json', '_register.sqlite3']
        _sections_lst = self._mod_conf['Main']['work_sections'].split(',')

        _fn = self._mod_conf['Main']['register_name']
        if _sections_lst:
            self._content_stop_lst = []
            for _sec in _sections_lst:
                _sec = _sec.strip()
                if not self._mod_conf.has_section(_sec):
                    continue
                if 'use_register' in self._mod_conf[_sec] and 1 == self._mod_conf[_sec]['use_register']:
                    self._content_stop_lst.append(_fn + '.' + self._mod_conf[_sec]['register_type'])

    def get_section_register(self, _sec):
        # получим информацию о секции
        _inf = self.get_section_inf(_sec)
        _register = None
        if _inf:
            _type = _inf['register_type']
            if 'json' == _type:
                from .json_register import JsonRegister
                _register = JsonRegister()
            if 'sqlite3' == _type:
                from .sqlite_register import SqliteRegister
                _register = SqliteRegister()
        if _register is not None:
            _register.set_work_path(_inf['path'])
            _register.set_log_path(self._work_path)
            _fields = []
            _fields = self.__get_section_fields(_sec)
            _register.set_fields(_fields)
            _register.init()
        return _register

    def __create_section_record(self, _sec, _file):
        _fields = self.__get_section_fields(_sec)
        _rec = {}
        for _fld in _fields:
            _v = _fld['default']
            if 'name' == _fld['name']:
                _v = _file
            if 'mdate' == _fld['name']:
                _v = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            _rec[_fld['name']] = _v
        return _rec

    def __get_section_record_tpl(self, _sec):
        _fields = self.__get_section_fields(_sec)
        _tpl = {}
        for _fld in _fields:
            _tpl[_fld['name']] = _fld['default']
        return _tpl

    def __get_section_fields(self, _sec):
        _fields = []
        _fields.append({'name': 'name', 'type': 'TEXT', 'default': ''})
        _fields.append({'name': 'mdate', 'type': 'TEXT', 'default': ''})
        if 'backups' == _sec:
            _fields.append({'name': 'comment', 'type': 'TEXT', 'default': ''})
        if 'data' == _sec:
            _fields.append({'name': 'result', 'type': 'TEXT', 'default': ''})
            _fields.append({'name': 'map', 'type': 'TEXT', 'default': ''})
        if 'res' == _sec:
            _fields.append({'name': 'deleted', 'type': 'INTEGER', 'default': 0})
        return _fields

    def __get_columns_map(self, _sec):
        columns_map = {'id': 'name', 'toolbar': 'name', 'Type': 'name', 'name': 'name', 'Name': 'name',
                       'loaddate': 'mdate', 'usemap': 'map', 'loadresult': 'result'}
        # теперь добавим колонки для медиа
        # backups
        if 'backups' == _sec:
            columns_map['cmt'] = 'comment'
        return columns_map

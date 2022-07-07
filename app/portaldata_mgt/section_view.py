# -*- coding: utf-8 -*-
import os

from .mod_utils import ModUtils
from ..utilites.code_helper import CodeHelper


class SectionView():
    _class_file = __file__

    def __init__(self, name):
        _mod_utils = ModUtils()
        self.__mod_cfg = _mod_utils.get_config()
        if name not in self.__mod_cfg['Main']['work_sections']:
            raise Exception('Undefined section -> ' + name)
        self._name = name

    def get_register(self):
        _reg = object()
        return _reg

    def get_jqgrid_config(self):
        _mod_utils = ModUtils()
        cfg = _mod_utils.get_jqgrid_config()
        cfg['colModel'] = self.get_cols_table()
        # /section/<section>/list
        cfg['url'] = '/'.join(['section', self._name, 'list'])
        return cfg

    def get_columns_map(self):
        columns_map = {'id': 'name', 'toolbar': 'name', 'Type': 'name', 'name': 'name', 'Name': 'name',
                       'loaddate': 'mdate', 'usemap': 'map', 'loadresult': 'result'}
        # теперь добавим колонки для медиа
        # backups
        if 'backups' == self._name:
            columns_map['cmt'] = 'comment'
        return columns_map

    def get_cols_table(self):
        _lst = []
        _lst = self._get_table_cols()
        if 'backups' == self._name:
            _lst.append({ "label": "Комментарий", "index": "cmt", "name": "cmt", "width": 80, "align": "center",
                          "search": True, 'stype': 'text',
                            'searchoptions': {'sopt': ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
                        })
        return _lst

    def _get_table_cols(self):
        _lst = []
        _lst.append({"label": "", "index": "toolbar", "name": "toolbar", "width": 40, "sortable": False, "search": False})
        # {name: 'Type', index: 'Type', label: 'Type', hidden: True, sortable: False}
        _lst.append({"label": "Тип", "index": "Type", "name": "Type", "hidden": True, "search": False})
        _lst.append({"label": "ID", "index": "id", "name": "id", "hidden": True, "search": False})
        _lst.append({"label": "Имя", "index": "name", "name": "Name", "width": 90, "search": True, "stype": 'text',
             "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
             })
        _lst.append({"label": "Дата загрузки", "index": "loaddate", "name": "loaddate", "width": 40, "align": "center",
             "search": True, 'stype': 'text',
             "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
             })
        return _lst

    def is_deleted(self, item):
        _reg = self.get_register()
        _flg = False
        return _flg

    def rename_file(self, file, new_name):
        path = ''
        if '' != file:
            file = os.path.join(path, file)
        if '' != new_name:
            new_name = self.normalize_file_name(new_name)
            new_name = os.path.join(path, new_name)
        return self._rename_fsi(file, new_name)

    @staticmethod
    def _rename_fsi(old_path, new_path):
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
        return os.path.exists(new_path)

    def save_uploaded_file(self, http_file, file_name=''):
        _mod_utils = ModUtils()
        flg = True
        if http_file:
            work_file = file_name
            if not os.path.exists(work_file):
                http_file.save(work_file)
                flg = True
        return flg

    @staticmethod
    def secure_file_name(file_name):
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

    @staticmethod
    def normalize_file_name(self, file_name):
        res = file_name
        res = '_'.join(res.split(' '))
        res = self.translit_rus_string(res)
        return res

    @staticmethod
    def translit_rus_string(ru_str):
        res = CodeHelper.translit_rus_string(ru_str)
        return res

    @staticmethod
    def sort_files(file_list, ord='asc', attr='name'):
        sort_result = []
        sort_result = file_list
        revers = True if 'asc' != ord else False
        sort_result = sorted(sort_result, key=lambda x: x[attr], reverse=revers)
        return sort_result

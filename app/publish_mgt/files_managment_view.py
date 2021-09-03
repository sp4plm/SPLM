# -*- coding: utf-8 -*-

from os import path as ospath
from json import loads as jloads
from app import app_api
from .module_conf import PublishModConf
from .managment_view import ManagmentView
from .files_managment import FilesManagment


class FilesManagmentView(ManagmentView):
    _class_file = __file__
    _base_url = '/'

    def __init__(self):
        self._base_url = PublishModConf.MOD_WEB_ROOT  # '/publisher'
        super(FilesManagmentView, self).__init__()

    @staticmethod
    def get_columns_map():
        columns_map = {'id': 'name', 'toolbar': 'name', 'Type': 'name', 'name': 'name', 'Name': 'name',
                       'loaddate': 'mdate', 'usemap': 'map', 'loadresult': 'result'}
        # теперь добавим колонки для медиа
        # backups
        columns_map['cmt'] = 'comment'
        return columns_map

    def get_default_cols_table(self):
        cols = [
            {"label": "", "index": "toolbar", "name": "toolbar", "width": 40, "sortable": False, "search": False},
            # {name: 'Type', index: 'Type', label: 'Type', hidden: True, sortable: False}
            {"label": "Тип", "index": "Type", "name": "Type", "hidden": True, "search": False},
            {"label": "ID", "index": "id", "name": "id", "hidden": True, "search": False},
            {"label": "Имя", "index": "name", "name": "Name", "width": 90, "search": True, "stype": 'text',
              "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
            },
            {"label": "Дата загрузки", "index": "loaddate", "name": "loaddate", "width": 40, "align": "center",
             "search": True, 'stype': 'text',
             "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
            }
        ]
        if 'data' == self._current_folder:
            cols.append({ "label": "Результат", "index": "loadresult", "name": "loadresult", "width": 80,
                          "align": "center", "search": False, 'stype': 'text', "hidden": True,
                            'searchoptions': {'sopt': ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
                        })
        if 'backups' == self._current_folder:
            cols.append({ "label": "Комментарий", "index": "cmt", "name": "cmt", "width": 80, "align": "center",
                          "search": True, 'stype': 'text',
                            'searchoptions': {'sopt': ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
                        })
        return cols

    def get_jqgrid_config(self):
        cfg = ManagmentView.get_jqgrid_config()
        cfg['colModel'] = self.get_default_cols_table()
        cfg['url'] = self._base_url + '/getFiles/' + self._current_folder
        return cfg

    def get_navi(self):
        navi = []

        meta = FilesManagment()
        dirs_list = meta.get_root_content()
        current = self._current_folder
        if dirs_list:
            for idir in dirs_list:
                if not self.grant_access_to(idir):
                    continue
                inavi = {}
                inavi['label'] = idir['label']
                inavi['href'] = self._base_url + '/files/' + idir['name']
                inavi['current'] = False
                if current == idir['name']:
                    inavi['current'] = True
                navi.append(inavi)

        return navi

    def set_current(self, name):
        self._current_folder = name

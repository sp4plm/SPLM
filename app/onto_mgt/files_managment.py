# -*- coding: utf-8 -*-

import os
from datetime import datetime
from json import loads, dumps

from app import CodeHelper
from app.utilites.some_config import SomeConfig

MOD_DATA_PATH = os.path.dirname(os.path.abspath(__file__))

import re

from app import app_api

class FilesManagment():

    _dir_cfg_file = 'register.json'
    _delete_key = 'deleted'

    def __init__(self):
        self._app_config = app_api.get_app_config()
        self._root_dir = ''
        self._root_dir = os.path.join(MOD_DATA_PATH, 'data')
        self._cfg = None
        self._current_dir = ''
        self._current_dir = self._root_dir
        self._admin_role = ''
        self._oper_role = ''
        self._init_roles()
        self._init_data_struct()

    def _init_data_struct(self):
        if not os.path.exists(MOD_DATA_PATH) or not os.path.isdir(MOD_DATA_PATH):
            os.mkdir(MOD_DATA_PATH)
        if not os.path.exists(self._root_dir) or not os.path.isdir(self._root_dir):
            os.mkdir(self._root_dir)
        dir_list = ['ontos']
        for i_dir in dir_list:
            test = os.path.join(self._root_dir, i_dir)
            if not os.path.exists(test) or not os.path.isdir(test):
                os.mkdir(test)
                if 'media' == i_dir:
                    # возможно придется положить внутрь файл с указанием источника данных
                    continue # пропускаем так как это просто директория - данные будут лежать в другом месте
                test_file = os.path.join(test, self._dir_cfg_file)
                with open(test_file, 'w', encoding='utf8') as obj_file:
                    obj_file.write('[]')
        test_file = os.path.join(self._root_dir, self._dir_cfg_file)
        if not os.path.exists(test_file) or not os.path.isfile(test_file):
            with open(test_file, 'w', encoding='utf8') as obj_file:
                obj_file.write('[]')
        self.sync_description() # sync dirs

    def get_root_content(self):
        old_current_dir = self._current_dir
        self._current_dir = self._root_dir
        _json = self.read_description()
        if '' == _json:
            self.add_description()
            _json = self.read_description()
        self._current_dir = old_current_dir
        result = None
        result = loads(_json)
        result = sorted(result, key=lambda x: x['label'])
        return result

    def get_dir_source(self, relative):
        try_dir = self.get_dir_realpath(relative)
        self.set_current_dir(relative)
        _json = self.read_description()
        return loads(_json)

    def set_file_description(self, file, descr_part):
        flg = False
        _json = ''
        _json = self.read_description()
        descr = {}
        descr = loads(_json)
        if descr:
            _t = []
            flg = False
            for row in descr:
                if file == row['name']:
                    new_row = {**row, **descr_part}
                    flg = True
                else:
                    new_row = row
                _t.append(new_row)
            if _t:
                descr = _t
        if flg:
            _json = ''
            _json = dumps(descr)
            with open(self.get_description_file(), 'w', encoding='utf8') as file_p:
                file_p.write(_json)
        return flg

    def sync_description(self):
        """
         метод приводит в соответствие файлы и их описание в директории
         текущее описание
        """
        dir_cfg = self.read_description()
        descr = loads(dir_cfg)
        new_descr = []
        _acted = []
        files = self.get_dir_content()
        if files:
            if '' != descr:
                for fi in descr:
                    _acted.append(fi['fullname'])
                    if fi['fullname'] in files:
                        new_descr.append(fi)
            for fi in files:
                if fi in _acted:
                    continue
                new_descr.append(self.create_item_description(fi))
            dir_cfg = dumps(new_descr)
        else:
            dir_cfg = ''
        # переделать на метод _dump_register
        with open(self.get_description_file(), 'w', encoding='utf8') as file_p:
            # сперва надо очистить файл
            file_p.write('')
            file_p.write(dir_cfg)

    def sync_res_with_data(self):
        """"""
        # получили список результатов из директории данных
        data_res = self._get_data_results()
        new_res_reg = [] # будем создавать новый реестр результатов
        to_delete = [] # будем указывать имена файлов которые требуется удалить из директории
        _curr = self.get_current_dir()
        _list = self.get_dir_source('res')
        if 0 < len(_list):
            for ires in _list:
                if self.is_deleted(ires):
                    new_res_reg.append(ires)
                    continue
                res_name = ires['name']
                if res_name in data_res:
                    new_res_reg.append(ires)
                    continue
                to_delete.append(ires)
        if 0 < len(to_delete):
            """ бежим по списку и удаляем ве файлым """
            self._clear_files_by_list(to_delete, 'res')

        # удивительно но проверку поставлю
        if 0 < len(new_res_reg):
            """ сохраняем результат нового реестра """
            self._dump_register(new_res_reg)

    def _clear_files_by_list(self, _list, relative=''):
        """ удаляем файлы по списку из директории """
        flg = False
        if 0 < len(_list):
            work_dir = self.get_current_dir()
            if self.has_dir(relative):
                work_dir = self.get_dir_realpath(relative)
            if os.path.exists(work_dir) and os.path.isdir(work_dir):
                cnt = 0
                for del_file in _list:
                    try_del = os.path.join(work_dir, del_file)
                    if os.path.exists(try_del) and os.path.isfile(try_del):
                        os.unlink(try_del)
                        cnt += 1
                if cnt == len(_list):
                    flg = True
        return flg

    def _dump_register(self, register):
        if register:
            dir_cfg = dumps(register)
        else:
            dir_cfg = '[]'

        with open(self.get_description_file(), 'w', encoding='utf8') as file_p:
            # сперва надо очистить файл
            file_p.write('')
            file_p.write(dir_cfg)

    def _get_data_results(self):
        _curr = self.get_current_dir()
        _list = self.get_dir_source('data')
        data_results = []
        if 0 < len(_list):
            for idata in _list:
                data_results.append(idata['result'])
        self.set_current_dir(_curr.split(os.path.sep)[-1])
        return data_results

    def remove_item(self, dir_name, item_name):
        file = os.path.join(self.get_dir_realpath(dir_name), item_name)
        if os.path.exists(file) and os.path.isfile(file):
            os.unlink(file)
            old_cur_dir = self.get_current_dir()
            self.set_current_dir(dir_name)
            self.sync_description()
            self.set_current_dir(old_cur_dir)

    def get_item_description(self, dir_name, item_name):
        old_cur_dir = self.get_current_dir()
        self.set_current_dir(dir_name)
        _json = self.read_description()
        descr = loads(_json)
        d = []
        if descr:
            for d in descr:
                if item_name == d['name']:
                    break
        self.set_current_dir(old_cur_dir)
        return d

    def get_item_description_by_path(self, file_path):
        dir_name = ''
        file_name = ''
        path_info = file_path.split(os.path.sep)
        file_name = path_info[-1]
        dir_name = path_info[-2]
        return self.get_item_description(dir_name, file_name)

    def set_relative_by_path(self, file_path):
        dir_name = ''
        file_name = ''
        path_info = file_path.split(os.path.sep)
        file_name = path_info[-1]
        dir_name = path_info[-2]

    def add_description(self):
        # if '' == self.read_description():
        files = self.get_dir_content()
        if files:
            data = []
            for item in files:
                data.append(self.create_item_description(item))
            dir_cfg = dumps(data)
            with open(self.get_description_file(), 'w', encoding='utf8') as file_p:
                file_p.write(dir_cfg)

    def read_description(self):
        dir_cfg = ''
        file = None
        file = self.get_description_file()
        if not os.path.exists(file):
            self.add_description()
        if os.path.exists(file):
            file_p = None
            with open(file, 'r', encoding='utf8') as file_p:
                dir_cfg = file_p.read()
        if '' == dir_cfg:
            dir_cfg = '[]'
        return dir_cfg

    def create_item_description(self, item):
        info = {}
        relative = item.replace(self._root_dir + os.path.sep, '')
        info['fullname'] = item
        if os.path.isdir(item):
            roles = self._admin_role
            if -1 < relative.find('data') or -1 < relative.find('media'):
                roles += ',' + self._oper_role
            if -1 < relative.find('res'):
                roles = ''
            info['name'] = relative
            info['roles'] = roles
            info['label'] = self.__get_dir_label(relative)
        else:
            t = relative.split(os.path.sep)
            info['name'] = t[1]
            info['mdate'] = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

            from app.onto_mgt.ontology import Ontology
            info['prefix'] = Ontology().getOntoPrefix(item)


            if -1 < relative.find('maps'):
                info['active'] = False
            if -1 < relative.find('backups'):
                info['comment'] = ''
            if -1 < relative.find('data'):
                info['map'] = ''
                info['result'] = ''
            if -1 < relative.find('ontos'):
                info['result'] = ''
            if -1 < relative.find('res'):
                info[self._delete_key] = False # указание что после публикации данный элемент требуется удалить
        return info

    def is_deleted(self, item):
        """
        Проверяет установлен ли флаг удаления
        :param item:
        :return:
        """
        flg = False
        if self._delete_key in item:
            flg = bool(item[self._delete_key])
        return flg

    def remove_data_file(self, name):
        """"""

    def remove_file(self, name):
        """"""

    def mark_result_as_deleted(self, name):
        """"""

    def check_description(self, relative=''):
        try_dir = self._current_dir
        file = os.path.join(try_dir, self._dir_cfg_file)
        return os.path.exists(file) and \
                os.path.isfile(file)

    def get_description_file(self):
        return os.path.join(self._current_dir, self._dir_cfg_file)

    def search_files_by_descr(self, dir_name, descr):
        files = self.get_dir_source(dir_name)
        result = []
        if files:
            for ifile in files:
                if not isinstance(ifile, dict):
                    continue
                if self._search_compare_func(ifile, descr):
                    result.append(ifile)
        return result

    @staticmethod
    def _search_compare_func(ifile, fdescr):
        cnt_flg = 0
        for k, v in fdescr.items():
            if k in ifile and v == ifile.get(k):
                cnt_flg += 1
        return cnt_flg == len(fdescr.items())

    def get_dir_content(self, relative=''):
        try_dir = self._current_dir
        if '' != relative and self.has_dir(relative):
            try_dir = self.get_dir_realpath(relative)
        files = []
        list_items = os.scandir(try_dir)
        if list_items:
            _is_root_dir = (try_dir == self._root_dir)
            for item in list_items:
                if not _is_root_dir and item.is_dir():
                    continue
                if item.name == self._dir_cfg_file:
                    continue
                files.append(os.path.join(try_dir, item.name))
        return files

    def set_current_dir(self, relative):
        if '' != relative and self.has_dir(relative):
            self._current_dir = self.get_dir_realpath(relative)
            return True
        return False

    def get_current_dir(self):
        return self._current_dir

    def has_dir(self, relative):
        if '' == relative or not relative:
            return False
        try_dir = self.get_dir_realpath(relative)
        return os.path.exists(try_dir) and \
                os.path.isdir(try_dir)

    def get_dir_realpath(self, relative):
        return os.path.join(self._root_dir, relative)

    def edit_file(self, file_name, new_name='', http_file=None, dirname=''):
        path = self.get_dir_realpath(dirname)
        file = os.path.join(path, file_name)
        flg = False
        if os.path.exists(file):
            # заменить
            if http_file is not None:
                # только замена
                if '' == new_name or new_name == file_name:
                    new_name = file_name # для переименования нового загруженного файла
                try:
                    self.save_uploaded_file(http_file, dirname)
                    flg = True
                except Exception as ex:
                    flg = False
                    raise Exception(str(ex))
                if flg:
                    flg = self.remove_file(file_name, dirname) # удалять надо если сохранили
                # если удалили старый файл и сохранили новый
                if flg:
                    # теперь для переименования мы должны использовать
                    # имя сохраненного файла
                    file_name = self.secure_file_name(http_file.filename)
            # переименование
            if '' != new_name:
                flg = self.rename_file(file_name, new_name, dirname)
        return flg

    def rename_file(self, file, new_name, parent_dir=''):
        path = self.get_dir_realpath()
        if '' != parent_dir:
            path += os.path.sep + parent_dir
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

    def remove_file(self, name, dirname=''):
        dirname = self.get_dir_realpath(dirname)
        file = os.path.join(dirname, name)
        flg = False
        if os.path.exists(file) and os.path.isfile(file):
            os.remove(file)
            flg = True
        return flg

    @staticmethod
    def save_uploaded_file(http_file, file_name=''):
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
    def normalize_file_name(file_name):
        res = file_name
        res = '_'.join(res.split(' '))
        res = FilesManagment.translit_rus_string(res)
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

    def _init_roles(self):
        self._admin_role = self._app_config.get('data_storages.Manage.adminRole')
        self._oper_role = self._app_config.get('data_storages.Manage.operRole')

    @staticmethod
    def __get_dir_label(dir_name):
        if 'ontos' == dir_name:
            return 'Онтологии'
        # elif 'maps' == dir_name:
        #     return 'Карты'
        # elif 'backups' == dir_name:
        #     return 'Резерв. копии'
        # elif 'data' == dir_name:
        #     return 'Данные'
        # elif 'res' == dir_name:
        #     return 'Результаты'
        # elif 'media' == dir_name:
        #     return 'Медиа файлы'
        return dir_name

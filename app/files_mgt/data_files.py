# -*- coding: utf-8 -*-
import os
from json import loads
from shutil import rmtree

from .mod_utils import app_api, ModUtils


class DataFiles():

    def __init__(self):
        self._app_cfg = app_api.get_app_config()
        self._last_uploaded_file = ''
        self._errors = {}
        settings_files_path = self._app_cfg.get('main.Info.pubFilesDir')
        if settings_files_path is None:
            settings_files_path = 'static' # заглушка
        self._files_root = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                        settings_files_path)
        if ''!= self._files_root and not os.path.exists(self._files_root):
            os.mkdir(self._files_root)
        self._utils = ModUtils()
        self._ALLOWED_EXTENSIONS = self._utils.get_allowed_files()

    def remove_selected_items(self, items_list, dirname=''):
        path = self._get_path(dirname)
        errors = {}
        answer = {'deleted': [], 'all':[]}
        for item in items_list:
            test_path = os.path.join(path, item)
            if not os.path.exists(test_path.encode('utf-8')):
                continue
            if os.path.isfile(test_path.encode('utf-8')):
                if self.remove_file(item, dirname):
                    answer['deleted'].append(item)
                else:
                    errors[item] = 'Can not delete!'
            if os.path.isdir(test_path.encode('utf-8')):
                if self.remove_directory(item, dirname):
                    answer['deleted'].append(item)
                else:
                    errors[item] = 'Can not delete!'
        answer['errors'] = errors
        return answer

    @staticmethod
    def secure_file_name(file_name):
        a=''
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

    def edit_file(self, file_name, new_name='', http_file=None, dirname=''):
        path = self._get_path(dirname)
        file = os.path.join(path, file_name)
        flg = False
        if os.path.exists(file.encode('utf-8')):
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
                    # print(str(ex))
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
        path = self._get_path()
        if '' != parent_dir:
            path += os.path.sep + parent_dir
        if '' != file:
            file = os.path.join(path, file)
        if '' != new_name:
            new_name = self.secure_file_name(new_name)
            new_name = os.path.join(path, new_name)
        return self._rename_fsi(file, new_name)

    def remove_file(self, name, dirname=''):
        dirname = self._get_path(dirname)
        file = os.path.join(dirname, name)
        flg = False
        if os.path.exists(file.encode('utf-8')) and os.path.isfile(file.encode('utf-8')):
            os.remove(file)
            flg = True
        return flg

    def save_uploaded_file(self, http_file, dirname=''):
        if http_file and self.is_correct_file(http_file.filename):
            filename = self.secure_file_name(http_file.filename)
            dirname = self._get_path(dirname)
            work_file = os.path.join(dirname, filename)
            if not os.path.exists(work_file.encode('utf-8')):
                with open(work_file.encode('utf-8'), 'wb') as fp:
                    http_file.save(fp)
                self._last_uploaded_file = work_file
            else:
                raise Exception('File allready exists!')
        else:
            raise Exception('Is not a correct file type!')

    def is_correct_file(self, file_path) -> bool:
        flg = False
        flg = '.' in file_path and \
            file_path.rsplit('.', 1)[1] in self._ALLOWED_EXTENSIONS
        return flg

    def rename_directory(self, dirname, new_name, parent_dir=''):
        path = self._get_path()
        if '' != parent_dir:
            path += os.path.sep + parent_dir
        if '' != dirname:
            dirname = os.path.join(path, dirname)
        if '' != new_name:
            new_name = os.path.join(path, new_name)
        return self._rename_fsi(dirname, new_name)

    @staticmethod
    def _rename_fsi(old_path, new_path):
        if os.path.exists(old_path.encode('utf-8')):
            os.rename(old_path, new_path)
        return os.path.exists(new_path)

    def remove_directory(self, dirname, parent_dir=''):
        path = self._get_path()
        if '' != parent_dir:
            path += os.path.sep + parent_dir
        if '' != dirname:
            path += os.path.sep + dirname
        if os.path.exists(path.encode('utf-8')):
            rmtree(path.encode('utf-8'), ignore_errors=True)
            # os.rmdir(path)
        return not os.path.exists(path.encode('utf-8'))

    def save_directory(self, dirname, parent_dir=''):
        path = self._get_path()
        if '' != parent_dir:
            path += os.path.sep + parent_dir
        if '' != dirname:
            path += os.path.sep + dirname
        if not os.path.exists(path.encode('utf-8')):
            os.mkdir(path.encode('utf-8'))
        return os.path.exists(path.encode('utf-8'))

    def get_relative_path(self, path):
        return path.replace(self._files_root, '')

    def get_dir_source(self, dir_name=None):
        path = self._get_path(dir_name)
        flist = os.scandir(path.encode('utf-8'))
        return list(flist)

    def search_items(self, dir_name, filters):
        """ search items in the directory """
        file_list = self.get_dir_source(dir_name)
        search_list = []
        search_list = self.apply_jqgrid_filters(file_list, filters)
        return search_list

    """
    # operations
    # 'cn' - содержит | поиск подстроки в строке
    # 'nc' - не содержит | поиск подстроки в строке инверсия
    # 'eq' - равно | прямое сравнение
    # 'ne' - не равно | инверсия прямого сравнения
    # 'bw' - начинается | позиция 0 искомого вхождения
    # 'bn' - не начинается | инверсия от 0 позиции
    # 'ew' - заканчивается на | подстрока является концом строки
    # 'en' - не заканчивается на | инверсия что подстрока является концом строки
    """
    def apply_filter_rule(self, item, rule):
        """ непосредственное сравнение со значением с использованием операции """
        flg = False
        # {"field":"name","op":"cn","data":"15-22"}
        field = rule['field']
        oper = rule['op']
        val = rule['data']
        file_name = item.name.decode('utf-8', 'unicode_escape')
        if 'cn' == oper:
            # 'cn' - содержит | поиск подстроки в строке
            flg = (-1 < file_name.find(val))
        elif 'nc' == oper:
            # 'nc' - не содержит | поиск подстроки в строке инверсия
            flg = (-1 == file_name.find(val))
        elif 'eq' == oper:
            # 'eq' - равно | прямое сравнение
            flg = (val == item.name)
        elif 'ne' == oper:
            # 'ne' - не равно | инверсия прямого сравнения
            flg = (val != file_name)
        elif 'bw' == oper:
            # 'bw' - начинается | позиция 0 искомого вхождения
            flg = file_name.startswith(val)
        elif 'bn' == oper:
            # 'bn' - не начинается | инверсия от 0 позиции
            flg = not (file_name.startswith(val))
        elif 'ew' == oper:
            # 'ew' - заканчивается на | подстрока является концом строки
            flg = (file_name.endswith(val))
        elif 'en' == oper:
            # 'en' - не заканчивается на | инверсия что подстрока является концом строки
            flg = not (file_name.endswith(val))
        return flg

    def is_respond_to_rules(self, item, rules, group_op):
        """ сравнение значения с помощью операции """
        flg = False
        count = 0
        #  [{"field":"name","op":"cn","data":"15-22"}]
        for rule in rules:
            if self.apply_filter_rule(item, rule):
                count += 1
        if 'AND' == group_op and len(rules) == count:
            flg = True
        if 'OR' == group_op and 0 < count:
            flg = True
        return flg

    def apply_jqgrid_filters(self, source_list, filters):
        """ прменение поиска по файлам """
        result_list = []
        f_params = loads(filters)
        # filters	{"groupOp":"AND","rules":[{"field":"name","op":"cn","data":"15-22"}]}
        for item in source_list:
            flg = self.is_respond_to_rules(item, f_params['rules'], f_params['groupOp'])
            if flg:
                result_list.append(item)
        return result_list

    @staticmethod
    def sort_files(file_list, ord='asc'):
        sort_result = []
        sort_result = file_list
        revers = True if 'asc' != ord else False
        sort_result = sorted(sort_result, key=lambda x: x.name, reverse=revers)
        return sort_result

    def get_struct_tree(self):
        return self._read_dir()

    def _read_dir(self, dir_name=None):
        if dir_name is None:
            dir_name = self._files_root
        source_list = os.scandir(dir_name)
        layer = []
        fd = {}
        for item in source_list:
            if not item.is_dir():
                continue
            fd = self.cook_tree_item(item.name)
            fd['children'] = self._read_dir(os.path.join(dir_name, item.name))
            fd['path'] = os.path.join(dir_name.replace(self._files_root, ''), item.name)
            layer.append(fd)
        return layer

    def _get_path(self, dir_name=None):
        path = self._files_root.rstrip(os.path.sep)
        if type('z') == type(dir_name) and '' != dir_name:
            path = os.path.join(path, dir_name.replace('$', os.path.sep))
        return path.encode('utf-8').decode('utf-8', 'unicode_escape')

    def get_dir_path(self, dir_name):
        return self._get_path(dir_name)

    def to_relative_path(self, dir_path):
        return dir_path.replace(self._files_root, '')

    @staticmethod
    def cook_tree_item(label):
        return {'name': label, 'text' : label, 'path' : label, 'children': [],
                'state': {
                'opened' : False,
                'disabled' : False,
                'selected' : False
                }}

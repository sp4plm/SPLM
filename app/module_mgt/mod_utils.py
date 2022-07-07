# -*- coding: utf-8 -*-
import os
from json import loads


class ModUtils():
    _class_file = __file__
    _debug_name = 'ModuleMgtUtils'

    def __init__(self):
        self._last_uploaded_file = ''
        self._oper_errors = []

    def get_web_tpl_path(self):
        pth = self.get_mod_path('templates')
        return pth

    def get_web_static_path(self):
        pth = self.get_mod_path('static')
        return pth

    def get_mod_path(self, relative):
        relative = relative.lstrip(os.path.sep)
        pth = os.path.join(self.get_mod_dir(), relative)
        _k = 'data'
        if relative.startswith(_k):
            from app import app_api
            d_pth = app_api.get_mod_data_path(self.get_mod_name())
            pth = os.path.join(d_pth , relative.replace(_k, '').lstrip(os.path.sep))
        return pth

    def get_mod_name(self):
        _mod_pth = self.get_mod_dir()
        return os.path.basename(_mod_pth)

    def get_mod_dir(self):
        return os.path.dirname(self._class_file)

    def get_view_table_columns(self):
        _cols = []
        # _cols.append({"label": "", "index": "Toolbar", "name": "Toolbar", "width": 40, "sortable": False, "search": False})
        # _cols.append({"label": "Активная", "index": "Enabled", "name": "Enabled", "width": 40, "sortable": False, "search": False, 'align':'center'})
        _cols.append({"label": "Имя", "index": "Name", "name": "Name", "width": 90, "search": True, "stype": 'text',
              "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
            })
        _cols.append({"label": "Наименование", "index": "Label", "name": "Label", "width": 90, "search": True, "stype": 'text',
              "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
            })
        _cols.append({"label": "Описание", "index": "Description", "name": "Description", "width": 200, "search": True, "stype": 'text',
              "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
            })
        _cols.append({"label": "Встроенный", "index": "IsDefault", "name": "IsDefault", "width": 40, "sortable": True, "search": False, 'align':'center'})
        return _cols

    @staticmethod
    def sort_tbl_rows(src_list, ord='asc', attr='Name'):
        sort_result = []
        sort_result = src_list
        revers = True if 'asc' != ord else False
        sort_result = sorted(sort_result, key=lambda x: x[attr], reverse=revers)
        return sort_result

    def search_tbl_rows(self, _rows, filters):
        search_list = []
        search_list = self.apply_jqgrid_filters(_rows, filters)
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
        _fld_map = {'Name': 'name', 'Label': 'title', 'Description': 'description', 'IsDefault': 'name'}
        _check_val = ''
        _orig_fld = _fld_map[field] if field in _fld_map else ''
        if '' == _orig_fld:
            return flg
        _check_val = str(item[_orig_fld])
        if 'IsDefault' == field:
            if 'Да' == val and not _check_val.startswith('mod_'):
                flg = True
            if ('' == val or 'Нет' == val) and _check_val.startswith('mod_'):
                flg = True
            return flg
        if 'cn' == oper:
            # 'cn' - содержит | поиск подстроки в строке
            flg = (-1 < _check_val.find(val))
        elif 'nc' == oper:
            # 'nc' - не содержит | поиск подстроки в строке инверсия
            flg = (-1 == _check_val.find(val))
        elif 'eq' == oper:
            # 'eq' - равно | прямое сравнение
            flg = (val == _check_val)
        elif 'ne' == oper:
            # 'ne' - не равно | инверсия прямого сравнения
            flg = (val != _check_val)
        elif 'bw' == oper:
            # 'bw' - начинается | позиция 0 искомого вхождения
            flg = _check_val.startswith(val)
        elif 'bn' == oper:
            # 'bn' - не начинается | инверсия от 0 позиции
            flg = not (_check_val.startswith(val))
        elif 'ew' == oper:
            # 'ew' - заканчивается на | подстрока является концом строки
            flg = (_check_val.endswith(val))
        elif 'en' == oper:
            # 'en' - не заканчивается на | инверсия что подстрока является концом строки
            flg = not (_check_val.endswith(val))
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

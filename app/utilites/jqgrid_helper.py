# -*- coding: utf-8 -*-

import json


class JQGridHelper:
    _class_file = __file__
    _debug_name = 'JQGridHelper'

    def __init__(self):
        self._map = {}

    def set_map(self, map):
        self._map = map

    def map_file_descr_property(self, col):
        prop = col
        if self._map:
            if col in self._map:
                prop = self._map[col]
        return prop

    def apply_filter_rule(self, item, rule):
        """ непосредственное сравнение со значением с использованием операции """
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
        flg = False
        # {"field":"name","op":"cn","data":"15-22"}
        field = self.map_file_descr_property(rule['field'])
        oper = rule['op']
        val = rule['data']
        if 'cn' == oper:
            # 'cn' - содержит | поиск подстроки в строке
            flg = (-1 < item[field].find(val))
        elif 'nc' == oper:
            # 'nc' - не содержит | поиск подстроки в строке инверсия
            flg = (-1 == item[field].find(val))
        elif 'eq' == oper:
            # 'eq' - равно | прямое сравнение
            flg = (val == item[field])
        elif 'ne' == oper:
            # 'ne' - не равно | инверсия прямого сравнения
            flg = (val != item[field])
        elif 'bw' == oper:
            # 'bw' - начинается | позиция 0 искомого вхождения
            flg = item[field].startswith(val)
        elif 'bn' == oper:
            # 'bn' - не начинается | инверсия от 0 позиции
            flg = not (item[field].startswith(val))
        elif 'ew' == oper:
            # 'ew' - заканчивается на | подстрока является концом строки
            flg = (item[field].endswith(val))
        elif 'en' == oper:
            # 'en' - не заканчивается на | инверсия что подстрока является концом строки
            flg = not (item[field].endswith(val))
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
        f_params = json.loads(filters)
        # filters	{"groupOp":"AND","rules":[{"field":"name","op":"cn","data":"15-22"}]}
        for item in source_list:
            flg = self.is_respond_to_rules(item, f_params['rules'], f_params['groupOp'])
            if flg:
                result_list.append(item)
        return result_list

    @staticmethod
    def search_to_filter_json(source):
        """"""
        """
        # filters	{"groupOp":"AND","rules":[{"field":"name","op":"cn","data":"15-22"}]}
        searchField
        searchString
        searchOper
        """
        filters = '{"groupOp":"AND","rules":['
        if 'searchField' in source and 'searchOper' in source and 'searchString' in source:
            filters += '{'
            filters += '"field":"{fld}","op":"{op}","data":"{val}"'.format(
                fld=source['searchField'], op=source['searchOper'], val=source['searchString'])
            filters += '}'
        filters += ']}'
        return filters

    @staticmethod
    def get_jqgrid_config():
        cfg = {
            "datatype": "json",
            "mtype": "POST",
            "colModel": [],
            "pager": '',
            "rowNum": 10,
            "rowList": [10, 20, 30],
            "sortname": "id",
            "sortorder": "desc",
            "viewrecords": True,
            "gridview": True,
            "jsonReader": {"repeatitems": False},
            "autoencode": True,
            "autowidth": True,
            "caption": "",
            "toolbar": [True, "top"],
            "width": 1024
        }
        return cfg

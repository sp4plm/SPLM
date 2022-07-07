# -*- coding: utf-8 -*-
import os
from json import loads, dumps
from datetime import datetime


class JsonRegister():
    _class_file = __file__
    _debug_name = 'JsonRegister'
    _log_name = _debug_name + '.log'

    def __init__(self):
        self._work_path = ''  #  путь к директории реестра
        self._db = ''
        self._conn = None  # будем хранить дескриптор файла
        self._record_fields = []
        self._def_fields = [['name', 'TEXT', ''], ['mdate', 'TEXT', '']]
        self._log_path = ''
        self._cols = []
        self._props = []
        self._name = ''
        self._table = None  # будем хранить список записей реестра при длительных операциях

    def remove_record(self, file_name):
        _flg = False
        # на всякий пожарный проверим есть ли запись для указанного файла
        _filter = [{'field':'name', 'op': 'eq', 'data': file_name}]
        _recs = self.get_records(filter=_filter)
        if 0 == len(_recs):
            _msg = self._debug_name + '.remove_record-> no record for {}!' . format(file_name)
            self.__to_log(_msg)
            return _flg

        _t = []
        self._table = self._get_all_data()
        for _r in self._table:
            if _r['name'] == file_name:
                _flg = True
                continue
            _t.append(_r)
        if _flg:
            self._table = None
            self._table = _t
            _t = None
            self._dump_register(self._table)
        return _flg

    def update_records(self, _recs_dict):
        _flg = False
        """ Ожидаем что _recs_dict : key is file name, value is dictionary with field-new_value"""
        _t = 0
        _cnt = len(_recs_dict.keys())
        self._table = self._get_all_data()
        for _file in _recs_dict:
            _t_flg = False
            _t_flg = self.update_record(_file, _recs_dict[_file], True)
            if _t_flg:
                _t += 1
            else:
                _msg = self._debug_name + '.update_records -> Can not update ' + _file + ' info!'
                self.__to_log(_msg)
        if _cnt == _t:
            _flg = True
        if _flg:
            self._dump_register(self._table)
        return _flg

    def update_record(self, _name, _new_data, _use_multi=False):
        _flg = False
        _cols = self._get_columns_list()
        _cols_map = [_c['name'] for _c in _cols]
        _types = {_c['name']: _c['type'] for _c in _cols}
        _t = {}
        for _c in _new_data:
            if _c not in _cols_map:
                continue
            _v = self.__val_to_type(_new_data[_c], _types[_c])
            _t[_c] = _v
        _new_data = None
        _new_data = _t
        if _new_data and self._table:
            if not _use_multi:
                self._table = self._get_all_data()
            for _i in range(0, len(self._table)):
                _fn = self._table[_i]['name']
                if _fn != _name:
                    continue
                self._table[_i] = dict(**self._table[_i], **_new_data)
        if not _use_multi:
            self._dump_register(self._table)
        return _flg

    def get_records(self, fields=[], filter=None, limit=10, offset=0, sort=None, sord='ASC'):
        _lst = []
        _json = self._get_all_data()
        _lst = loads(_json)

        if _lst:
            if filter is not None:
                _lst = self.__apply_filters(_lst, filter)

            """ теперь после поиска надо отсортировать """

            _lst = self.__sort_files(_lst, sort, sord)
            _lst = _lst[offset:offset + limit] if len(_lst) > limit else _lst
        return _lst

    def count_records(self, filter=None):
        _cnt = 0
        # read file
        _lst = self.get_records(filter)
        _cnt = len(_lst)
        _lst = None # clearing
        return _cnt

    def add_records(self, _recs):
        _flg = False
        _cols = self._get_columns_list()
        self._table = self._get_all_data()
        _new_recs = []
        if self._table:
            _indexed = {_r['name']: _r for _r in self._table}
            for _nf in _recs:
                if _nf['name'] not in _indexed:
                    _new_recs.append(_nf)
        if _new_recs:
            for _nr in _new_recs:
                self._table.append(_nr)
            self._dump_register(self._table)
            _flg = True
        return _flg

    def init(self):
        self._db = os.path.join(self._work_path, 'register.json')
        is_new = False
        if not os.path.exists(self._db):
            open(self._db, 'w').close()
            is_new = True
        if is_new:
            self._name = os.path.basename(self._work_path)

    def _get_all_data(self):
        dir_cfg = ''
        if not os.path.exists(self._db):
            self.init()
        if os.path.exists(self._db):
            file_p = None
            with open(self._db, 'r', encoding='utf8') as file_p:
                dir_cfg = file_p.read()
        if '' == dir_cfg:
            dir_cfg = '[]'
        return dir_cfg

    def _dump_register(self, register):
        if register:
            dir_cfg = dumps(register)
        else:
            dir_cfg = '[]'
        if not os.path.exists(self._db):
            self.init()
        with open(self._db, 'w', encoding='utf8') as file_p:
            # сперва надо очистить файл
            file_p.write('')
            file_p.write(dir_cfg)

    def set_work_path(self, _work_path):
        self._work_path = str(_work_path)

    def set_log_path(self, _log_path):
        self._log_path = str(_log_path)

    def get_name(self):
        return os.path.basename(self._work_path)

    def set_fields(self, _fields):
        """
        Метод устанавливает список свойст записи на основании которого будет создана таблица.
        Обязательные ключи(свойства записи): name и type, имя и тип соответственно
        :param _fields: список свойст записи,
        :return:
        """
        self._record_fields = _fields

    def __val_to_type(self, _val, _type):
        _res = _val
        if 'NONE' == _type:
            _res = None
        if 'INTEGER' == _type:
            _res = int(_res)
        if 'REAL' == _type:
            _res = float(_res)
        if 'TEXT' == _type:
            _res = str(_res)
        if 'NUMERIC' == _type:
            _res = self.__to_numeric(_res)
        # print(self._debug_name + '.__val_to_type->_res', _res)
        return _res

    @staticmethod
    def __to_numeric(_val):
        _hex = 'abcdefghABCDEFGH'
        _digits = '1234567890'
        _res = ''
        _t = str(_val)
        for i in _t:
            if i not in _hex and i not in _digits:
                continue
            _res += str(i)
        return _res

    def __get_work_files(self):
        _lst = []
        # надо получить список файлов в рабочей директории
        _t = os.scandir(self._work_path)
        # исключить файлы реестра с расширениями json b sqlite3
        _stop_list = ['register.json', 'register.sqlite3']
        for _f in _t:
            if _f.is_dir():
                continue
            _n = _f.name
            if _n.startswith('.'):
                continue
            if _n in _stop_list:
                continue
            _lst.append(_n)
        return _lst

    def __sort_files(self, file_list, ord='asc', attr='name'):
        sort_result = []
        sort_result = file_list
        revers = True if 'asc' != ord else False
        sort_result = sorted(sort_result, key=lambda x: x[attr], reverse=revers)
        return sort_result

    def __apply_filter_rule(self, item, rule):
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
        field = rule['field']
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

    def __is_respond_to_rules(self, item, rules, group_op):
        """ сравнение значения с помощью операции """
        flg = False
        count = 0
        #  [{"field":"name","op":"cn","data":"15-22"}]
        for rule in rules:
            if self.__apply_filter_rule(item, rule):
                count += 1
        if 'AND' == group_op and len(rules) == count:
            flg = True
        if 'OR' == group_op and 0 < count:
            flg = True
        return flg

    def __apply_filters(self, source_list, filters):
        """ прменение поиска по файлам """
        result_list = []
        f_params = filters
        # filters	{"groupOp":"AND","rules":[{"field":"name","op":"cn","data":"15-22"}]}
        for item in source_list:
            flg = self.__is_respond_to_rules(item, f_params['rules'], f_params['groupOp'])
            if flg:
                result_list.append(item)
        return result_list

    def __has_col(self, cname):
        _flg = False
        _cols = self._get_columns_list()
        for _c in _cols:
            if cname == _c['name']:
                _flg = True
                break
        return _flg

    def _get_columns_list(self):
        if not self._cols:
            self._cols = []
            self._cols.append({'name': 'name', 'type': 'TEXT', 'default': ''})
            self._cols.append({'name': 'mdate', 'type': 'TEXT', 'default': ''})
            if 'backups' == self._name:
                self._cols.append({'name': 'comment', 'type': 'TEXT', 'default': ''})
            if 'data' ==  self._name:
                self._cols.append({'name': 'result', 'type': 'TEXT', 'default': ''})
                self._cols.append({'name': 'map', 'type': 'TEXT', 'default': ''})
            if 'res' ==  self._name:
                self._cols.append({'name': 'deleted', 'type': 'INTEGER', 'default': 0})
        return self._cols

    def __to_log(self, msg):
        log_file = os.path.join(self._log_path, self._log_name)
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as fp:
                fp.write('')
        with open(log_file, 'a', encoding='utf-8') as fp:
            time_point = datetime.now().strftime("%Y%m%d %H-%M-%S")
            _msg = '[' + time_point + '] ' + msg + "\n"
            fp.write(_msg)

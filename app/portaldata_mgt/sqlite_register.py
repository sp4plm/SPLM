# -*- coding: utf-8 -*-
import json
import os
import sqlite3
from datetime import datetime


class SqliteRegister(object):
    _class_file = __file__
    _debug_name = 'SqliteRegister'
    _log_name = _debug_name + '.log'

    def __init__(self):
        self._work_path = ''  #  путь к директории реестра
        self._db = ''
        self._conn = None
        self._record_fields = []
        self._def_fields = [['name', 'TEXT', ''], ['mdate', 'TEXT', '']]
        self._log_path = ''
        self._cols = []
        self._props = []
        self._sords = ['ASC', 'DESC', 'asc', 'desc']

    def sync_description(self):
        # надо получить список файлов в рабочей директории
        _available_files = self.__get_work_files()
        # получить список существующих записей в таблице
        _available_recs = []
        _msg = self._debug_name + '.sync_description->try get available records'
        self.__to_log(_msg)
        _available_recs = self.get_records()
        # сравнить два списка по имени
        _recs_to_delete = []
        _files_to_add = []
        _files_has_records = []
        if _available_recs:
            _msg = self._debug_name + '.sync_description->_available_files: ' + str(_available_files)
            # self.__to_log(_msg)
            _msg = self._debug_name + '.sync_description->_available_recs: ' + str(list(_available_recs))
            # self.__to_log(_msg)
            for _ri in _available_recs:
                _msg = self._debug_name + '.sync_description->_ri[\'name\']: ' + str(_ri['name'])
                # self.__to_log(_msg)
                has_file = _ri['name'] in _available_files
                if has_file:
                    _files_has_records.append(_ri['name'])
                if not has_file:
                    _recs_to_delete.append(_ri)
            _files_to_add = list(set(_available_files)-set(_files_has_records))
        else:
            _files_to_add = _available_files
        # удалить записи для которых файлов не нашлось
        if _recs_to_delete:
            pass
        # добавить записи для файлов без записи
        if _files_to_add:
            self._add_records(_files_to_add)

    def update_records(self, _recs_dict):
        _flg = False
        """ Ожидаем что _recs_dict : key is file name, value is dictionary with field-new_value"""
        _t = 0
        _cnt = len(_recs_dict.keys())
        for _file in _recs_dict:
            _t_flg = False
            _t_flg = self.update_record(_file, _recs_dict[_file], True)
            if _t_flg:
                _t += 1
            else:
                _msg = self._debug_name + '.update_records -> Can not update ' + _file + ' info!'
                # self.__to_log(_msg)
        if _cnt == _t:
            _flg = True
        self._conn.commit()
        return _flg

    def update_record(self, _name, _new_data, _use_multi=False):
        _flg = False
        _update_clause = ''
        _cols = self._get_columns_list()
        _cols_map = [_c['name'] for _c in _cols]
        _types = {_c['name']: _c['type'] for _c in _cols}
        _t = []
        for _c in _new_data:
            if _c not in _cols_map:
                continue
            _v = _c + ' = ' + str(self.__val_to_type(_new_data[_c], _types[_c]))
            _t.append(_v)
        _update_clause = ', '.join(_t)
        _q = ''
        _q += 'UPDATE'
        _q += ' ' + self.__get_tbl_name()
        _q += ' SET'
        _q += ' ' + _update_clause
        _q += ' WHERE'
        _q += ' name=\'' + _name + '\''
        try:
            _res = self.__exec(_q).fetchone()
            # print(self._debug_name + '.update_record->_res:', _res)
            _flg = True # считаем если не произошла ошибка, то все обнавилось
        except Exception as ex:
            print(self._debug_name + '.update_record->Exception:', ex.args)
            self.__to_log(self._debug_name + '.update_record->Exception: %s' % str(ex.args))
        if not _use_multi:
            self._conn.commit()
        return _flg

    def add_records(self, _records):
        _flg = False
        _ins_cols_construct = ''
        _cols = self._get_columns_list()
        _ins_cols_construct = ', '.join([_c['name'] for _c in _cols])
        _q = 'INSERT INTO {}'.format(self.__get_tbl_name())
        _q += ' (' + _ins_cols_construct + ')'
        _q += ' VALUES'

        _insert_construct = ''
        _v = []
        for _ri in _records:
            _1f = []
            for _c in _cols:
                _set_val = ''
                _set_val = self._get_prop_def_value(_c['name'])
                if _c['name'] in _ri:
                    _set_val = _ri[_c['name']]
                if 'TEXT' == _c['type']:
                    _set_val = '"' + _set_val + '"'
                _1f.append(str(_set_val))
            _v.append('(' + ', '.join(_1f) + ')')
        _insert_construct = ', '.join(_v)
        if '' != _insert_construct:
            _q += _insert_construct
            try:
                _res = self.__exec(_q)
                # print(self._debug_name + '.add_records -> :_res ', str(_res))
                self._conn.commit()
                _flg = True
            except Exception as ex:
                _msg = self._debug_name + '.add_records->Exception: {}'.format(ex.args)
                # print(_msg)
                self.__to_log(_msg)
        return _flg

    def _add_records(self, _files):
        _flg = False
        _recs = self.get_records()
        _exists = []
        if _recs:
            _exists = [_fr['name'] for _fr in _recs]
        _ins_cols_construct = ''
        _cols = self._get_columns_list()
        _ins_cols_construct = ', '.join([_c['name'] for _c in _cols])
        _q = 'INSERT INTO {}'.format(self.__get_tbl_name())
        _q += ' ({})'.format(_ins_cols_construct)
        _q += ' VALUES'

        _insert_construct = ''
        _v = []
        for _fi in _files:
            if _fi in _exists:
                continue
            _1f = []
            for _c in _cols:
                _set_val = ''
                # надо установить значения по умолчанию для колонок
                _set_val = self._get_prop_def_value(_c['name'])
                if 'name' == _c['name']:
                    _set_val = _fi
                if 'mdate' == _c['name']:
                    _set_val = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                if 'TEXT' == _c['type']:
                    _set_val = '"' + _set_val + '"'
                _1f.append(str(_set_val))
            _v.append('(' + ', '.join(_1f) + ')')
        _insert_construct = ', '.join(_v)
        if '' != _insert_construct:
            _q += _insert_construct
            _res = self.__exec(_q)
            # print('add_records:', str(_res))
            self._conn.commit()

        for _fi in _files:
            flg = self._add_record(_fi)

        return _flg

    def _add_record(self, file_name):
        _flg = False
        # на всякий пожарный проверим есть ли запись для указанного файла
        _recs = self.get_records(filter=[{'field':'name', 'oper': '=', 'value': file_name}])
        if 0 < len(_recs):
            _msg = self._debug_name + '._add_record-> {} already have record!' . format(file_name)
            # self.__to_log(_msg)
            return _flg
        _ins_cols_construct = ''
        _cols = self._get_columns_list()
        _ins_cols_construct = ', '.join([_c['name'] for _c in _cols])
        _q = 'INSERT INTO {}' . format(self.__get_tbl_name())
        _q += ' ({})' . format(_ins_cols_construct)
        _q += ' VALUES'
        _insert_construct = ''
        _v = []
        for _c in _cols:
            _set_val = ''
            # надо установить значения по умолчанию для колонок
            _set_val = self._get_prop_def_value(_c['name'])
            if 'name' == _c['name']:
                _set_val = file_name
            if 'mdate' == _c['name']:
                _set_val = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            if 'TEXT' == _c['type']:
                _set_val = '"' + _set_val + '"'
            _v.append(str(_set_val))
        _insert_construct = ', '.join(_v)
        #  на вход передаем словарь или список словарей для вставки одной и более
        _q += '({})' . format(_insert_construct)
        _res = self.__exec(_q)
        # print('add_record:', str(_res))
        self._conn.commit()
        return _flg

    def _get_prop_def_value(self, name):
        _val = ''
        _props = self.__get_record_props()
        for _p in _props:
            if _p[0] == name:
                _val = _p[2]
                break
        return _val

    def _get_columns_list(self):
        if not self._cols:
            self._cols = []
            _q = 'PRAGMA table_info(\'{}\')' . format(self.__get_tbl_name())
            _res = self.__exec(_q)
            if _res:
                for _r in _res:
                    _d = dict(_r)
                    _d1 = {}
                    _d1['name'] = _d['name']
                    _d1['type'] = _d['type']
                    _d1['default'] = _d['dflt_value']
                    self._cols.append(_d1)
        return self._cols

    def get_records(self, fields=None, filter=None, limit=-1, offset=0, sort=None, sord='ASC'):
        _res = []
        _str_fields = '*'
        # определим колонки таблицы
        if fields:
            _str_fields = ', '.join(fields)
        _q = 'SELECT %s FROM %s ' % (_str_fields, self.__get_tbl_name())
        # возможно нам передали фильтр
        if filter is not None and filter:
            # print(self._debug_name + '.get_records->filter', filter)
            _q += ' ' + self.__filter_2_where(filter)
        if sort is not None:
            if self.__has_col(sort):
                if sord not in self._sords:
                    sord = 'ASC'
                _q += ' ORDER BY ' + str(sort) + ' ' + sord.upper()
        if 0 < limit:
            _q += ' LIMIT ' + str(limit)
        if 0 < offset:
            _q += ' OFFSET ' + str(offset)
        _t = []
        try:
            _t = self.__exec(_q).fetchall()
        except Exception as ex:
            _msg = self._debug_name + '.get_records->Exception: {}'.format(ex.args)
            # print(_msg)
            self.__to_log(_msg)
        for _r in _t:
            _res.append(dict(_r))
        return _res

    def __has_col(self, cname):
        _flg = False
        _cols = self._get_columns_list()
        for _c in _cols:
            if cname == _c['name']:
                _flg = True
                break
        return _flg

    def count_records(self, filter=None):
        _cnt = 0
        _q = 'SELECT COUNT(1) FROM %s ' % self.__get_tbl_name()
        # возможно нам передали фильтр
        if filter is not None and filter:
            # print(self._debug_name + '.count_records->filter', filter)
            _q += ' ' + self.__filter_2_where(filter)
        try:
            _t = self.__exec(_q).fetchone()
            _cnt = _t[0]
        except Exception as ex:
            _msg = self._debug_name + '.count_records->Exception: {}'.format(ex.args)
            # print(_msg)
            self.__to_log(_msg)
        return _cnt

    def remove_record(self, file_name):
        _flg = False
        # на всякий пожарный проверим есть ли запись для указанного файла
        _filter = [{'field':'name', 'op': 'eq', 'data': file_name}]
        _recs = self.get_records(filter=_filter)
        if 0 == len(_recs):
            _msg = self._debug_name + '.remove_record-> no record for {}!' . format(file_name)
            # self.__to_log(_msg)
            _flg = True
            return _flg
        _q = 'DELETE FROM %s ' % self.__get_tbl_name()
        if _filter is not None and filter:
            _q += ' ' + self.__filter_2_where(_filter)
        _t = []
        try:
            _t = self.__exec(_q).fetchone()
        except Exception as ex:
            _msg = self._debug_name + '.remove_record->Exception: {}'.format(ex.args)
            # print(_msg)
            self.__to_log(_msg)
        _recs = self.get_records(filter=_filter)
        _flg = 0 == len(_recs)
        if _flg:
            self._conn.commit()
        return _flg

    def remove_records(self, _lst):
        _flg = False
        # на всякий пожарный проверим есть ли запись для указанного файла
        _filter = [{'field':'name', 'op': 'in', 'data': _lst}]
        _recs = self.get_records(filter=_filter)
        if 0 == len(_recs):
            _msg = self._debug_name + '.remove_record-> no records for {}!' . format(str(_lst))
            # self.__to_log(_msg)
            _flg = True
            return _flg
        _q = 'DELETE FROM %s ' % self.__get_tbl_name()
        if _filter is not None and filter:
            _q += ' ' + self.__filter_2_where(_filter)
        _t = []
        try:
            _t = self.__exec(_q).fetchone()
        except Exception as ex:
            _msg = self._debug_name + '.remove_record->Exception: {}'.format(ex.args)
            # print(_msg)
            self.__to_log(_msg)
        _recs = self.get_records(filter=_filter)
        _flg = 0 == len(_recs)
        if _flg:
            self._conn.commit()
        return _flg

    def __get_escape_clause(self):
        return 'ESCAPE \'\\\''

    def __get2escape(self):
        return ['_', '%']

    def __has2escape(self, _in):
        _flg = False
        _2esc = self.__get2escape()
        for _n in _2esc:
            if _in.find(_n):
                _flg = True
        return _flg

    def __escape_str(self, _in):
        _out = ''
        _out = _in
        if self.__has2escape(_in):
            _2esc = self.__get2escape()
            for _s in _2esc:
                _out = _out.replace(_s, '\\' + _s)
        return _out

    def __filter_2_where(self, _filter):
        _where = ''
        if not _filter:
            return _where
        if isinstance(_filter, str):
            _filter = json.loads(_filter)
        if 'rules' in _filter:
            _filter = _filter['rules'] # для sql нам нужны только правила
        _cols = self._get_columns_list()
        _cols_map = [_c['name'] for _c in _cols]
        _types = {_c['name']: _c['type'] for _c in _cols}
        # filter=[{'field':'name', 'oper': '=', 'value': file_name}]
        _if = []
        _escape_clause = self.__get_escape_clause()
        # print(self._debug_name + '.__filter_2_where->_cols_map', _cols_map)
        for _fi in _filter:
            # print(self._debug_name + '.__filter_2_where->_fi', _fi)
            if _fi['field'] not in _cols_map:
                continue
            _expression = ''
            _has_escaped = False
            _val = _fi['data']
            if 'cn' == _fi['op']:
                # 'cn' - содержит | поиск подстроки в строке
                _val = str(_val)
                _has_escaped = self.__has2escape(_val)
                _val = '\'%' + self.__escape_str(_val) + '%\''
                _expression = _fi['field'] + ' LIKE ' + _val
                if _has_escaped:
                    _expression += ' ' + _escape_clause
                pass  # flg = (-1 < item[field].find(val))
            elif 'nc' == _fi['op']:
                # 'nc' - не содержит | поиск подстроки в строке инверсия
                _val = str(_val)
                _has_escaped = self.__has2escape(_val)
                _val = '"%' + self.__escape_str(_val) + '%"'
                _expression = _fi['field'] + ' NOT LIKE ' + _val
                if _has_escaped:
                    _expression += ' ' + _escape_clause
                pass  # flg = (-1 == item[field].find(val))
            elif 'eq' == _fi['op']:
                # 'eq' - равно | прямое сравнение
                _val = self.__val_to_type(_fi['data'], _types[_fi['field']])
                _expression = _fi['field'] + ' = ' + str(_val)
                pass  # flg = (val == item[field])
            elif 'ne' == _fi['op']:
                # 'ne' - не равно | инверсия прямого сравнения
                _val = self.__val_to_type(_fi['data'], _types[_fi['field']])
                _expression = _fi['field'] + ' <> ' + str(_val)
                pass  # flg = (val != item[field])
            elif 'bw' == _fi['op']:
                # 'bw' - начинается | позиция 0 искомого вхождения
                _val = str(_val)
                _has_escaped = self.__has2escape(_val)
                _val = '"' + self.__escape_str(_val) + '%"'
                _expression = _fi['field'] + ' LIKE ' + _val
                if _has_escaped:
                    _expression += ' ' + _escape_clause
                pass  # flg = item[field].startswith(val)
            elif 'bn' == _fi['op']:
                # 'bn' - не начинается | инверсия от 0 позиции
                _val = str(_val)
                _has_escaped = self.__has2escape(_val)
                _val = '"' + self.__escape_str(_val) + '%"'
                _expression = _fi['field'] + ' NOT LIKE ' + _val
                if _has_escaped:
                    _expression += ' ' + _escape_clause
                pass  # flg = not (item[field].startswith(val))
            elif 'ew' == _fi['op']:
                # 'ew' - заканчивается на | подстрока является концом строки
                _val = str(_val)
                _has_escaped = self.__has2escape(_val)
                _val = '"%' + self.__escape_str(_val) + '"'
                _expression = _fi['field'] + ' LIKE ' + _val
                if _has_escaped:
                    _expression += ' ' + _escape_clause
                pass  # flg = (item[field].endswith(val))
            elif 'en' == _fi['op']:
                # 'en' - не заканчивается на | инверсия что подстрока является концом строки
                _val = str(_val)
                _has_escaped = self.__has2escape(_val)
                _val = '"%' + self.__escape_str(_val) + '"'
                _expression = _fi['field'] + ' NOT LIKE ' + _val
                if _has_escaped:
                    _expression += ' ' + _escape_clause
                pass  # flg = not (item[field].endswith(val))
            elif 'in' == _fi['op']:
                # 'in' - включает | самоделка для оператора IN в SQL
                if isinstance(_val, str):
                    _val = _val.split(',')
                if isinstance(_val, list):
                    for _i in range(0, len(_val)):
                        _val[_i] = self.__val_to_type(_val[_i], _types[_fi['field']])
                _val = ', '.join(_val)
                _expression = _fi['field'] + ' IN (' + _val + ')'
                pass  # flg = not (item[field].endswith(val))
            #_if.append(_fi['field'] + _fi['oper'] + self.__val_to_type(_fi['value'], _types[_fi['field']]))
            _if.append(_expression)
        if 1 < len(_if):
            _where = ' AND '.join(_if)
        else:
            _where = _if[0] if _if else ''
        if '' != _where:
            _where = 'WHERE ' + _where
        return _where

    def __val_to_type(self, _val, _type):
        _res = _val
        if 'NONE' == _type:
            _res = None
        if 'INTEGER' == _type:
            _res = int(_res)
        if 'REAL' == _type:
            _res = float(_res)
        if 'TEXT' == _type:
            _res = '\'' + str(_res.strip('\'')) + '\''
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

    def init(self):
        self._db = os.path.join(self._work_path, 'register.sqlite3')
        is_new = False
        if not os.path.exists(self._db):
            open(self._db, 'w').close()
            is_new = True
        self._conn = sqlite3.connect(self._db)
        self._conn.row_factory = sqlite3.Row
        if is_new:
            self.__create()

    def drop(self):
        self._db = os.path.join(self._work_path, 'register.sqlite3')
        self._conn = None
        if os.path.exists(self._db):
            os.unlink(self._db)
        return os.path.exists(self._db)

    def set_fields(self, _fields):
        """
        Метод устанавливает список свойст записи на основании которого будет создана таблица.
        Обязательные ключи(свойства записи): name и type, имя и тип соответственно
        :param _fields: список свойст записи,
        :return:
        """
        self._record_fields = _fields

    def __get_tbl_name(self):
        _name = 'reg_'
        _name += os.path.basename(self._work_path)
        return _name

    def set_work_path(self, _work_path):
        self._work_path = str(_work_path)

    def set_log_path(self, _log_path):
        self._log_path = str(_log_path)

    def __create(self):
        try:
            self.__create_table()
        except Exception as ex:
            print(self._debug_name + '.__create->Exception:', ex.args)
            self.__to_log(self._debug_name + '.__create->Exception: %s' % str(ex.args))

    def __create_table(self):
        _cre_tbl = 'CREATE TABLE %s (' % self.__get_tbl_name()
        _cre_tbl += self.__props_to_tbl_create()
        _cre_tbl += ');'
        try:
            self.__exec(_cre_tbl)
        except Exception as ex:
            print(self._debug_name + '.__create_table->Exception:', ex.args)
            self.__to_log(self._debug_name + '.__create_table->Exception: %s' % str(ex.args))

    def __props_to_tbl_create(self):
        _props = self.__get_record_props()
        _cols = [_f[0] + ' ' + _f[1] for _f in _props]
        return ','.join(_cols)

    def __get_record_props(self):
        if not self._props:
            self._props = []
            _def_ind = {_i[0]: _i for _i in self._def_fields}
            self._props = self._def_fields
            if self._record_fields:
                for _f in self._record_fields:
                    if _f['name'] not in _def_ind:
                        self._props.append([_f['name'], _f['type'], _f['default']])
        return self._props

    def __exec(self, com):
        _res = None
        if self._conn:
            _msg = self._debug_name + '.__exec->com: ' + com
            # self.__to_log(_msg)
            with self._conn as c:
                _cur = c.cursor()
                _res = _cur.execute(com)
        return _res

    def __exec_multi(self, com, _args):
        _res = None
        if self._conn:
            with self._conn as c:
                _cur = c.cursor()
                _res = _cur.executemany(com, _args)
        return _res

    def __to_log(self, msg):
        log_file = os.path.join(self._log_path, self._log_name)
        if not os.path.exists(log_file):
            with open(log_file, 'w', encoding='utf-8') as fp:
                fp.write('')
        with open(log_file, 'a', encoding='utf-8') as fp:
            time_point = datetime.now().strftime("%Y%m%d %H-%M-%S")
            _msg = '[' + time_point + '] ' + msg + "\n"
            fp.write(_msg)

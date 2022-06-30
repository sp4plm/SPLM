# -*- coding: utf-8 -*-
import os
from datetime import datetime

from app import CodeHelper


class UsersAuthLogger:
    _class_file=__file__
    _debug_name='UsersAuthLogger'
    _log_ext = 'log'

    def __init__(self, work_dir, file_name):
        # $accessLog = new PortalLog(portalApp::getInstance()->getSetting('main.Info.userAccLogName'));
        self._export_data = []
        self._rotation_circle = 40
        self._logs_dir = ''
        if os.path.exists(work_dir) and os.path.isdir(work_dir):
            self._logs_dir = work_dir
        else:
            self._logs_dir = os.path.dirname(self._class_file)
        if not file_name or not isinstance(file_name, str):
            file_name = self._debug_name
        self._file_name = file_name
        self._write_point = self._get_write_point_init()

    def format_export_data(self):
        _formatted = []
        _formatted = self._to_html()
        return _formatted

    def export(self):
        self._export_data = self.txt2list()
        return self.format_export_data()

    def _to_html(self):
        _html = ''
        _html += '<table border="1">'
        _html += '<tbody>'
        for _row in self._export_data:
            _html += '<tr>'
            for _col in _row:
                _html += '<td>'+_col+'</td>'
            _html += '</tr>'
        _html += '</tbody>'
        _html += '</table>'
        return _html

    def txt2list(self, use_k=False):
        headers = ['AuthDate', 'AuthTime', 'User']
        _res = []
        _t = []
        _txt = self.get_log_text()
        data_lst = _txt.split("\n") # [] # $this->read(true);
        if data_lst:
            for row in data_lst:
                if not row:
                    continue
                _t = row.split('] [')
                _t[0] = _t[0].lstrip('[')
                _t[2] = _t[2].rstrip(']')
                _nr = CodeHelper.dict_combine(headers, _t) if use_k else _t
                _res.append(_nr)
        return _res

    def get_log_text(self):
        _txt = ''
        _txt = CodeHelper.read_file(self._write_point)
        return _txt

    def write(self, msg):
        if not self._check_file():
            self._create_write_point()
        msg = self._cook_msg(msg)
        file_path = self._get_write_point()
        CodeHelper.write_to_file(file_path, msg)

    def _get_write_point(self):
        # проверяем условие ротации
        f_size = os.stat(self._write_point).st_size # Output is in bytes
        limit_size = 1048576 # 1 мегабайт
        limit_size = 4194304 # 4 мегабайт
        if limit_size < f_size:
            """"""
            # применяем механизм ротации
            # нужна ротация логов
            self._rotate()
        # возвращаем
        return self._write_point

    def _rotate(self):
        # получаем имя файла
        fname = os.path.basename(self._write_point)
        fdir = os.path.dirname(self._write_point)
        fname = fname[:fname.rfind('.')]
        files = os.scandir(fdir)
        catched = {}
        for it in files:
            # print('seached file:', it.name)
            if it.name.startswith(fname):
                f_ind = it.name.replace(fname, '').replace('.' + self._log_ext, '')
                if not f_ind:
                    f_ind = '0'
                else:
                    f_ind = f_ind.lstrip('.')
                catched[f_ind] = it.name
        # print('catched:', catched)
        _keys = catched.keys()
        _keys = sorted(_keys)[::-1]
        # print('_keys:', _keys)
        for _k in _keys:
            _int_ind = int(_k)
            _int_ind +=1
            if self._rotation_circle < _int_ind:
                delete_file = os.path.join(fdir, catched[_k])
                # print('delete_file', delete_file)
                os.unlink(delete_file)
            else:
                new_name = fname + '.' + str(_int_ind) + '.' + self._log_ext
                copy_file = os.path.join(fdir, new_name)
                src_file = os.path.join(fdir, catched[_k])
                # print('copy_file', src_file)
                # print('to_file', copy_file)
                with open(src_file, 'rb') as sfp:
                    with open(copy_file, 'wb') as tfp:
                        tfp.write(sfp.read())
        # теперь создаем базу
        self._create_write_point()

    def _cook_msg(self, txt):
        _now = self._get_time_point()
        _str = '[' + _now.strftime("%Y-%m-%d") + '] [' + _now.strftime("%H:%M:%S") + '] [' + txt + ']' + "\n"
        return _str

    def _create_write_point(self):
        return CodeHelper.add_file(self._write_point)

    def _check_file(self):
        return CodeHelper.check_fs_item(self._write_point)

    def _get_time_point(self):
        time_point = datetime.now()
        return time_point

    def _get_write_point_init(self):
        logs_dir = self._get_dir()
        file_name = self._get_file_name()
        file_path = os.path.join(logs_dir, file_name)
        return file_path

    def _get_dir(self):
        if not os.path.exists(self._logs_dir):
            os.mkdir(self._logs_dir)
        return self._logs_dir

    def _get_file_name(self):
        file_name = self._file_name + '.' + self._log_ext
        return file_name

# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

from app import app_api
from app.utilites.code_helper import CodeHelper

"""
work_files.total - количество файлов данных для обработки
work_files.done - счетчик обрабатываемых файлов данных
upload_files.total - количество файлов, которое требуется загрузить в хранилище
upload_files.done - счетчик загруженных файлов в результате процесса
onto_files.[имя файла онтологии] -  файлы онтологии? которые загружаем и используем для конвертации
errors - ключ для сохранения ошибок
"""


class DataPublishLogger:
    _class_file = __file__
    _default_log_name = 'publish.proclog'

    def __init__(self, file_proc=''):
        self._proc_file = ''
        self._idata = {}
        self._init_idata()
        mod_data_path = app_api.get_mod_data_path('portaldata_mgt')
        proc_logger_file = os.path.join(mod_data_path, self._default_log_name)
        if '' == file_proc:
            file_proc = proc_logger_file
        self.set_process_file(file_proc)
        self._debug = False

    def get_state(self):
        self._restore()
        return self._idata

    def get(self, key):
        self._restore()
        _parsed = self._parse_key(key)
        rec_val = None
        rec_val = self._idata
        for step in _parsed:
            if isinstance(rec_val, dict):
                if step in rec_val:
                    rec_val = rec_val[step]
            if isinstance(rec_val, list):
                real_key = int(step)
                if len(rec_val) > real_key > -1:
                    rec_val = rec_val[real_key]
        return rec_val

    def set(self, key, val):
        """ """
        _parsed = self._parse_key(key)
        if _parsed[0] not in self._idata:
            self._idata[_parsed[0]] = {}
        if isinstance(self._idata[_parsed[0]], dict):
            self._idata[_parsed[0]][_parsed[1]] = val
        if isinstance(self._idata[_parsed[0]], list):
            self._idata[_parsed[0]].append(val)
        self._dump()
        if self._debug:
            print('DataPablishLogger.set: DEBUG -> key: ', key, ' | val: ', val)
            print('DataPablishLogger.set: DEBUG -> ', self._idata)

    def _parse_key(self, str_key):
        return str_key.split('.')

    def set_process_file(self, file_path):
        if '' != file_path:
            self._proc_file = file_path
        # self._restore()

    def _restore(self):
        self._idata = self._read_file()

    def _dump(self):
        self._write_file(self._idata)

    def _init_idata(self):
        self._idata['work_files'] = {'total': 0, 'done': 0}
        self._idata['converted_files'] = {'total': 0, 'done': 0}
        self._idata['upload_files'] = {'total': 0, 'done': 0}
        self._idata['onto_files'] = {}
        self._idata['errors'] = []
        # self._idata['crash_message'] = ''

    def _write_file(self, idata):
        if '' != self._proc_file and not CodeHelper.check_file(self._proc_file):
            CodeHelper.add_file(self._proc_file)
        txt = json.dumps(idata)
        CodeHelper.write_to_file(self._proc_file, txt, mod='w')

    def _read_file(self):
        txt = ''
        txt = CodeHelper.read_file(self._proc_file)
        content = None
        if '' != txt:
            content = json.loads(txt)
        else:
            content = {}
        return content

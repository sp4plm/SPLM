# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime

from app.utilites.code_helper import CodeHelper


class ProcessLogger:
    _class_file = __file__

    def __init__(self, file_path=''):
        self._nL = "\n"
        self._write_point = ''
        self.set_log_file(file_path)

    def write(self, msg):
        if not self._check_file():
            self._create_write_point()
        time_point = self._get_time_point()
        msg = '[{}] - {}' . format(time_point, msg)
        CodeHelper.write_to_file(self._write_point, msg + self._nL)

    def _get_time_point(self):
        time_point = datetime.now().strftime("%Y%m%d %H-%M-%S")
        return time_point

    def _create_write_point(self):
        return CodeHelper.add_file(self._write_point)

    def _check_file(self):
        return CodeHelper.check_file(self._write_point)

    def set_log_file(self, file_path):
        if '' != file_path:
            self._write_point = file_path

    def clear_log_file(self):
        if self._check_file():
            CodeHelper.add_file(self._write_point)

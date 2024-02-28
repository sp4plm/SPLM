# -*- coding: utf-8 -*-
import os
import configparser
from app import app_api
from app.utilites.utilites import Utilites
from .mod_conf import ModConf


class ModEnv:
    _class_file=__file__
    _debug_name='clsModEnv'
    _work_dir_name = 'env'

    def __init__(self):
        self._work_dir = os.path.join(os.path.dirname(self._class_file), self._work_dir_name)
        if not os.path.exists(self._work_dir):
            raise Exception(self._debug_name + '.__init__-> No working directory!')
        conf_path = ModConf.get_mod_path(self._work_dir_name)
        self._main = app_api.get_config_util()(conf_path)

    @property
    def cfg(self):
        return self._main
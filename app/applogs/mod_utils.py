# -*- coding: utf-8 -*-
import os.path


class ModUtils:
    _class_file = __file__
    _debug_name = 'AppLogsUtils'
    _tpl_file_ext = 'html'

    def get_error_logs(self, root):
        _lst = []
        if os.path.isdir(root):
            _items = os.scandir(root)
            from .config import Config
            fname = Config.error_file
            for _it in _items:
                _t = str(_it.name)
                if not _t.startswith(fname):
                    continue
                _lst.append(_t)
        return _lst

    def read_log_file(self, root):
        _lines = []
        name = ''
        if os.path.isdir(root):
            from .config import Config
            name = os.path.join(root, Config.error_file)
        if os.path.exists(name):
            with open(name, 'r', encoding="utf-8") as fp:
                _lines = fp.readlines()
        return _lines

    def get_template(self, name):
        _mod_name = self.get_mod_name()
        _f_ext = '.' + self._tpl_file_ext
        if not name:
            name = 'index'
        if not name.endswith(_f_ext):
            name += _f_ext
        _pth = os.path.join(_mod_name, name)
        return _pth

    def get_mod_name(self):
        _pth = self.get_mod_path()
        _name = os.path.basename(_pth)
        return _name

    def get_mod_path(self):
        _pth = os.path.dirname(self._class_file)
        return _pth

# -*- coding: utf-8 -*-
import os
import json

from app.admin_mgt.admin_conf import AdminConf
from app.utilites.code_helper import CodeHelper


class PortalNavigation(AdminConf):
    _class_file = __file__
    _debug_name = 'PortalNavigation'
    _register = 'navi_blocks.json'

    def __init__(self):
        self._files_path = os.path.join(AdminConf.DATA_PATH, 'navi')

    def get_section_by_code(self, code):
        current = None
        lst = self.get_sections()
        if lst:
            for sec in lst:
                if sec['code'] == code:
                    current = sec
                    break
        return current

    def get_sections(self):
        lst = []
        sections_file = self._register
        sections_path = os.path.join(self._files_path, sections_file)
        if CodeHelper.check_file(sections_path):
            lst = self._read_json_file(sections_path)
        return lst

    def get_sections_navi(self, section_code, user=None):
        lst = []
        sections_file = section_code + '.json'
        sections_path = os.path.join(self._files_path, sections_file)
        if CodeHelper.check_file(sections_path):
            lst = self._read_json_file(sections_path)
        if lst and user is not None:
            _t = []
            for _it in lst:
                """ требуется проверить роли пользователя и роли пункта меню """
                # отсеиваем не подходящее
                if not self._check_user_access(_it, user):
                    continue
                _t.append(_it)
            lst = _t
        return lst

    def _check_user_access(self, point, user):
        flg = False
        if 'roles' not in point:
            flg = True
        else:
            if not point['roles']:
                flg = True
            else:
                _roles = point['roles'].split(',')
                for _r in _roles:
                    if user.has_role(_r):
                        flg = True
                        break
        return flg

    def _read_json_file(self, file_path):
        data = None
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf8') as fp:
                _cont = fp.read()
                if _cont:
                    try:
                        data = json.loads(_cont)
                    except Exception as ex:
                        raise Exception(self._debug_name + '._read_json_file.Exception: {}'.format(str(ex)))
        return data

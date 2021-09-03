# -*- coding: utf-8 -*-

# from os import path as ospath
from app import app_api
from app.utilites.jqgrid_helper import JQGridHelper


class ManagmentView:
    _class_file = __file__

    def __init__(self):
        self._app_config = app_api.get_app_config()
        self._current = ''
        self._current_side_navi = ''
        self._current_folder = ''
        self._current_tool = ''
        self._called_args = None
        self._current_data_role = ''

    def get_selected_folder(self):
        fld = 'data'
        """
        _currentSideNavi = '';
        _currentFolder = '';
        _currentTool = '';
        _calledArgs = null;
        if (!empty($this->_calledArgs) && 'files' == $this->_currentSideNavi) {
            if (array_key_exists(1, $this->_calledArgs)) {
                $dir = $this->_calledArgs[1];
            }
        }
        return $dir;
        """
        return fld

    def get_navi(self):
        return []

    @staticmethod
    def get_jqgrid_config():
        return JQGridHelper.get_jqgrid_config()

    def set_current(self, name):
        self._current = name

    def grant_access_to(self, item):
        flg = False
        if '' != self._current_data_role:
            roles = ''
            if 'roles' in item:
                roles = item['roles']

            point = roles.find(self._current_data_role)
            if -1 < point:
                flg = True
        return flg

    def set_data_role(self, role_name):
        self._current_data_role = role_name

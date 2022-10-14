# -*- coding: utf-8 -*-
import os
from .driver import Driver


class ModApi:
    _class_file = __file__
    _debug_name = 'LDAPAuthAPI'

    def __init__(self):
        self._orig = None  # экземпляр класса выполняющего авторизацию в системе
        _pth = os.path.join(os.path.dirname(__file__), 'cfg')
        if os.path.exists(_pth):
            self._orig = Driver(_pth)

    def login(self, login, auth_secret):
        flg = False
        try:
            flg = self._orig.login(login, auth_secret)
        except Exception as ex:
            print(self._debug_name + '.login.Exception: ', ex)
            flg = False
        return flg

    def logout(self):
        pass

    def get_user(self, login):
        user = None
        try:
            user = self._orig.get_user(login)
        except Exception as ex:
            print(self._debug_name + '.get_user.Exception:', ex)
            user = None
        return user
        pass

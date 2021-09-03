# -*- coding: utf-8 -*-
from app.admin_mgt.auth import *

class AuthProvider:

    type = ''

    def __init__(self):
        self._driver = None
        self._init_driver()

    def login(self, login, auth_secret):
        flg = False
        try:
            flg = self._driver.login(login, auth_secret)
        except Exception as ex:
            print('AuthProvider.login Error: ', ex)
            flg = False
        return flg

    def get_user(self, login):
        user = None
        try:
            user = self._driver.get_user(login)
        except Exception as ex:
            print('AuthProvider.get_user Error:', ex)
            user = None
        return user

    def _init_driver(self):
        self._driver = LDAPAuthProvider()

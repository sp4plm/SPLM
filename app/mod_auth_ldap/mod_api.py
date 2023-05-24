# -*- coding: utf-8 -*-
import os
from .driver import Driver


class ModApi:
    _class_file = __file__
    _debug_name = 'LDAPAuthAPI'

    def __init__(self, _ext_pth_logs=''):
        self._orig = None  # экземпляр класса выполняющего авторизацию в системе
        self._logs_ext_path = ''  # директория которю может назначить пользователь API
        if _ext_pth_logs:
            self._logs_ext_path = str(_ext_pth_logs)
        _pth = os.path.join(os.path.dirname(__file__), 'cfg')
        if os.path.exists(_pth):
            self._orig = Driver(_pth)
            # теперь надо придумать как получить директорию внешнюю для логирования
            # в каком виде хранить логи и как группировать принимает решение данный драйвер
            _log_pth = ''
            # хорошо бы хранить логи в app/data path!!!
            if self._logs_ext_path:
                _log_pth = self._logs_ext_path
            else:
                try:
                    from app import app_api
                    _log_pth = app_api.get_logs_path()
                except: pass
            self._orig.set_logs_dir(_log_pth)

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

    def set_external_logs_path(self, _pth):
        """
        Метод устанавливает внешнюю директорию для логов
        :param _pth:
        :return:
        """
        if _pth and os.path.exists(_pth) and os.path.isdir(_pth):
            self._logs_ext_path = str(_pth)
            if self._orig is not None:
                self._orig.set_logs_dir(self._logs_ext_path)

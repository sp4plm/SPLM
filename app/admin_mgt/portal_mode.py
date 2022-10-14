# -*- coding: utf-8 -*-
import os
import inspect
from json import loads, dumps
from datetime import datetime


class PortalMode():
    _class_file = __file__
    _debug_name = 'PortalMode'

    def __init__(self, _name):
        """
        :param _name: имя режима
        """
        self.__secure_call()
        self._name = str(_name)
        self._redirect_http = False
        self._white_eps = []  # endpoints for flask.url_for
        self._target_ep = ''  # endpoint for flask.url_for
        self._data = None  # содержимое файла
        self._store = None  # функционал работы с хранением данных
        self._caller_mod = ''
        self._caller_debug = {'file': '', 'func': ''}
        self._started = 0
        self.__sync()

    def get_target(self):
        return self._target_ep

    def set_target(self, _target):
        self._target_ep = str(_target)
        self.__sync()

    def get_opened(self):
        _lst = self._white_eps
        if '' != self._target_ep:
            _lst.append(self._target_ep)
        return _lst

    def set_opened(self, _white_lst):
        if isinstance(_white_lst, list):
            self._white_eps = _white_lst
            self.__sync()

    def update_opened(self, _val):
        _val = str(_val)
        if _val not in self._white_eps:
            self._white_eps.append(_val)
            self.__sync()

    def __sync(self):
        if not isinstance(self._data, dict):
            self._data = {}
        # self._name = str(_name)
        self._data['_name'] = self._name
        # self._redirect_http = False
        self._data['_redirect_http'] = self._redirect_http
        # self._white_eps = []  # endpoints for flask.url_for
        self._data['_white_eps'] = self._white_eps
        # self._target_ep = ''  # endpoint for flask.url_for
        self._data['_target_ep'] = self._target_ep
        # self._caller_mod = ''
        self._data['_caller_mod'] = self._caller_mod
        # self._caller_debug = {'file': '', 'func': ''}
        self._data['_caller_debug'] = self._caller_debug

    def __fill(self):
        if not isinstance(self._data, dict):
            _msg = self._debug_name + '.__fill.Exception: No data to fill mode attributes!'
            print(_msg)
            raise Exception(_msg)
        # self._name = str(_name)
        self._name = self._data['_name']
        # self._redirect_http = False
        self._redirect_http = self._data['_redirect_http']
        # self._white_eps = []  # endpoints for flask.url_for
        self._white_eps = self._data['_white_eps']
        # self._target_ep = ''  # endpoint for flask.url_for
        self._target_ep = self._data['_target_ep']
        # self._caller_mod = ''
        self._caller_mod = self._data['_caller_mod']
        # self._caller_debug = {'file': '', 'func': ''}
        self._caller_debug = self._data['_caller_debug']
        self._started = self._data['_started'] # всемя старта

    def enable(self):
        _flg = False
        if self._store is not None:
            if self._store.exists():
                raise Exception('The mode "' + self._name + '" is already enabled!')
            _data = ''
            _step = inspect.stack()[1]
            self._caller_debug['file'] = _step[1]
            self._caller_debug['func'] = _step[3]
            # вычислять модуль будем относительно себя
            _app_path = os.path.dirname(os.path.dirname(self._class_file))
            _caller_rel = _step[1].replace(_app_path + os.path.sep, '')
            self._caller_mod = _caller_rel.split(os.path.sep)[0]
            # теперь надо добавить к открытым url странички административной части портала
            if self._redirect_http:
                self.update_opened('admin_mgt.static')  # статичные файлы административного интерфейса
                self.update_opened('admin_mgt.__modes_management')  # управление режимами портала
                self.update_opened('admin_mgt.__drop_portal_mode')  # сброс режима портала
                self.update_opened('portal.login')  # login
                self.update_opened('portal.logout')  # logout
            self.__sync()
            self._started = datetime.now().timestamp()
            _t = self._data
            _t['_started'] = self._started
            try:
                _data = dumps(_t)
            except Exception as ex:
                print(self._debug_name + '.enable.Exception on saving mode attributes to file: ' + str(ex))
                raise ex
            self._store.write(_data)
            _flg = True
        return _flg

    def disable(self):
        _flg = False
        if self._store is not None:
            if not self._store.exists():
                raise Exception('No enabled modes!')
            self._store.remove()
            _flg = True
        return _flg

    def __secure_call(self):
        _step = inspect.stack()[2]
        # print(self._debug_name + '.__init__->inspect_stack[2][1]: ' + str(_step[1]))
        # print(self._debug_name + '.__init__->inspect_stack[2][3]: ' + str(_step[3]))
        _caller_dir = os.path.dirname(self._class_file)
        _caller_file = 'portal_mode_util.py'
        _caller_funcs = ['set_portal_mode', 'get_current', 'get_modes']

        _caller_file = os.path.join(_caller_dir, _caller_file)
        if _caller_file != _step[1] or _step[3] not in _caller_funcs:
            raise Exception('Incorrect call order!')

    def set_store(self, _store):
        if _store is None:
            raise Exception('Undefined store point!')
        if '__ModeStore' != str(type(_store).__name__):
            raise Exception('Incorrect store point!')
        self._store = _store
        if self._store.exists():
            _data = self._store.read()
            try:
                self._data = loads(_data)
            except Exception as ex:
                print(self._debug_name + '.set_store->Exception on filling mode attributes from file data: ' + str(ex))
                raise ex
            # теперь надо заполнить все переменные
            self.__fill()

    def get_start_time(self, _tpl=''):
        """
        :param _tpl: '%Y-%m-%d %H:%M:%S' default -> ''
        :return: int timestamp or string formated by template arg
        """
        _res = self._started
        if '' != _tpl:
            _res = datetime.utcfromtimestamp(_res).strftime(_tpl)
        return _res

    def enable_redirect(self):
        self._redirect_http = True
        self.__sync()

    def disable_redirect(self):
        self._redirect_http = False
        self.__sync()

    def use_redirecting(self):
        return self._redirect_http

    def get_name(self):
        return self._name

    def get_initiator(self):
        return self._caller_mod

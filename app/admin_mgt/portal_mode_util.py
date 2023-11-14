# -*- coding: utf-8 -*-
"""
Класс реализует функциональность управления режимами работы портала
Например - публикация данных(загрузка ttl файлов в TripleStore)

Достоверно известно:
Режим работы портала должен знать:
- перенаправлять запросы к порталу по http или нет
- адрес страницы для перенаправления всех запросов
- список адресов для портала, перенаправление которых не требуется - т.е. исключено
- кто включил режим
- когда включен был режим
Режим работы портала должен уметь:
- включаться - оставлять отметку однозначно говорящуюю что режим включен и это он
- выключаться - удалять отметку о включении режима
- блокировать попытку включения режима другого или такого же
- выдавать информацию кто включил
- выдавать информацию когда включился
"""

import os
import inspect


class PortalModeUtil():
    _class_file = __file__
    _debug_name = 'admin_mgt.PortalModeUtil'
    _mode_pref = 'pwm'
    _mode_suff = '.pid'

    def __init__(self):
        self.__secure_call()
        pass

    def get_modes(self):
        """
        Метод возвращает список действующих режимов работы портала
        :return:
        """
        _lst = []
        _dir = self.__get_work_dir()
        _files = self.__get_files()
        if _files:
            from app.admin_mgt.portal_mode import PortalMode
            for _file in _files:
                _f = os.path.join(_dir, _file)
                _mode_store = self.__cook_mode_store(_f)
                _mode_name = self._get_mode_name(_f)
                _mode = PortalMode(_mode_name)
                _mode.set_store(_mode_store)
                _lst.append(_mode)
        return _lst

    def get_current(self, _name=''):
        """
        Метод возвращает экземпляр класса режима работы портала или None
        :return:
        """
        _mode = None
        # _name = ''  # видимо данная опция должна быть частью имени файла
        _file = self.__search_mode_file(_name)
        if '' == _name:
            _name = self._get_mode_name(_file)
        if _name and os.path.exists(_file):
            from app.admin_mgt.portal_mode import PortalMode
            _mode = PortalMode(_name)
            _mode_store = self.__cook_mode_store(_file)
            _mode.set_store(_mode_store)
        return _mode

    def set_portal_mode(self, _name):
        _mode = None
        from app.admin_mgt.portal_mode import PortalMode
        _file = self.__search_mode_file(_name)
        if _file and os.path.exists(_file):
            _name = self._get_mode_name(_file)
            print(self._debug_name + '.set_portal_mode: Portal mode "' + _name + '" is enabled!')
            return _mode
        _mode = PortalMode(_name)
        _file = self.__cook_mode_file_name(_name)
        _mode_store = self.__cook_mode_store(_file)
        _mode.set_store(_mode_store)
        return _mode

    def drop(self, _portal_mode):
        if 'PortalMode' != str(type(_portal_mode).__name__):
            print(self._debug_name + '.drop.Exception: Incorrect argument "_portal_mode" type -> ' + str(type(_portal_mode).__name__))
            return
        _name = _portal_mode.get_name()
        _file = self.__cook_mode_file_name(_name)
        if os.path.exists(_file):
            os.unlink(_file)

    def _get_mode_name(self, _file):
        _name = os.path.basename(_file)
        _name = _name.replace(self._mode_pref + '_', '')
        _name = _name.replace('_' + self._mode_suff, '')
        return _name

    def __is_mode_file(self, _name):
        _name = os.path.basename(_name)
        _flg = False
        if _name.startswith(self._mode_pref + '_') and \
            _name.endswith('_' + self._mode_suff):
            _flg = True
        return _flg

    def __cook_mode_file_name(self, _name):
        _file_name = str(_name)
        _file_name = self._mode_pref + '_' + _file_name
        _file_name = _file_name + '_' + self._mode_suff
        _dir = self.__get_work_dir()
        _file_name = os.path.join(_dir, _file_name)
        return _file_name

    def __secure_call(self):
        _step = inspect.stack()[2]
        # print(self._debug_name + '.__init__->inspect_stack[2][1]: ' + str(_step[1]))
        # print(self._debug_name + '.__init__->inspect_stack[2][3]: ' + str(_step[3]))
        _caller_dir = os.path.dirname(self._class_file)
        _caller_file = 'mod_api.py'
        _caller_funcs = ['get_portal_mode_util']

        _caller_file = os.path.join(_caller_dir, _caller_file)
        if _caller_file != _step[1] or _step[3] not in _caller_funcs:
            raise Exception('Incorrect call order!')

    def __cook_mode_store(self, _file):
        _store = None

        _cur_pref = self._mode_pref
        _cur_suff = self._mode_suff

        class __ModeStore():
            _class_file = __file__
            _debug_name = 'PortalModeStore'

            _mode_pref = _cur_pref
            _mode_suff = _cur_suff

            def __init__(self, _file):
                self.__secure_call()
                # не проверяем на создание, так как файл создастся когда включится режим
                # и удалиться когда выключится
                self._point = _file

            def check_name(self, _name):
                _flg = False
                _test = self._mode_pref + '_' + str(_name) + '_' + self._mode_suff
                if os.path.basename(self._point) == _test:
                    _flg = True
                return _flg

            def exists(self):
                _flg = False
                if os.path.exists(self._point) and os.path.isfile(self._point):
                    _flg = True
                return _flg

            def __secure_call(self):
                _step = inspect.stack()[2]
                # print(self._debug_name + '.__init__->inspect_stack[2][1]: ' + str(_step[1]))
                # print(self._debug_name + '.__init__->inspect_stack[2][3]: ' + str(_step[3]))
                _caller_dir = os.path.dirname(self._class_file)
                _caller_file = os.path.basename(self._class_file)
                _caller_funcs = ['__cook_mode_store']

                _caller_file = os.path.join(_caller_dir, _caller_file)
                if _caller_file != _step[1] or _step[3] not in _caller_funcs:
                    raise Exception('Incorrect call order!')

            def read(self):
                _res = ''
                if os.path.exists(self._point):
                    with open(self._point, 'r', encoding='utf-8') as _fp:
                        _res = _fp.read()
                return _res

            def write(self, _data):
                _flg = False
                with open(self._point, 'w', encoding='utf-8') as _fp:
                    _fp.write(_data)
                    _flg = True
                return _flg

            def remove(self):
                if os.path.exists(self._point):
                    os.unlink(self._point)

        _store = __ModeStore(_file)

        return _store

    def __search_mode_file(self, name=''):
        _dir = self.__get_work_dir()
        _find = self.__get_files()
        _file = ''
        if _find:
            _work_fname = ''
            if '' == name:
                _work_fname = _find[0]
            else:
                for _fn in _find:
                    _mn = self._get_mode_name(_fn)
                    if _mn == name:
                        _work_fname = _fn
                        break
            _file = os.path.join(_dir, _work_fname)
        if not os.path.isfile(_file):
            _file = ''
        return _file

    def __get_files(self):
        """
        Метод возвращает файлы всех режимов
        :return:
        """
        _dir = self.__get_work_dir()
        _files = os.scandir(_dir)
        _find = []
        for _fi in _files:
            if _fi.name.startswith('.') or _fi.is_dir():
                continue
            _name = _fi.name
            #  теперь надо проверить на начало и конец имени режима
            if not self.__is_mode_file(_name):
                continue
            _find.append(_name)
        return _find

    def __get_work_dir(self):
        _pth = os.path.dirname(self._class_file)
        _pth = os.path.join(_pth, 'data')
        if not os.path.exists(_pth):
            try: os.mkdir(_pth)
            except: pass
        return _pth

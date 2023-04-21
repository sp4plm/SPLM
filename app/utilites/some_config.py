from os import scandir as oscandir, path as opath
from app.utilites.conf_driver_ini import ConfigDriverIni


class SomeConfig:
    _class_file = __file__
    _key_splitter = '.'
    _configs_root = opath.dirname(opath.dirname(_class_file))

    def __init__(self, configs_root=''):
        self.set_root(configs_root)
        self._catched_vals = {}
        self._last_requested_key = ''

    def get(self, key):
        """ key - string with dot delimetr aka Key1.kEy2.3key """
        self._last_requested_key = key
        if key in self._catched_vals:
            return self._catched_vals[key]
        _parsed_key = self._parse_key(key)
        # теперь требуется бежать по ключу и найти файл в котором есть значение
        folder = self._configs_root
        for step in _parsed_key:
            catch_file = ''
            catch_dir = ''
            try_dir = opath.join(folder, step)
            # если нашли директорию
            if opath.exists(try_dir):
                catch_dir = try_dir
            # сперва ищем файл в директории
            files = oscandir(folder)
            for fI in files:
                if not fI.is_file():
                    continue
                splited = fI.name.split('.')
                if step == splited[0] and 2== len(splited):
                    # нашли файл - значит пытаемся получить значение по нему
                    catch_file = opath.join(folder, fI.name)
                    break
            if '' != catch_file:
                try:
                    # print('SomeConfig.get->catch_file:', catch_file)
                    catch_file = self.__get_real_filepath(catch_file)
                    # print('SomeConfig.get->catch_file real:', catch_file)
                    file_driver = self._get_file_driver(splited[1])
                    file_driver.set_file(catch_file)
                    last_steps = _parsed_key[_parsed_key.index(step)+1:]

                    if not last_steps:
                        # dump full file content
                        if 0== _parsed_key.index(step) and step == opath.basename(catch_file).split('.')[0]:
                            #  мы спросили только файл
                            val = file_driver.to_dict()
                            if val is not None:
                                self._catched_vals[key] = val
                            pass
                        break # когда оказывается последнее значение ключа - имя файла
                    val = file_driver.get(last_steps)
                    if val is not None:
                        self._catched_vals[key] = val
                except:
                    # написать в лог для какого типа файла нет драйвера конфига
                    file_driver = None
                    catch_file = ''
                    print('Undefined setting key "{}"'.format(key))
                    # теперь пробросить исключение что такого ключа нет в хранилище
                    raise Exception('Undefined setting key "{}"'.format(key))
            # теперь можно изменить директорию для поиска
            if '' != catch_dir:
                folder = catch_dir
        # теперь кода все обработано отберем только правильное значение
        result = None
        result = self._detect_result()
        return result

    def _detect_result(self):
        res = None
        res = self._catched_vals[self._last_requested_key]
        del self._catched_vals[self._last_requested_key]
        # print(res)
        return res

    @staticmethod
    def _get_file_driver(file_ext):
        if 'ini' == file_ext:
            return ConfigDriverIni()
        raise Exception('No config file driver for {} file type!'.format(file_ext))

    def _parse_key(self, key):
        parsed = key.split(self._key_splitter)
        return parsed

    def set_root(self, file_name):
        if opath.exists(file_name) and opath.isdir(file_name):
            self._configs_root = file_name

    def __get_real_filepath(self, req_file):
        _root_pth = self.__get_app_path()
        # рассматриваем файлы внутри приложения
        if req_file.startswith(_root_pth):
            _app_conf_pth = _root_pth + opath.sep + 'cfg'
            # если запрошенный файл находится вне конфигурационной директории приложения
            if not req_file.startswith(_app_conf_pth):
                # определяем в какой поддиректории приложения ищется файл
                relative = req_file.replace(_root_pth, '')
                # считаем что данная директория модуль
                _mod_name = relative.lstrip(opath.sep).split(opath.sep)[0]
                # _mod_name = _mod_name.lstrip(opath.sep)
                # если конфигурационная директория существует
                if opath.exists(_app_conf_pth):
                    _t = opath.join(_app_conf_pth, _mod_name)
                    # если существует директория модуля в конфигурационной директории
                    if opath.exists(_t):
                        _t = opath.join(_app_conf_pth, relative.lstrip(opath.sep))
                        # существует ли указанный конфигурационный файл
                        if opath.exists(_t):
                            req_file = _t
        return req_file

    def __get_app_path(self):
        """
        Метод вычисляет путь директории приложения - это отсчетная точка для модулей
        :return: None
        """
        _pth_utils = opath.dirname(self._class_file)
        return opath.dirname(_pth_utils)

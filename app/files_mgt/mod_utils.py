from app import app_api

from .mod_conf import ModConf

class ModUtils(ModConf):
    _class_file = __file__
    _debug_name = 'ModUtils'

    def get_jslib_jqGrid_vers(self):
        return '4.13.2'

    def get_jslib_jquery_vers(self):
        return '1.9.13'

    def get_jslib_jstree_vers(self):
        return '3.3.12'

    def get_allowed_files(self):
        """
        Функция возвращает список разширений файлов
        :return: list: список разширений
        """
        return self._ALLOWED_EXTENSIONS

    def get_max_filesize(self):
        """
        Метод возвращает максимальный допустимый размер файла
        :return: int: максимальный размер файла
        """
        return self._MAX_FILE_SIZE

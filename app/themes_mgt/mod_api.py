# -*- coding: utf-8 -*-


class ModApi():
    _class_file = __file__
    _debug_name = 'ThemesMgtApi'

    def __init__(self):
        self.__mod_utils = self.__get_mod_utils()

    @staticmethod
    def __get_mod_utils():
        from .mod_utils import ModUtils
        return ModUtils()

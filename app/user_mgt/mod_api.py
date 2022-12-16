# -*- coding: utf-8 -*-
from app.user_mgt.models.roles import Role

class ModApi:
    _class_file = __file__
    _debug_name = 'UsersModApi'

    @staticmethod
    def get_roles():
        """
        Функция возвращает роли .....

        :returm: список
        :rtype: list
        """
        lst = []
        _data = Role.query.all()
        if _data:
            lst = [r.name for r in _data]
        return lst

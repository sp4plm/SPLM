# -*- coding: utf-8 -*-
from app.user_mgt.models.roles import Role
try:
    from flask_login import LoginManager, current_user, login_required
except Exception as ex:
    def login_required(func):
        return True
    current_user = {}


def login_required(func):
    """
    Функция должна заменить декоратор login_required из flask_login
    чтобы сделать его программно отключаемым для определенных url проекта
    :return:
    """

class ModApi:
    _class_file = __file__
    _debug_name = 'UsersModApi'

    @staticmethod
    def get_roles():
        """"""
        lst = []
        _data = Role.query.all()
        if _data:
            lst = [r.name for r in _data]
        return lst

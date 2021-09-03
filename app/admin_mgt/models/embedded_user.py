# -*- coding: utf-8 -*-
from werkzeug.security import check_password_hash
from app import app


class EmbeddedUser:
    _class_file = __file__
    _debug_name = 'EmbeddedUser'
    id = -1
    name = 'System Administrator'
    login = ''
    password = ''
    _roles = []

    def __init__(self):
        self.login = app.config['PORTAL_MAN_USER']
        self.password = app.config['PORTAL_MAN_SECRET']

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.id

    @property
    def roles(self):
        # для супер админа надо выбрать все роли
        return self._roles

    @roles.setter
    def roles(self, value):
        self._roles = value

    def has_role(self, *args):
        return True

    # Required for administrative interface
    def __unicode__(self):
        return self.login

    # Flask - Login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @staticmethod
    def is_local_admin(user_name):
        # read app settings about local admin name
        flag = False
        if user_name == app.config['PORTAL_MAN_USER']:
            flag = True
        return flag

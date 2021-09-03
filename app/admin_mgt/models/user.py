# -*- coding: utf-8 -*-
from app import app_api
from werkzeug.security import check_password_hash
from app import app
from flask_login import UserMixin
from app.admin_mgt.models.embedded_user import EmbeddedUser
try:
    from app import db, login_manager
except ImportError as ex:
    # все сломалось надо остановить проект
    raise ex


# нужно для загрузки пользователя в сессию
@login_manager.user_loader
def load_user(id):
    if -1 == id:
        return EmbeddedUser()
    else:
        if app_api.is_app_module_enabled('user_mgt'):
            from app.user_mgt.models.users import User
            return User.query.get(int(id))


class User(UserMixin):
    _class_file = __file__
    _debug_name = 'AdminMgtUser'
    id = 0
    name = 'Anonymous user'
    login = 'anonymous'
    password = 'zsdrsdmam433745v35v34'
    _roles = []

    def __init__(self, id):
        #self.id = int(id) + 1000000
        self.id = int(id) - int(id)

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
        self._roles = []

    def has_role(self, *args):
        return False

    # Required for administrative interface
    def __unicode__(self):
        return self.login

    # Flask - Login
    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return True

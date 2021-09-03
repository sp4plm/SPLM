# -*- coding: utf-8 -*-
from flask_sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from app import app_api
from app import app, db

admin_api = app_api.get_mod_api('admin_mgt')
NodeObject = admin_api.get_base_model()
ManUser = admin_api.get_embedded_user()

'''
Поля таблицы с проекта на php из настроечного файла
id[type] = INTEGER
id[] = primary key
id[] = autoincrement
name[type] = TEXT
login[type] = TEXT
password[type] = INTEGER
email[type] = TEXT
roles[type] = 'NONE'
last_ip[type] = TEXT
authkey[type] = TEXT
lastlogin[type] = TEXT
org[type]= TEXT
'''


class User(UserMixin, NodeObject):
    __tablename__ = 'users'

    id = db.Column(db.Integer, nullable=False, unique=True,
                   primary_key=True, autoincrement=True)

    name = db.Column(db.Unicode, index=True, unique=True)
    login = db.Column(db.String(80), index=True, unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128))
    _roles = db.Column('roles', db.String(1), nullable=True)
    last_ip = db.Column(db.String(40))
    authkey = db.Column(db.String(128))
    lastlogin = db.Column(db.String(20))
    _org = db.Column('org', db.String(1), nullable=True)

    _log_name = 'users'
    _links = {'roles': 'roles', 'org': 'orgs'}
    _links_data = {'roles': [], 'org': []}

    def to_dict(self):
        view = {}
        view['id'] = int(self.id)
        view['name'] = self.name
        view['login'] = self.login
        view['email'] = self.email
        view['roles'] = []
        view['last_ip'] = self.last_ip
        view['lastlogin'] = self.lastlogin
        view['org'] = []
        if hasattr(self, 'links_data'):
            view['link_fields'] = self.links_data
        return view

    def init_links(self):
        # if not hasattr(self, '_roles'):
        #    self._roles = []
        if not hasattr(self, '_links'):
            self._links = {'roles': 'roles', 'org': 'orgs'}
        if not hasattr(self, 'links_data'):
            self._links_data = {'roles': [], 'org': []}

    @property
    def roles(self):
        # print('User.roles.getter say: Start')
        if self._roles is None:
            self._roles = []
        # self.init_links()
        linked = []
        if hasattr(self, '_links_data'):
            linked =  self._links_data['roles']
            self._roles =  self._links_data['roles']
        # linked = self._roles
        # print('User.roles.getter say: End')
        return linked

    @roles.setter
    def roles(self, value):
        # print('User.roles.setter say: Start')
        self._roles = value
        self._links_data['roles'] = value
        # проверить все ли узлы для ссылок существуют
        # exists_nodes = []
        # check_count = len(self._roles)
        # exists_nodes = self.get_linked_nodes(self._roles)
        # all_exists = (check_count == len(exists_nodes))
        # сохраняем те узыл которые существуют
        self._roles = None
        # print('User.roles.setter say: End')

    @hybrid_property
    def org(self):
        return self._org;

    @org.setter
    def org(self, value):
        self._org = value

    @staticmethod
    def auth(self, login, secret):
        flg = False
        return flg

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

    def has_role(self, *args):
        return set(args).issubset({role.name for role in self.roles})

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def is_local_admin(user_name):
        # read app settings about local admin name
        flag = False
        if user_name == app.config['PORTAL_MAN_USER']:
            flag = True
        return flag

    @staticmethod
    def auth_admin(user_name, secret):
        flag = check_password_hash(app.config['PORTAL_MAN_SECRET'], secret)
        user = None
        if flag:
            user = ManUser()
        return user

    def __repr__(self):
        return '<User %r>' % (self.login)


# """
@event.listens_for(User, 'before_insert')
def before_add_user(mapper, connection, node):
    d = 0
    # print('Before User insert trigger')
    node._roles = '0'
    # print('END Before User insert trigger')
# """


# """
@event.listens_for(User, 'after_insert')
def after_add_user(mapper, connection, node):
    q=2
    # print('After User insert trigger')
    # теперь надо вставить ссылки на узлы Link !!!!
    node.sync_node_links()
    node._roles = node._links_data['roles']
    # теперь попытаемся сделать commit внутри commit
    # print('END After User insert trigger')
# """


# """
@event.listens_for(User, 'before_update')
def before_update_user(mapper, connection, node):
    d = 0
    node._roles = '1'
    # print('Before User update trigger')
    # print('END Before User update trigger')
# """


@event.listens_for(User, 'after_update')
def after_update_user(mapper, connection, node):
    # print('After User update trigger')
    # теперь надо вставить ссылки на узлы Link !!!!
    node.sync_node_links()
    node._roles = node._links_data['roles']
    # print('END After User update trigger')

# """
@event.listens_for(User, 'load')
def load_user(target, context):
    a=1
    # print('Load trigger')
    target.init_links()
    # теперь надо вставить все ссылки по полям
    target.fill_links_fields()
    # print('END Load trigger')
# """

"""
@event.listens_for(User, 'init')
def init_user(target, args, kwargs):
    d = 0
    # target.init_links()
    # теперь надо вставить все ссылки по полям
    # target.fill_links_fields()
# """

"""
@event.listens_for(User, 'before_delete')
def before_delete_user(mapper, connection, target):
    # "listen for the 'before_delete' event"
    print('Before User delete trigger')
    print('END Before User delete trigger')
# """

# standard decorator style
@event.listens_for(User, 'after_delete')
def after_delete_user(mapper, connection, target):
    # "listen for the 'after_delete' event"
    # print('After User delete trigger')
    target.drop_links()
    # print('END After User delete trigger')

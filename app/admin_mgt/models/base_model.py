# -*- coding: utf-8 -*-
import os
import datetime

from app import db
from app.admin_mgt.models.log_component import LogComponent


class AppBaseModel(db.Model):
    __abstract__ = True
    __dblink__ = db
    __debug_log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs', 'models_debug.log')

    id = db.Column(db.Integer, nullable=False, unique=True,
                   primary_key=True, autoincrement=True)

    _logger = None
    _log_name = ''
    _log_file_name = 'all_models'

    def to_log(self, message):
        # """
        if not hasattr(self, '_logger'):
            self._logger = None
        if not hasattr(self, '_log_name'):
            self._log_name = ''
        if self._logger is None:
            log_file_name = os.path.dirname(os.path.dirname(__file__)) + '/data/{}.log'.format(self.get_log_filename())
            self._logger = LogComponent.get_app_logger(self._log_name,
                                                       log_file_name)
        self._logger.info(message)
        # """

    def to_log2(self, message):
        self.init_self_log()
        cur_time = '[{}]' . format(datetime.datetime.now())
        new_line = "\n"
        line = '{} {} '.format(cur_time, message) + new_line
        with open(self.__debug_log_file, 'a') as the_file:
            the_file.write(line)

    def drop_self_log(self, purge=False):
        if self.exists_log():
            os.system(r' >{}'.format(self.__debug_log_file))
            if purge:
                os.remove(self.__debug_log_file)

    def create_log_file(self):
        if not os.path.exists(self.__debug_log_file):
            with open(self.__debug_log_file, 'w') as fm:
                fm.write('')

    def init_self_log(self):
        if not self.exists_log():
            self.create_log_file()

    def exists_log(self):
        return os.path.exists(self.__debug_log_file)

    def get_records_source(self):
        return self.__tablename__

    def get_log_filename(self):
        return self._log_file_name

    def to_dict(self):
        view = {}
        view['id'] = int(self.id)
        return view

    @staticmethod
    def _get_class_by_table(tablename):
        # нужна проверка на стороние модули !!!
        if 'users' == tablename:
            from app.user_mgt.models.users import User
            return User
        if 'roles' == tablename:
            from app.user_mgt.models.roles import Role
            return Role
        if 'l' == tablename:
            from app.admin_mgt.models.links import Link
            return Link
        return None

    @staticmethod
    def str_to_node(str_node):
        t = str_node.split('-')
        cls = AppBaseModel._get_class_by_table(t[0])
        if cls is not None:
            node = cls.query.get(t[1])
            return node
        # если не смогли определить класс
        return str_node

    @staticmethod
    def node_to_str(node):
        table = node.get_record_source()
        nid = node.id
        return table + '-' + nid

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r})>".format(self)

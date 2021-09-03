# -*- coding: utf-8 -*-
from sqlalchemy import event
from app import db
from app import app_api

admin_api = app_api.get_mod_api('admin_mgt')
NodeObject = admin_api.get_base_model()

'''
Поля таблицы с проекта на php из настроечного файла
id[type] = INTEGER
id[] = primary key
id[] = autoincrement
name[type] = TEXT
code[type] = TEXT
descr[type] = TEXT
'''


class Role(NodeObject):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, nullable=False, unique=True,
                   primary_key=True, autoincrement=True)

    name = db.Column(db.String(30), nullable=False)
    code = db.Column(db.String(30), nullable=False)
    descr = db.Column(db.Text, nullable=False)

    _links = {}
    _log_name = 'roles'

    def can_delete_me(self):
        related = self.get_nodes_related_to_me()
        flg = True
        if 0 < len(related):
            flg = False
        return flg

    def to_dict(self):
        view = {}
        view['id'] = int(self.id)
        view['name'] = self.name
        view['code'] = self.code
        view['descr'] = self.descr
        return view

    def __repr__(self):
        return '<Role %r>' % (self.name)


@event.listens_for(Role, 'before_delete')
def before_delete_role(mapper, connection, target):
    # "listen for the 'before_delete' event"
    # print('Before Role delete trigger')
    # требуется проверить ссылаются ли на данную роль
    # если есть хоть одна ссылка нужно вызвать ошибку
    if not target.can_delete_me():
        raise Exception('Сперва требуется удалить ссылки на эту роль "{}"' . format(target.name))
    # print('END Before Role delete trigger')

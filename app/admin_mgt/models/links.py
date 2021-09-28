# -*- coding: utf-8 -*-
from sqlalchemy import event
from app import db
from app.admin_mgt.models.base_model import AppBaseModel

'''
Поля таблицы с проекта на php из настроечного файла
id[type] = INTEGER
id[] = primary key
id[] = autoincrement
ts[type] = TEXT
fs[type] = TEXT
rs[type] = INTEGER
tl[type] = TEXT
fl[type] = TEXT
rl[type] = INTEGER
tag[type]= TEXT
'''

class Link(AppBaseModel):
    __tablename__ = 'l'

    id = db.Column(db.Integer, nullable=False, unique=True,
                   primary_key=True, autoincrement=True)

    ts = db.Column(db.String(20), nullable=False)
    fs = db.Column(db.String(20), nullable=False)
    rs = db.Column(db.Integer, nullable=False)
    tl = db.Column(db.String(20), nullable=False)
    fl = db.Column(db.String(20), nullable=False)
    rl = db.Column(db.Integer, nullable=False)
    tag = db.Column(db.String(80), nullable=False)

    @staticmethod
    def is_node_link(node, link):
        flg = False
        str_link = '{}-{}'.format(link['tl'], link['rl'])
        str_node = '{}-{}'.format(node.get_records_source(), node.id)
        if str_link == str_node:
            flg = True
        return flg

    @staticmethod
    def get_node_links(node, field=None):
        links = None
        filter = {}
        filter['ts'] = node.get_records_source()
        filter['rs'] = int(node.id)
        has_field = False
        if field is not None and type('z') == type(field) \
                and '' != field:
            filter['fs'] = str(field)
            has_field = True
        links_temp = Link.query.filter_by(**filter).all()
        # print('Link.get_node_links say: temp links {}'.format(str(links_temp)))
        if 0 < len(links_temp):
            if has_field:
                links = []
            else:
                links = {}
            for link in links_temp:
                if not has_field:
                    if link['fs'] not in links:
                        links[link['fs']] = []
                    links[link['fs']].append(link)
                else:
                    links.append(link)
        else:
            links = [] # возвращаем
        return links

    @staticmethod
    def resolve_links_by_node(node):
        filter = {}
        filter['ts'] = node.get_records_source()
        filter['rs'] = int(node.id)
        links = Link.query.filter_by(**filter).all()
        l = []
        for link in links:
            l.append(link.to_dict())
        links = None
        filter = None
        # print('Link.resolve_links_by_node say: ', str(l))
        return Link.resolve_links(l)

    @staticmethod
    def resolve_links(links):
        # struct [field][nodes_list]
        nodes = {}
        if 0 < len(links):
            a=0
            # работаем только с записями таблицы ссылок
            # следовательно каждый элемент списка должен
            # быть словарем с полями как в таблице
            # {'ts': 'source_table', 'fs': 'source_field', 'rs': source_id,
            #  'tl': 'target_table','fl': 'target_field','rl': 'target',
            #   'tag': 'some_description'}
            # группируем по таблица для запросов
            by_tables = {}
            for link in links:
                if link['tl'] not in by_tables:
                    by_tables[link['tl']] = []
                by_tables[link['tl']].append(int(link['rl']))
                # делаем заготовку для вставки
                if link['fs'] not in nodes:
                    nodes[link['fs']] = []
            by_tables_nodes = {}
            if 0 < len(by_tables.keys()):
                for table in by_tables:
                    cls = AppBaseModel._get_class_by_table(table)
                    by_tables_nodes[table] = cls.query.filter(cls.id.in_(by_tables[table])).all()
                # print('resolve_links.by_tables.keys()', by_tables.keys())
            indexed_nodes = {}
            if 0 < len(by_tables_nodes.keys()):
                for table in by_tables_nodes:
                    for node in by_tables_nodes[table]:
                        key = table + '-' + str(node.id)
                        indexed_nodes[key] = node
                # print('resolve_links.by_tables_nodes.keys()', by_tables_nodes.keys())
            for link in links:
                key = link['tl'] + '-' + str(link['rl'])
                if link['fs'] not in nodes:
                    nodes[link['fs']] = []
                if key in indexed_nodes:
                    nodes[link['fs']].append(indexed_nodes[key])
        return nodes

    def resolve_link(self):
        return self.get_linked()

    def get_source(self):
        cls = self._get_class_by_table(self.ts)
        # node = cls({'id': int(self.rs)})
        node = cls.query.get(int(self.rs))
        return node.to_dict()

    @staticmethod
    def to_source(node, field):
        link = {}
        link['ts'] = str(node.get_records_source())
        link['fs'] = str(field)
        link['rs'] = int(node.id)
        return link

    def get_linked(self):
        cls = self._get_class_by_table(self.tl)
        node = cls({'id': int(self.rl)})
        return node.to_dict()

    @staticmethod
    def to_linked(node, field='id'):
        link = {}
        link['tl'] = str(node.get_records_source())
        link['fl'] = str(field)
        link['rl'] = int(node.id)
        return link

    def to_dict(self):
        view = {}
        view['id'] = int(self.id)
        view['ts'] = self.ts
        view['fs'] = self.fs
        view['rs'] = int(self.rs)
        view['tl'] = self.tl
        view['fl'] = self.fl
        view['rl'] = int(self.rl)
        view['tag'] = self.tag
        return view

@event.listens_for(Link, 'before_insert')
def before_add_link(mapper, connection, node):
    # print('Before Link insert trigger')
    node.tag = ''
    # print(mapper)
    # print(connection)
    # node.to_log(str(node.to_dict()))
    # print(node)
    # print('END Before Link insert trigger')

"""
@event.listens_for(Link, 'after_insert')
def after_add_link(mapper, connection, node):
    # print('After Link insert trigger')
    # print(mapper)
    # print(connection)
    # node.to_log(str(node.to_dict()))
    # print(node)
    # print('END After Link insert trigger')
# """


"""
@event.listens_for(Link, 'before_remove')
def before_remove_link(mapper, connection, node):
    print('Before Link remove trigger')
    # print(mapper)
    # print(connection)
    # node.to_log(str(node.to_dict()))
    # print(node)
    print('END Before Link insert trigger')


@event.listens_for(Link, 'after_remove')
def after_remove_link(mapper, connection, node):
    print('After Link remove trigger')
    # print(mapper)
    # print(connection)
    # node.to_log(str(node.to_dict()))
    # print(node)
    print('END After Link insert trigger')
# """

# """
@event.listens_for(Link, 'init')
def init_link(target, args, kwargs):
    d = 0
    # print('Init Link trigger')
    target.tag = ''
    # print('END Init Link trigger')
# """

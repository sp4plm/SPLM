# -*- coding: utf-8 -*-
from sqlalchemy import event

from app.admin_mgt.models.base_model import AppBaseModel
from app.admin_mgt.models.links import Link


class NodeObject(AppBaseModel):
    # объявляются переменные класса - одинаковые для всех экземпляров
    __abstract__ = True
    _links={}

    def sync_node_links(self):
        if hasattr(self, '_links') and hasattr(self, '_links_data'):

            def gen_node_key(node):
                return '{}-{}'.format(node.get_records_source(), node.id)

            def gen_linked_key(link):
                return '{}-{}'.format(link.tl, link.rl)
                # return '{}-{}'.format(link['tl'], link['rl'])

            # print('NodeObject.sync_node_links say: local links {}' . format(str(self._links_data)))
            # теперь уикл по _links_data для каждого поля производим синхронизацию
            for field in self._links_data:
                # print('NodeObject.sync_node_links say: proccess field {}' . format(field))
                self_link = Link.to_source(self, field)
                # выбираем ссылки для данного поля
                exists_field_links = []
                exists_field_links = Link.get_node_links(self, field)
                # print('NodeObject.sync_node_links say: exists links {}' . format(str(exists_field_links)))
                exists_field_links = self.list_to_dict(exists_field_links, gen_linked_key)
                # print('NodeObject.sync_node_links say: exists2 links {}' . format(str(exists_field_links)))
                checked_links = self.list_to_dict(self._links_data[field], gen_node_key)
                # print('NodeObject.sync_node_links say: checked links {}' . format(str(checked_links)))

                # находим пересечение это то что надо оставить как есть - удалить из всех списков
                no_acts_links = list(set(exists_field_links.keys()) & set(checked_links.keys()))
                # print('NodeObject.sync_node_links say: no acts links {}' . format(str(no_acts_links)))
                # остаток в checked_links - надо вставить
                # new_links = []
                for key in checked_links:
                    if key in no_acts_links:
                        continue
                    # надо превратить в новую ссылку
                    new_link = Link.to_linked(checked_links[key])
                    new_link.update(self_link)
                    # new_links.append(new_link)
                    link = Link(**new_link)
                    try:
                        self.__dblink__.session.add(link)
                        # print('add new link: {}' .format(str(link.to_dict())))
                    except:
                        msg = 'NodeObject.sync_node_links say: can not add new link - {}'.format(str(new_link))
                        self.to_log(msg)
                # остаток в exists_field_links - надо удалить
                # remove_links = []
                for key in exists_field_links:
                    if key in no_acts_links:
                        continue
                    # remove_links.append(exists_field_links[key])
                    try:
                        self.__dblink__.session.delete(exists_field_links[key])
                        # print('set remove link: {}' .format(str(exists_field_links[key].to_dict())))
                    except:
                        msg = 'NodeObject.sync_node_links say:'
                        msg += ' can not remove link - {}'.format(str(exists_field_links[key].to_dict()))
                        self.to_log(msg)
        else:
            msg = 'NodeObject.sync_node_links say:'
            msg += ' No _links and _links_data attributes on node {}' . format(self.to_dict())
            self.to_log(msg)

    def drop_links(self):
        if hasattr(self, '_links') and hasattr(self, '_links_data'):
            for field in self._links_data:
                # print('NodeObject.sync_node_links say: proccess field {}' . format(field))
                self_link = Link.to_source(self, field)
                # выбираем ссылки для данного поля
                exists_field_links = []
                exists_field_links = Link.get_node_links(self, field)
                for link in exists_field_links:
                    try:
                        self.__dblink__.session.delete(link)
                        # print('set remove link: {}' .format(str(link.to_dict())))
                    except:
                        msg = 'NodeObject.sync_node_links say:'
                        msg += ' can not remove link - {}'.format(str(link.to_dict()))
                        self.to_log(msg)

    def sync_field_links(self, field, linked=None):
        # метод требуется вызывать из триггера после вставки записи Пользователя в таблицу
        s=0
        if hasattr(self, '_links'):
            if field in self._links and field in self._links_data:
                e=2
        else:
            self.to_log('NodeObject.sync_field_links say: No _links attribute on node {}' . format(self.to_dict()))

    def fill_links_fields(self):
        if hasattr(self, '_links') and hasattr(self, '_links_data'):
            # print('NodeObject.fill_links_fields say:', self)
            nodes = Link.resolve_links_by_node(self)
            # print('NodeObject.fill_links_fields say:', str(nodes))
            for field in self._links:
                if field in nodes:
                    # setattr(self, field, nodes[field])
                    self._links_data[field] = nodes[field]

    def get_nodes_related_to_me(self):
        # надо составить условие поиска ссылкой
        linked = Link.to_linked(self)
        related = Link.query.filter_by(**linked).all()
        if 0 < len(related):
            _t = {}
            try:
                for rel_node in related:
                    if rel_node.ts not in _t:
                        _t[rel_node.ts] = []
                    _t[rel_node.ts].append(rel_node.get_source())
                    # print('get_nodes_related_to_me, self.dict ', rel_node.to_dict())
                    # print('get_nodes_related_to_me link source ', rel_node.get_source())
                related = _t
            except Exception as ex:
                print('get_nodes_related_to_me.Ex', ex)
            # related = [rel_node.get_source() for rel_node in related]
            # related = Link.resolve_links(related)
        return related

    def updateme(self, data):
        if 0 < len(data):
            # проверить - требуется идентификатор объекта
            if 1 > self.id and \
                    ('id' not in data or 1 > data['id']):
                return
            for key in data:
                if hasattr(self, key):
                    setattr(self, key, data[key])

    def addme(self, data):
        if 0 < len(data):
            for key in data:
                if hasattr(self, key):
                    setattr(self, key, data[key])
        try:
            self.__dblink__.session.add(self)
        except:
            self.to_log('Can not add node with data: {}' . format(str(data)))

    def deleteme(self):
        try:
            self.__dblink__.session.delete(self)
        except:
            self.to_log('Can not remove node: {}' . format(str(self.to_dict())))

    @staticmethod
    def get_linked_nodes(nodes):
        by_tables_nodes = {}
        by_tables = NodeObject.group_nodes_by_table(nodes)
        # print('NodeObject.get_linked_nodes say: by_tables', by_tables)
        if 0 < len(by_tables.keys()):
            for table in by_tables:
                # print('NodeObject.get_linked_nodes say: operate table ->', table)
                cls = AppBaseModel._get_class_by_table(table)
                # print('NodeObject.get_linked_nodes say: select cls ->', cls)
                ids = [int(node.id) for node in by_tables[table]]
                # print('NodeObject.get_linked_nodes say: select ids ->', ids)
                # print('NodeObject.get_linked_nodes say: select condition ->', cls.id.in_(ids))
                try:
                    # print('NodeObject.get_linked_nodes say: exec query ->', cls.query.filter(cls.id.in_(ids)).statement)
                    query_result = cls.query.filter(cls.id.in_(ids)).all()
                    # print('NodeObject.get_linked_nodes say: exec query done !', query_result)
                    by_tables_nodes[table] = query_result
                except Exception as ex:
                    print('NodeObject.get_linked_nodes say: query error ->', str(ex))
                # print('NodeObject.get_linked_nodes say: select ids nodes ->', by_tables_nodes[table])
        result = []
        for table in by_tables_nodes:
            result += by_tables_nodes[table]
        # print('NodeObject.get_linked_nodes say: result', result)
        return result

    @staticmethod
    def group_nodes_by_table(nodes):
        by_tables = {}
        for node in nodes:
            table = node.get_records_source()
            if table not in by_tables:
                by_tables[table] = []
            by_tables[table].append(node)
        return by_tables

    @staticmethod
    def list_to_dict(items, key_func):
        temp = {}
        for item in items:
            key = key_func(item)
            temp[key] = item
        return temp

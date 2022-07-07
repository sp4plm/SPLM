# -*- coding: utf-8 -*-
'''
Created on 4 sept. 2021 г.
@author: oleg st
'''
import numpy as np
import pandas as pd
from urllib.parse import quote
from app.app_api import tsc_query
from app import app_api
onto_mod_api = app_api.get_mod_api('onto_mgt')

def make_breadcrumbs(prefix, pref_unquote, cls):

    bc = []
    while cls != 'Thing':
        if cls == '': # в онтологии могут быть несколько родительских классов и возможно не выполнение первого условия
            break

        query_paretn_lbl = tsc_query('mod_data_navigation.Thing.class_lbl',
                                    {'URI': "<" + pref_unquote + cls + ">"})
        df_prnt = pd.DataFrame(query_paretn_lbl)

        if len(df_prnt):
            cls_lbl = df_prnt.cls_lbl[0]
        else:
            cls_lbl = cls

        bc.insert(0, {'href': cls + '?' + 'prefix=' + prefix, 'label' : cls_lbl})
        cls = onto_mod_api.get_parent(prefix, cls)

    return bc

class Thing:
    def __init__(self, argm):
        prefixes = onto_mod_api.get_prefixes()
        self.argm = argm
        if self.argm['class'] == 'Thing':
            self.parent = ''
            q = tsc_query('mod_data_navigation.Thing.list_of_subclasses',{'URI':"owl:Thing"})
            if q:
                self.pref_unquote = q[0]['cls'].split("#")[0] + "#"
                self.pref_4_data = ''
                for p in prefixes:
                    if p[1] == self.pref_unquote:
                        self.argm['prefix'] = p[0]
            else:
                self.pref_unquote = ''
                self.pref_4_data = ''
        else:
            self.parent = onto_mod_api.get_parent(argm['prefix'], argm['class'])
            for p in prefixes:
                if p[0] == argm['prefix']:
                    self.pref_unquote = p[1]

            query = tsc_query('mod_data_navigation.Thing.one_instances',
                              {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
            if query:
                self.pref_4_data = query[0]['inst'].split("#")[0] + "#"
            else:
                self.pref_4_data = ''


    def getTemplate(self):
        '''
        Возвращает шаблон HTML страницы, сформированный в соответствии с полученными в URL аргументами
        '''

        pref = self.argm['prefix']
        parent = self.parent
        subclasses = ''
        instances = ''

        query_class_lbl = tsc_query('mod_data_navigation.Thing.class_lbl',
                     {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
        df_cls = pd.DataFrame(query_class_lbl)

        if len(df_cls):
            class_lbl = df_cls.cls_lbl[0]
        else:
            class_lbl = self.argm['class']

        query_paretn_lbl = tsc_query('mod_data_navigation.Thing.class_lbl',
                                    {'URI': "<" + self.pref_unquote + self.parent + ">"})
        df_prnt = pd.DataFrame(query_paretn_lbl)

        if len(df_prnt):
            parent_lbl = df_prnt.cls_lbl[0]
        else:
            parent_lbl = self.parent

        # Если есть аргумент URI, то значит показываем страничку "Экземпляра класса"
        if 'uri' in self.argm.keys():
            query_inst = tsc_query('mod_data_navigation.Thing.instance',
                                   {'PREF': self.pref_unquote, 'URI': self.argm['uri']})

            df = pd.DataFrame(query_inst)

            if len(df) > 0:
                df.columns = ['Наименование','Атрибут', 'Значение']
                templ = app_api.render_page("data_navigation/Thing_inst.html", title="TEST",
                                class_name='<a href="{}?prefix={}">{}</a>'.format(self.argm['class'], self.argm['prefix'], class_lbl),
                                instance=df.to_html(escape=False, index=False),
                                argm=self.argm.items())

            else:
                templ = app_api.render_page("data_navigation/Thing_inst.html", title="TEST",
                                class_name='<a href="{}?prefix={}">{}</a>'.format(self.argm['class'], self.argm['prefix'], class_lbl),
                                instance="No data about this instance.",
                                argm=self.argm.items())

        # В остальных случаях показываем страничку со "Списком экземпляров класса и его подклассами"
        else:
            # меняем префик в запросе для лксса Thing
            if self.argm['class'] == 'Thing':
                pref4req = 'http://www.w3.org/2002/07/owl#'
            else:
                pref4req = self.pref_unquote

            # -------------- SUBCLASS --------------
            query_subclass = tsc_query('mod_data_navigation.Thing.list_of_subclasses',
                                       {'URI': "<" + pref4req + self.argm['class'] + ">"})
            df = pd.DataFrame(query_subclass)
            if len(df) > 0:
                df.cls = '<a href="/datanav/' + df.cls.str.replace(self.pref_unquote,'') + \
                         '?prefix=' + self.argm['prefix'] + '">' + df.cls_lbl + '</a>'
                df.drop('cls_lbl', axis=1, inplace=True)
                df.columns = ['Наименование']

            # -------------- INST--------------
            query_list_inst = tsc_query('mod_data_navigation.Thing.list_of_instances',
                                        {'URI': "<" + pref4req + self.argm['class'] + ">"})
            df2 = pd.DataFrame(query_list_inst)

            if len(df2) > 0:
                df2.inst_lbl.replace('', np.nan, inplace=True)
                df2.inst_lbl.fillna(value=df2.inst.str.replace(self.pref_unquote, ''), inplace=True)

                if self.argm['class'] == 'Thing':
                    df2.inst = df2.inst_lbl
                else:
                    df2.inst = '<a href="/datanav/' + self.argm['class']  + '?prefix=' + self.argm['prefix'] + '&uri=' + \
                           df2.inst.str.replace(self.pref_4_data, quote(self.pref_4_data)) + '">' + df2.inst_lbl + '</a>'

                df2.drop('inst_lbl', axis=1, inplace=True)
                df2.columns = ['Наименование']

            if self.parent == 'Thing':
                pref = 'owl'

            if self.parent:
                parent = '<a href="/datanav/{}?prefix={}">{}</a>'.format(self.parent,pref, parent_lbl)

            if len(df) > 0:
                subclasses = df.to_html(escape=False, index=False)

            if len(df2) > 0:
                instances = df2.to_html(escape=False, index=False)

            page_path = make_breadcrumbs(self.argm['prefix'], self.pref_unquote, self.argm['class'])
            templ = app_api.render_page("data_navigation/Thing.html", title="",
                                    class_name=class_lbl,
                                    parent=parent,
                                    subclasses=subclasses,
                                    instances = instances,
                                    argm=self.argm.items(),
                                    page_path=page_path)

        return templ
# -*- coding: utf-8 -*-
'''
Created on 4 sept. 2021 г.
@author: oleg st
'''

import pandas as pd
from flask import render_template
from urllib.parse import quote
from app.app_api import tsc_query
from app import app_api
onto_mod_api = app_api.get_mod_api('onto_mgt')

class Document:
    def __init__(self, argm):

        self.argm = argm
        self.parent = onto_mod_api.get_parent(argm['prefix'], argm['class'])

        self.pref_unquote = ''
        prefixes = onto_mod_api.get_prefixes()
        for p in prefixes:
            if p[0] == argm['prefix']:
                self.pref_unquote = p[1]

        query = tsc_query('mod_data_navigation.Document.one_instances',
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

        query_class_lbl = tsc_query('mod_data_navigation.Document.class_lbl',
                     {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
        df_cls = pd.DataFrame(query_class_lbl)

        if len(df_cls):
            class_lbl = df_cls.cls_lbl[0]
        else:
            class_lbl = self.argm['class']

        query_paretn_lbl = tsc_query('mod_data_navigation.Document.class_lbl',
                                    {'URI': "<" + self.pref_unquote + self.parent + ">"})
        df_prnt = pd.DataFrame(query_paretn_lbl)

        if len(df_prnt):
            parent_lbl = df_prnt.cls_lbl[0]
        else:
            parent_lbl = self.parent

        # Если есть аргумент URI, то значит показываем страничку "Экземпляра класса"
        if 'uri' in self.argm.keys():
            query_inst = tsc_query('mod_data_navigation.Document.instance',
                                   {'PREF': self.pref_unquote, 'URI': self.argm['uri']})
            df = pd.DataFrame(query_inst)

            if len(df) > 0:
                templ = render_template("/Document_inst.html", title="TEST",
                                class_name='<a href="{}?prefix={}">{}</a>'.format(self.argm['class'], self.argm['prefix'], class_lbl),
                                instance=df.to_html(escape=False, index=False),
                                argm=self.argm.items())

            else:
                templ = render_template("/Document_inst.html", title="TEST",
                                class_name='<a href="{}?prefix={}">{}</a>'.format(self.argm['class'], self.argm['prefix'], class_lbl),
                                instances="No data about this instance.",
                                argm=self.argm.items())

        # В остальных случаях показываем страничку со "Списком экземпляров класса и его подклассами"
        else:
            query_subclass = tsc_query('mod_data_navigation.Document.list_of_subclasses',
                                       {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
            df = pd.DataFrame(query_subclass)
            if len(df) > 0:
                df.cls = '<a href="/datanav/' + df.cls.str.replace(self.pref_unquote,'') + \
                         '?prefix=' + self.argm['prefix'] + '">' + df.cls_lbl + '</a>'

            query_list_inst = tsc_query('mod_data_navigation.Document.list_of_instances',
                                        {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
            df2 = pd.DataFrame(query_list_inst)
            if len(df2) > 0:
                df2.inst = '<a href="/datanav/' + self.argm['class']  + '?prefix=' + self.argm['prefix'] + '&uri=' + \
                           df2.inst.str.replace(self.pref_4_data, quote(self.pref_4_data)) + '">' + df2.inst_lbl + '</a>'
                df2.drop('inst_lbl', axis=1, inplace=True)

            if self.parent == 'Thing':
                pref = 'owl'

            if self.parent:
                parent = '<a href="/datanav/{}?prefix={}">{}</a>'.format(self.parent,pref, parent_lbl)

            if len(df) > 0:
                subclasses = df.to_html(escape=False, index=False)

            if len(df2) > 0:
                instances = df2.to_html(escape=False, index=False)

            templ = render_template("/Document.html", title="TEST", class_name=class_lbl,
                                                                            parent=parent,
                                                                            subclasses=subclasses,
                                                                            instances = instances,
                                                                            argm=self.argm.items())

        return templ
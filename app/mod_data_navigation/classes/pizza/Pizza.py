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

class Pizza:
    def __init__(self, argm):

        self.argm = argm
        self.parent = onto_mod_api.get_parent(argm['prefix'], argm['class'])

        self.pref_unquote = ''
        prefixes = onto_mod_api.get_prefixes()
        for p in prefixes:
            if p[0] == argm['prefix']:
                self.pref_unquote = p[1]

        query = tsc_query('mod_data_navigation.Pizza.one_instances',
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

        # Если есть аргумент URI, то значит показываем страничку "Экземпляра класса"
        if 'uri' in self.argm.keys():
            query_inst = tsc_query('mod_data_navigation.Pizza.instance',
                                   {'PREF': self.pref_unquote, 'URI': self.argm['uri']})
            df = pd.DataFrame(query_inst)

            if len(df) > 0:
                templ = render_template("/Pizza_inst.html", title="TEST",
                                class_name='<a href="{}?prefix={}">{}</a>'.format(self.argm['class'], self.argm['prefix'], self.argm['class']),
                                instance=df.to_html(escape=False),
                                argm=self.argm.items())

            else:
                templ = render_template("/Pizza_inst.html", title="TEST",
                                class_name='<a href="{}?prefix={}">{}</a>'.format(self.argm['class'], self.argm['prefix'], self.argm['class']),
                                instances="No data about this instance.",
                                argm=self.argm.items())

        # В остальных случаях показываем страничку со "Списком экземпляров класса и его подклассами"
        else:
            query_subclass = tsc_query('mod_data_navigation.Pizza.list_of_subclasses',
                                       {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
            df = pd.DataFrame(query_subclass)
            if len(df) > 0:
                df.cls = '<a href="/datanav/' + df.cls.str.replace(self.pref_unquote,'') + \
                         '?prefix=' + self.argm['prefix'] + '">' + df.cls_lbl + '</a>'
                df.drop('cls_lbl', axis=1, inplace=True)

            query_list_inst = tsc_query('mod_data_navigation.Pizza.list_of_instances',
                                        {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
            df2 = pd.DataFrame(query_list_inst)

            if len(df2) > 0:
                df2.inst = '<a href="/datanav/' + self.argm['class']  + '?prefix=' + self.argm['prefix'] + '&uri=' + \
                           df2.inst.str.replace(self.pref_4_data, quote(self.pref_4_data)) + '">' + df2.inst_lbl + '</a>'
                df2.drop('inst_lbl', axis=1, inplace=True)


            if self.parent == 'Thing':
                pref = 'owl'

            if self.parent:
                parent = '<a href="/datanav/{}?prefix={}">{}</a>'.format(self.parent,pref, self.parent)

            if len(df) > 0:
                subclasses = df.to_html(escape=False, index=False, header=False)

            if len(df2) > 0:
                instances = df2.to_html(escape=False, index=False, header=False)

            templ = render_template("/Pizza.html", title="TEST", class_name=self.argm['class'],
                                                                            parent=parent,
                                                                            subclasses=subclasses,
                                                                            instances = instances)

        return templ
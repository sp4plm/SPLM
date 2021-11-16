# -*- coding: utf-8 -*-
'''
Created on 4 sept. 2021 г.
@author: oleg st
'''

import pandas as pd
import numpy as np
from flask import render_template
from urllib.parse import quote
from app.app_api import tsc_query
from app import app_api
from hashlib import sha1
onto_mod_api = app_api.get_mod_api('onto_mgt')

class PizzaTopping:
    def __init__(self, argm):

        self.argm = argm
        self.parent = onto_mod_api.get_parent(argm['prefix'], argm['class'])

        self.pref_unquote = ''
        prefixes = onto_mod_api.get_prefixes()
        for p in prefixes:
            if p[0] == argm['prefix']:
                self.pref_unquote = p[1]

        query = tsc_query('mod_data_navigation.PizzaTopping.one_instances',
                          {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
        if query:
            self.pref_4_data = query[0]['inst'].split("#")[0] + "#"
        else:
            self.pref_4_data = ''

    def __make_href__(self,cls='',prf='', uri='', lbl=''):
        if uri =='':
            uri_str = '<a href="{}?prefix={}">{}</a>'.format(cls,prf,lbl)
        else:
            uri_str = '<a href="{}?prefix={}&uri={}">{}</a>'.format(cls,prf,uri,lbl)


        return uri_str

    def getTemplate(self):
        '''
        Возвращает шаблон HTML страницы, сформированный в соответствии с полученными в URL аргументами
        '''

        pref = self.argm['prefix']
        parent = self.parent
        subclasses = ''
        instances = ''
        d = {}

        query_class_lbl = tsc_query('mod_data_navigation.PizzaTopping.class_lbl',
                     {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
        df_cls = pd.DataFrame(query_class_lbl)

        if len(df_cls):
            class_lbl = df_cls.cls_lbl[0]
        else:
            class_lbl = self.argm['class']

        query_paretn_lbl = tsc_query('mod_data_navigation.PizzaTopping.class_lbl',
                                    {'URI': "<" + self.pref_unquote + self.parent + ">"})
        df_prnt = pd.DataFrame(query_paretn_lbl)

        if len(df_prnt):
            parent_lbl = df_prnt.cls_lbl[0]
        else:
            parent_lbl = self.parent


        # Если есть аргумент URI, то значит показываем страничку "Экземпляра класса"
        if 'uri' in self.argm.keys():
            query_inst = tsc_query('mod_data_navigation.PizzaTopping.instance',
                                   {'PREF': self.pref_unquote, 'URI': self.argm['uri']})
            df = pd.DataFrame(query_inst)

            # INSERT PICTURE ----------------------------------------------------
            myHash = sha1(self.argm['uri'].encode('utf-8')).hexdigest()
            gravatar_url = "http://www.gravatar.com/avatar/{}?d=identicon&s=300".format(myHash)
            Avatar = '<img src=\"' + gravatar_url + '\" width=\"400\" height=\"400\" alt=\"pizza topping\">'


            if len(df) > 0:
                for ind, row in df.iterrows():
                    if not row.inst_lbl in d:
                        d.update({row.inst_lbl:{} })
                    if row.att_cls_lbl == 'Topping':
                        row_topp = row.att_val.split('&&')
                        d[row.inst_lbl].update({row.att_cls_lbl : self.__make_href__(cls=row_topp[0].split('#')[1],
                                                                                    prf='pizza', uri=row_topp[1],
                                                                                     lbl=row_topp[2])})
                    elif row.att_cls_lbl == 'Base':
                        row_base = row.att_val.split('&&')
                        d[row.inst_lbl].update({row.att_cls_lbl: self.__make_href__(cls=row_base[0].split('#')[1],
                                                                                    prf='pizza', uri=row_base[1],
                                                                                    lbl=row_base[2])})
                    else:
                        d[row.inst_lbl].update({row.att_cls_lbl : row.att_val})


                d[row.inst_lbl].update({'Avatar':Avatar})

                templ = render_template("/PizzaTopping_inst.html", title="Пицца",
                                class_name=self.__make_href__(cls=self.argm['class'], prf=self.argm['prefix'], uri='',lbl=class_lbl),
                                instance=d,
                                argm=self.argm.items())

            else:
                templ = render_template("/PizzaTopping_inst.html", title="Пицца",
                                class_name=self.__make_href__(cls=self.argm['class'], prf=self.argm['prefix'], uri='', lbl=class_lbl),
                                instance={"No data":{"Comment":"about this instance.","Avatar":""}},
                                argm=self.argm.items())

        # В остальных случаях показываем страничку со "Списком экземпляров класса и его подклассами"
        else:
            # ------------- subclasses --------------------------
            query_subclass = tsc_query('mod_data_navigation.PizzaTopping.list_of_subclasses',
                                       {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
            df = pd.DataFrame(query_subclass)
            if len(df) > 0:
                df.cls = '<a href="' + df.cls.str.replace(self.pref_unquote,'') + \
                         '?prefix=' + self.argm['prefix'] + '">' + df.cls_lbl + '</a>'
                df.drop('cls_lbl', axis=1, inplace=True)
                df.columns = ['Наименование','Доступно для заказа']

            # ------------- list of instances --------------------------
            query_list_inst = tsc_query('mod_data_navigation.PizzaTopping.list_of_instances',
                                        {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})
            df2 = pd.DataFrame(query_list_inst)

            if len(df2) > 0:
                # Если у экземпляра нет лейбла, то вместо него вставляем часть URI
                df2.inst_lbl.replace('', np.nan, inplace=True)
                df2.inst_lbl.fillna(value=df2.inst.str.replace(self.pref_unquote, ''), inplace=True)

                df2.insert(loc=2, column='Avatar', value="")
                for ind, row in df2.iterrows():
                    myHash = sha1(row.inst.encode('utf-8')).hexdigest()
                    gravatar_url = "http://www.gravatar.com/avatar/{}?d=identicon&s=50".format(myHash)
                    df2.iloc[ind]['Avatar'] = '<img src=\"' + gravatar_url + '\" width=\"40\" height=\"40\" alt=\"pizza topping\">'

                df2.inst = '<a href="' + self.argm['class']  + '?prefix=' + self.argm['prefix'] + '&uri=' + \
                           df2.inst.str.replace(self.pref_4_data, quote(self.pref_4_data)) + '">' + df2.inst_lbl + '</a>'
                df2.drop('inst_lbl', axis=1, inplace=True)
                df2.columns = ['Наименование', 'Картинка']

            if self.parent == 'Thing':
                pref = 'owl'

            if self.parent:
                parent = self.__make_href__(cls=self.parent, prf=pref, lbl=parent_lbl)

            if len(df) > 0:
                subclasses = df.to_html(escape=False, index=False)

            if len(df2) > 0:
                instances = df2.to_html(escape=False, index=False)

            templ = render_template("/PizzaTopping.html", title="Пицца", class_name=class_lbl,
                                                                            parent=parent,
                                                                            subclasses=subclasses,
                                                                            instances = instances)

        return templ
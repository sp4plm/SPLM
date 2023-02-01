# -*- coding: utf-8 -*-
'''
Created on 4 sept. 2021 г.
@author: oleg st
'''

import pandas as pd
from app import app_api


class Blank:
    def __init__(self, current_class, argm):
        self.argm = argm
        self.current_class=current_class
        self.df_inst = pd.DataFrame()
        self.df_subclass = pd.DataFrame()


    def getTemplate(self):
        '''
        Возвращает шаблон HTML страницы, сформированный в соответствии с полученными в URL аргументами
        '''

        return app_api.render_page("data_navigation/Blank.html", title="Blank",
                            class_name = self.current_class,
                            error=self.argm)

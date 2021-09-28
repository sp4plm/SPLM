# -*- coding: utf-8 -*-
import os
from app.query_mgt.query_conf import QueryConf
from app.query_mgt.views import create_sparqt_manager

class ModApi(QueryConf):
    _class_file = __file__
    _debug_name = 'QueryUtilsApi'


    @staticmethod
    def create_sparqt_manager(__URL, __mod):
        return create_sparqt_manager(__URL, __mod)



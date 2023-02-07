# -*- coding: utf-8 -*-
import os
from app.query_mgt.query_conf import QueryConf
from app.query_mgt.views import create_sparqt_manager

class ModApi(QueryConf):
    _class_file = __file__
    _debug_name = 'QueryUtilsApi'

    @staticmethod
    def create_sparqt_manager(__URL, __mod):
        """
        Создает новые методы для интерфейса редактирования sparqt шаблонов
        Для модуля blueprint : __mod под адресом : <base_mod_uri>/__URL

        :param str __URL: наш url по которому будет SPARQTManager,
		:param Blueprint __mod: экземпляр класса blueprint в файле views текущего модуля,

		:return: метод реализующий редактор sparqt-файлов для модулей через интерфейс.
		:rtype: def
        """
        return create_sparqt_manager(__URL, __mod)



# -*- coding: utf-8 -*-
import os

# from app.utilites.code_helper import CodeHelper
from app.onto_mgt.onto_conf import OntoConf
from app.onto_mgt.ontology import Ontology

class OntoUtils(OntoConf):
    _class_file = __file__
    _debug_name = 'OntoUtils'

    @staticmethod
    def get_prefixes(onto_file):
        """ Возвращает словрь префиксов онтологии {prefix : uri} """
        return Ontology(onto_file).getPrefixes()

    @staticmethod
    def get_classes(onto_file):
        """ Возвращает словрь классов онтологии {uri : label} """
        return Ontology(onto_file).getClasses()

    @staticmethod
    def get_ontos():
        """ Возвращает список списков [fullname, baseURI] """
        return Ontology().getOntos()

    

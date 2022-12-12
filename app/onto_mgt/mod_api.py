# -*- coding: utf-8 -*-
import os

from app.onto_mgt.onto_conf import OntoConf
from app.onto_mgt.ontology import Ontology


class ModApi(OntoConf):
    _class_file = __file__
    _debug_name = 'OntoModApi'

    @staticmethod
    def get_prefixes():
        """ Возвращает список списков префиксов и baseURI онтологий [prefix, baseUri] """
        return Ontology().getPrefixes()

    @staticmethod
    def get_all_prefixes(onto = ""):
        """ Возвращает словарь префиксов онтологии onto в формате {prefix : uri}. onto - префикс онтологии. Если onto = "", то возвращает словарь префиксов всех онтологий в формате {prefix : uri}. """
        return Ontology().getAllPrefixes(onto)

    @staticmethod
    def get_classes(onto):
        """ Возвращает словарь классов онтологии {uri : label}, где onto - префикс онтологии."""
        return Ontology().getClasses(onto)

    @staticmethod
    def get_ontos():
        """ Возвращает список списков [fullname, baseURI] """
        return Ontology().getOntos()
    
    @staticmethod
    def get_parent(onto, child):
        """ Возвращает родителя класса child для онтологии onto; onto - префикс онтологии, child - название класса без baseUri. """
        return Ontology().getParent(onto, child)
    
    @staticmethod
    def get_graph(onto):
        """ Возвращает объект rdflib.graph онтологии onto; onto - префикс онтологии. """
        return Ontology().getGraph(onto)
    

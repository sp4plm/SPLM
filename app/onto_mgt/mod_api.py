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
        """ onto - префикс онтологии """
        """ Возвращает словарь префиксов онтологии onto {prefix : uri} ; """
        """ Если onto = "", то возвращает словарь префиксов всех онтологий {prefix : uri} """
        return Ontology().getAllPrefixes(onto)

    @staticmethod
    def get_classes(onto):
        """ onto - префикс онтологии """
        """ Возвращает словарь классов онтологии {uri : label} """
        return Ontology().getClasses(onto)

    @staticmethod
    def get_ontos():
        """ Возвращает список списков [fullname, baseURI] """
        return Ontology().getOntos()
    
    @staticmethod
    def get_parent(onto, child):
        """ onto - префикс онтологии, child - название класса без baseUri """
        """ Возвращает родителя класса child для онтологии onto"""
        return Ontology().getParent(onto, child)
    
    @staticmethod
    def get_graph(onto):
        """ onto - префикс онтологии """
        """ Возвращает объект rdflib.graph онтологии onto"""
        return Ontology().getGraph(onto)
    

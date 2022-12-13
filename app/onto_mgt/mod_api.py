# -*- coding: utf-8 -*-
import os

from app.onto_mgt.onto_conf import OntoConf
from app.onto_mgt.ontology import Ontology


class ModApi(OntoConf):
    _class_file = __file__
    _debug_name = 'OntoModApi'

    @staticmethod
    def get_prefixes():
        """ Возвращает список списков префиксов и baseURI онтологий

        :return: [prefix, baseUri], где prefix(str) и baseUri(str)
        :rtype: list"""
        return Ontology().getPrefixes()

    @staticmethod
    def get_all_prefixes(onto = ""):
        """ Возвращает словарь префиксов онтологии в формате словаря для указанной в параметре онтологии.

        :param str onto: префикс онтологии.
        :return: {prefix : uri}
        :rtype: dict

        Если onto = "", то возвращает словарь префиксов всех зарегистрированных на портале онтологий. """
        return Ontology().getAllPrefixes(onto)

    @staticmethod
    def get_classes(onto):
        """ Возвращает словарь классов онтологии:

        :param str onto: префикс онтологии
        :return: {uri : label}
        :rtype: dict"""
        return Ontology().getClasses(onto)

    @staticmethod
    def get_ontos():
        """ Возвращает список списков:

        :return: [[fullname, baseURI]]
        :rtype: list"""
        return Ontology().getOntos()
    
    @staticmethod
    def get_parent(onto, child):
        """ Возвращает родителя для класса child из онтологии onto;

        :param str onto: префикс онтологии,
        :param str child: название класса без baseUri.

        :return: имя класса
        :rtype: str"""
        return Ontology().getParent(onto, child)
    
    @staticmethod
    def get_graph(onto):
        """ Возвращает объект граф, который формирует из TTL файла онтологии

        :param str onto: onto - это префикс онтологии.
        :return: экземпляр класса для указанной онтологии.
        :rtype: rdflib.graph"""
        return Ontology().getGraph(onto)
    

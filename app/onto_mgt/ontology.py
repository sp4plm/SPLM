# -*- coding: utf-8 -*-

import os
import re
from rdflib import Graph, RDF, OWL, RDFS

from app.onto_mgt.files_managment import FilesManagment
from app.utilites.code_helper import CodeHelper

from app.onto_mgt.views import *

from app.app_api import compile_query_result

class Ontology():
    _class_file = __file__
    _debug_name = 'Ontology'

    MOD_DATA_PATH = os.path.dirname(os.path.abspath(__file__))

    onto_file = ""
    dir_name = "ontos"

    ONTOS_PREFIXES = []


    def __init__(self, onto_file = None):
        self.prefixes = {}
        self.onto_file = onto_file



    def addOntology(self):
        # /loadFiles/ontos
        upload_files()


    def deleteOntology(self):
        # /removeFile/ontos
        remove_file()


    def updateOntology(self):
        # В текущей реализации работы с онтологиями добавить и обновить онтологию
        # выполняет одна функция с условием проверяющим существование загружаемой онтологии
        self.addOntology()




    def getClassName(self, ontology_class):
        """ Возвращает имя класса без URI : ontology_class """
        try:
            ontology, ontology_class = ontology_class.split("#")
        except Exception as e:
            pass

        return ontology_class


    def getBaseUri(self, file_name):
        """ Возвращает baseUri по файлу : fullname """
        _baseURI = ""
        mfile = open(file_name, "r", encoding="utf-8")
        for line in mfile.readlines():
            baseURI = re.findall(r'^\s*#\s*baseURI:\s*(.*)\s*$', line.strip())
            if baseURI:
                _baseURI = baseURI[0]
                if not _baseURI.endswith("#"):
                    _baseURI += "#"

        mfile.close()

        return _baseURI





    def getFileOntoByPrefix(self, prefix):
        """ Возвращает файл по префиксу : fullname """
        uri = ""
        prefs = self.getPrefixes()
        for pref in prefs:
            if pref[0] == prefix:
                uri = pref[1]

        ontos = self.getOntos()
        for onto in ontos:
            if onto[1] == uri:
                return onto[0]

        return ""



    def getOntoPrefix(self, onto_file):
        """ Возвращает префикс по файлу : prefix """
        baseURI = self.getBaseUri(onto_file)

        prefixes = {}
        mfile = open(onto_file, "r", encoding="utf-8")
        for line in mfile.readlines():
            prefix = re.findall(r'^\s*@prefix\s+(\w+):\s*<(.*)>\s*\.\s*$', line.strip())
            if prefix:
                prefixes[prefix[0][1]] = prefix[0][0]

        mfile.close()

        if baseURI in prefixes:
            return prefixes[baseURI]

        return ""




    def getPrefixes(self):
        """ Возвращает список префиксов всех онтологий [[prefix, baseUri], ...]"""
        self.ONTOS_PREFIXES = []
        ontos = self.getOntos()
        for onto in ontos:
            self.ONTOS_PREFIXES.append([self.getOntoPrefix(onto[0]), onto[1]])

        return self.ONTOS_PREFIXES



    def getAllPrefixes(self, onto = ""):
        """ Возвращает словарь префиксов онтологий {prefix : uri} """
        prefixes = {}
        if onto:
            onto_file = self.getFileOntoByPrefix(onto)
            mfile = open(onto_file, "r", encoding="utf-8")
            for line in mfile.readlines():
                prefix = re.findall(r'^\s*@prefix\s+(\w+):\s*<(.*)>\s*\.\s*$', line.strip())
                if prefix:
                    prefixes[prefix[0][0]] = prefix[0][1]

            mfile.close()

        else:
            prefs = self.getPrefixes()
            for pref in prefs:
                result = self.getAllPrefixes(pref[0])
                prefixes = {**prefixes, **result}

        return prefixes



    def getClasses(self, onto):
        """ Возвращает словарь классов онтологии {uri : label} """
        classes = {}
        self.onto_file = self.getFileOntoByPrefix(onto)

        if self.onto_file:
            g = Graph()
            g.parse(self.onto_file, format='ttl')

            for class_name in g.subjects(RDF.type, OWL.Class):
                for class_label in g.objects(class_name, RDFS.label):
                    classes[str(class_name)] = str(class_label)

        return classes


    def getOntos(self):
        """ Возвращает список списков [fullname, baseURI] """
        ontos = []

        df = FilesManagment()
        file_list = df.get_dir_source("ontos")
        for file in file_list:
            ontos.append([file["fullname"], self.getBaseUri(file["fullname"])])
        
        return ontos
    

    def getParent(self, onto, class_name):
        """ Возвращает родителя класса parent """
        parent = ""

        onto_file = self.getFileOntoByPrefix(onto)
        graph = Graph().parse(onto_file, format='ttl')


        QUERY = "SELECT ?parent WHERE { %s:%s rdfs:subClassOf ?parent . filter (isIRI(?parent)) }" % (onto, class_name)
        parent_result = compile_query_result( json.loads( graph.query(QUERY).serialize(format="json").decode("utf-8") )  )

        if parent_result:
            parent = self.getClassName(parent_result[0]["parent"])

        return parent



    def getGraph(self, onto):
        """ Возвращает объект rdflib.graph онтологии по префиксу """
        onto_file = self.getFileOntoByPrefix(onto)
        graph = Graph().parse(onto_file, format='ttl')

        return graph


# -*- coding: utf-8 -*-

import os
import re
from rdflib import Graph, RDF, OWL, RDFS

from app.onto_mgt.files_managment import FilesManagment
from app.utilites.code_helper import CodeHelper

from app.onto_mgt.views import *

class Ontology():
    _class_file = __file__
    _debug_name = 'Ontology'

    MOD_DATA_PATH = os.path.dirname(os.path.abspath(__file__))

    onto_file = ""
    dir_name = "ontos"


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


    def getPrefixes(self):
        """ Возвращает словрь префиксов онтологии {prefix : uri} """
        prefixes = {}
        if self.onto_file:
            mfile = open(self.onto_file, "r", encoding="utf-8")
            for line in mfile.readlines():
                prefix = re.findall(r'^\s*@prefix\s*(\w+):\s*<(.*)>\s*\.\s*$', line.strip())
                if prefix:
                    prefixes[prefix[0][0]] = prefix[0][1]

            mfile.close()

        return prefixes



    def getClasses(self):
        """ Возвращает словрь классов онтологии {uri : label} """
        classes = {}

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
            baseURI = None
            if "baseURI" in file:
                baseURI = file["baseURI"]
            ontos.append([file["fullname"], baseURI])
        
        return ontos





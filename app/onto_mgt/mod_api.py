# -*- coding: utf-8 -*-
import os

from app.onto_mgt.onto_conf import OntoConf
from app.onto_mgt.onto_utils import OntoUtils


class ModApi(OntoConf):
    _class_file = __file__
    _debug_name = 'OntoModApi'

    @staticmethod
    def get_onto_utils():
        return OntoUtils

    @staticmethod
    def get_prefixes(onto_file):
        return OntoUtils().get_prefixes(onto_file)

    @staticmethod
    def get_classes(onto_file):
        return OntoUtils().get_classes(onto_file)

    @staticmethod
    def get_ontos():
        return OntoUtils().get_ontos()
    

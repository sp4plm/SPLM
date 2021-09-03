# -*- coding: utf-8 -*-
from app.admin_mgt.admin_conf import AdminConf
from app.drivers.store_manager import StoreManager
from app.utilites.some_config import SomeConfig

import os
import json

class Utilites:

    namespaces = {
        "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
        "owl" : "http://www.w3.org/2002/07/owl#",
        "dc" : "http://purl.org/dc/elements/1.1/",
        "dcterm" : "http://purl.org/dc/terms/",
        "foaf" : "http://xmlns.com/foaf/0.1/",
        "fti" : "http://franz.com/ns/allegrograph/2.2/textindex/",
        "skos" : "http://www.w3.org/2004/02/skos/core#",
        "raos" : "http://proryv2020.ru/odek/data#",
        "onto" : "http://proryv2020.ru/req_onto#",
        "err" : "http://www.w3.org/2005/xqt-errors#",
        "fn" : "http://www.w3.org/2005/xpath-functions#",
        "xs" : "http://www.w3.org/2001/XMLSchema#",
        "xsd" : "http://www.w3.org/2001/XMLSchema#",
        "qudt" : "http://data.nasa.gov/qudt/owl/qudt#"
    }

    def __init__(self):
        self.endPoint = ""
        self.driver = ""
        self.triplestore = ""

        # self.PORTAL_DATA_FILE = "portal_data.json"


    # def getQueryData(self):
    #     """
    #     Метод возвращает namespaces из json
    #     :return: namespaces
    #     """
    #     with open(os.path.join(MOD_DATA_PATH, self.PORTAL_DATA_FILE), "r", encoding="utf-8") as f:
    #         return json.load(f)


    @classmethod
    def getQueryData(self):
        """
        Метод возвращает реквизиты для работы с триплстором
        :return: url, headers, namespaces
        """
        app_cfg = SomeConfig(AdminConf.CONFIGS_PATH)
        self.endPoint = app_cfg.get("main.DataStorage.endPoints.main")
        self.driver = app_cfg.get("main.DataStorage.drivers.main")

        self.triplestore = StoreManager.get_driver(self.driver)
        self.triplestore.set_endpoint(self.endPoint)

        url = self.triplestore.get_endpoint()
        headers = self.triplestore.get_headers()

        return url, headers, self.namespaces

    @staticmethod
    def get_storage_driver():
        app_cfg = SomeConfig(AdminConf.CONFIGS_PATH)
        _endpoint = app_cfg.get("main.DataStorage.endPoints.main")
        _driver_name = app_cfg.get("main.DataStorage.drivers.main")
        _driver = StoreManager.get_driver(_driver_name)
        _driver.set_endpoint(_endpoint)
        return _driver


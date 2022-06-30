# -*- coding: utf-8 -*-
from app.admin_mgt.admin_conf import AdminConf
from app.drivers.store_manager import StoreManager
from app.utilites.some_config import SomeConfig

import os
import json

class Utilites:

    def __init__(self):
        self.endPoint = ""
        self.driver = ""
        self.triplestore = ""


    @classmethod
    def get_query_data(self):
        """
        Метод возвращает реквизиты для работы с триплстором, которые получает от драйвера текущего хранилища
        :return: url, headers
        """
        _driver = self.get_storage_driver()
        return _driver.get_endpoint(), _driver.get_headers()

    @staticmethod
    def get_storage_driver():
        app_cfg = SomeConfig(AdminConf.get_configs_path())
        _endpoint = app_cfg.get("data_storages.EndPoints.main")
        _driver_name = app_cfg.get("data_storages.Drivers.main")
        _driver = StoreManager.get_driver(_driver_name)
        _driver.set_endpoint(_endpoint)
        return _driver

    @staticmethod
    def get_file_editor():
        from app.kv_editor.mod_api import ModApi
        editor_api = ModApi()
        return editor_api


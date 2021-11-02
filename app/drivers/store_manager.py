# -*- coding: utf-8 -*-

from app.drivers.store_driver_agraph import StoreDriverAgraph
from app.drivers.store_driver_fuseki import StoreDriverFuseki
from app.drivers.store_driver_blazegraph import StoreDriverBlazegraph


class StoreManager:
    _class_file = __file__

    @staticmethod
    def get_driver(name):
        if 'fuseki' == name:
            return StoreDriverFuseki()
        if 'agraph' == name:
            return StoreDriverAgraph()
        if 'blazegraph' == name:
            return StoreDriverBlazegraph()
        raise Exception('Undefined store driver name -> "{}"!' . format(name))

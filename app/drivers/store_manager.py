# -*- coding: utf-8 -*-

from app.drivers.store_driver_agraph import StoreDriverAgraph
from app.drivers.store_driver_fuseki import StoreDriverFuseki
from app.drivers.store_driver_blazegraph import StoreDriverBlazegraph

from app import app_api


class StoreManager:
    _class_file = __file__

    @staticmethod
    def get_driver(name):
        if 'fuseki' == name:
            return StoreDriverFuseki()
        if 'agraph' == name:
            return StoreDriverAgraph()
        if 'blazegraph' == name:
            _drv = StoreDriverBlazegraph()
            _store_cfg = StoreManager.__get_store_conf()
            # _app_cfg.get('data_storages.Accounts.main')
            _store_cred = ''
            if 'Accounts' in _store_cfg:
                _store_cred = _store_cfg['Accounts']['main']
            if '' != _store_cred:
                _use_store_auth = True  # использовать для измененя хранилища авторизацию
                parsed_cred = StoreManager.__get_parsed_store_credential(_store_cred)
                _store_user = parsed_cred[0]
                _store_secret = parsed_cred[1]
                if _drv is not None:
                    _drv.use_auth_admin = _use_store_auth
                    _drv.set_auth_credential(_store_user, _store_secret)
            return _drv
        raise Exception('Undefined store driver name -> "{}"!' . format(name))

    @staticmethod
    def __get_parsed_store_credential(to_parse):
        parsed = []
        semi_ind = to_parse.find(':')
        uname = to_parse[0:semi_ind]
        usecret = to_parse[semi_ind + 1:]
        parsed.append(uname)
        parsed.append(usecret)
        return parsed

    @staticmethod
    def __get_store_conf():
        _app_cfg = app_api.get_app_config()
        _store_cfg = _app_cfg.get('data_storages')
        return _store_cfg

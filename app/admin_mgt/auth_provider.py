# -*- coding: utf-8 -*-
from app.admin_mgt.auth import *


class AuthProvider:
    _class_file = __file__
    _debug_name = 'PortalAuthProvider'

    type = ''

    def __init__(self):
        self._driver = None
        self._init_driver()

    def login(self, login, auth_secret):
        flg = False
        try:
            flg = self._driver.login(login, auth_secret)
        except Exception as ex:
            print('AuthProvider.login Error: ', ex)
            flg = False
        return flg

    def get_user(self, login):
        user = None
        try:
            user = self._driver.get_user(login)
        except Exception as ex:
            print('AuthProvider.get_user Error:', ex)
            user = None
        return user

    def _init_driver(self):
        # self._driver = LDAPAuthProvider()
        # return
        from app import app_api
        _mod_man = app_api.get_mod_manager()
        _auth_mods = _mod_man.get_drivers_by_subj("authorization")
        # print('AdminMGT.views._test_auth_provider->_auth_mods', _auth_mods)
        # теперь надо получить протокол LDAP
        _work_mod = None
        if _auth_mods:
            portal_uri = app_api.get_portal_onto_uri()
            # print('AdminMGT.views._test_auth_provider->portal_uri', portal_uri)
            from rdflib import Namespace, URIRef, Literal
            OSPLM = Namespace(portal_uri+'#')
            # print('AdminMGT.views._test_auth_provider->predicate', URIRef(portal_uri + '#useMethod'))
            # print('AdminMGT.views._test_auth_provider->portal_uri', Literal('ldap'))
            portal_cfg = app_api.get_app_config()
            _auth_met = portal_cfg.get('main.Auth.protocol')  # "ldap"
            _q = 'SELECT ?s WHERE { ?s <%s> ?o . ' % str(OSPLM.useMethod)
            _q += 'FILTER(?o="%s" || ?o="%s") }' % (_auth_met.lower(), _auth_met.upper())
            _q += ' LIMIT 1'
            _work_mod_name = ''
            for _m in _auth_mods:
                _mod_inf = _mod_man.get_mod_decscription(_m)
                if len(_mod_inf):
                    # print('AdminMGT.views._test_auth_provider->catch mod info', _mod_inf)
                    _triples = _mod_inf.query(_q)
                    _lst = [str(_x) for _x in list(_triples)]
                    # print('AdminMGT.views._test_auth_provider-> catch triples', _lst)
                    if _lst:
                        _work_mod_name = _m
                        break
                pass
            # print('AdminMGT.views._test_auth_provider->_work_mod_name', _work_mod_name)
            if _work_mod_name:
                self._driver = app_api.get_mod_api(_work_mod_name)

# -*- coding: utf-8 -*-

import os
import requests
from urllib.parse import quote, quote_plus
from app.drivers.store_driver import StoreDriver


class StoreDriverBlazegraph(StoreDriver):
    _class_file = __file__
    _name = 'blazegraph'
    _graph_name_field = 'context'

    def __init__(self):
        super().__init__()
        self._after_modify_storage_triggers.append(self._trg_delete_duplicate_statements)
        self.export_types = [
            {'name': "N-Triples", 'content-type': "text/plain", 'file-ext': "nt", 'some-flag': True, 'description-length': 4},
            {'name': "N-Quads", 'content-type': "text/x-nquads", 'file-ext': "nq", 'some-flag': True, 'description-length': 4},
            {'name': "Extended N-Quads (NQX)", 'content-type': "application/x-extended-nquads", 'file-ext': "nqx", 'some-flag': True, 'description-length': 4},
            {'name': "RDF/XML", 'content-type': "application/rdf+xml", 'file-ext': "xml", 'some-flag': True, 'description-length': 4},
            {'name': "TriG", 'content-type': "application/trig", 'file-ext': "trig", 'some-flag': True, 'description-length': 4},
            {'name': "Turtle", 'content-type': "text/turtle", 'file-ext': "ttl", 'some-flag': True, 'description-length': 4}
        ]

    def cook_graph_name(self, suffix):
        return '<' + self._graph_name_prefix_iri + suffix + '>'

    def _exec_query(self, query, endpoint=''):
        """ send a query to the triple store """
        fields = {}
        query_key = 'query'
        return_result = True
        if not self._is_select_query(query):
            return_result = False
        if '' == endpoint:
            endpoint = self._get_query_url(return_result) # read default TripleStoreUri
        fields[query_key] = query
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept':  'application/sparql-results+json'}
        if -1 < query.find('CONSTRUCT'):
            headers['Accept'] = 'application/json'
        send_data = {}
        send_data['data'] = fields
        send_data['headers'] = headers
        auth = {}
        if not self._is_select_query(query) and  self.use_auth_admin:
            cred = self.get_auth_credential()
            auth['uname'] = cred[0]
            auth['usecret'] = cred[1]

        if auth:
            result_params = self._post_req(endpoint, send_data, auth['uname'], auth['usecret'])
        else:
            result_params = self._post_req(endpoint, send_data)

        result = None
        if result_params.ok:
            if return_result:
                result = result_params.text
            else:
                result = True
        else:
            result = False
        return result


    def _trg_delete_duplicate_statements(self):
        """ """
        flg = False
        return flg


    def _get_query_url(self, select_query=True):
        """ """
        url = ''
        url = os.path.join(self.get_endpoint(), "sparql")
        return url


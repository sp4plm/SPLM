# -*- coding: utf-8 -*-
import os
from app.drivers.store_driver import StoreDriver


class StoreDriverFuseki(StoreDriver):
    _class_file = __file__
    _debug_name = 'StoreDriverFuseki'
    _name = 'fuseki'
    _upload_file_name = 'files[]' # customize for storage - this one to Fuseki
    _graph_name_field = 'graph'
    
    def __init__(self):
        super().__init__()

    def cook_graph_name(self, suffix):
        return self._graph_name_prefix_iri + suffix

    def _exec_query(self, query, endpoint=''):
        """ send a query to the triple store """
        fields = {}
        send_data = {}
        query_key = 'query'
        return_result = True
        if not self._is_select_query(query):
            query_key = 'update'
            return_result = False
        if '' == endpoint:
            # fuseki endpoint use different urls for query: select and others
            endpoint = self._get_query_url(return_result) # read default TripleStoreUri
        fields[query_key] = query
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept':  'application/sparql-results+json'}
        if -1 < query.find('CONSTRUCT ') or -1 < query.find('construct '):
            headers['Accept'] = 'application/json'
        if fields:
            send_data['data'] = fields
        result_params = self._post_req(endpoint, send_data, headers)
        result = None
        if result_params.ok:
            if return_result:
                result = result_params.text
            else:
                result = True
        else:
            result = False
        return result

    def upload_file(self, file_path):
        flg = False
        send_data = {}
        auth = {}
        if self.use_auth_admin:
            cred = self.get_auth_credential()
            auth['uname'] = cred[0]
            auth['usecret'] = cred[1]

        send_data['headers'] = {}

        file_name = os.path.basename(file_path)
        url = self._get_file_upload_url()

        if self._use_named_graph:
            send_data['data'] = {}
            send_data['data'][self._graph_name_field] = self.cook_graph_name(file_name)

        send_data['files'] = {}
        send_data['files'][self._upload_file_name] = self.__cook_post_file(file_path)

        # send_data['headers']['Content-type'] = 'text/turtle;charset=utf-8'
        # send_data['headers']['Content-type'] = 'multipart/form-data' # не требуется - вызывает ошибку
        send_data['headers']['Content-Disposition'] = 'form-data; name="{}"; filename="{}"'.format(self._upload_file_name, file_name)

        if auth:
            answer = self._post_req(url, send_data, auth['uname'], auth['usecret'])
        else:
            answer = self._post_req(url, send_data)
        if answer.ok:
            flg = True
        else:
            self.to_log(self._debug_name + '.upload_file: result -> FAIL (' + file_name + ')')
        return flg

    def __cook_post_file(self, file_path):
        """"""
        file_mime = self.get_file_mime(file_path)
        return (os.path.basename(file_path), open(file_path, 'rb'), file_mime)

    def _get_file_download_url(self):
        """ """
        url = ''
        url = self.get_endpoint()
        url = url.replace('/query', '/get')
        return url

    def _get_file_upload_url(self):
        """ """
        url = ''
        url = self.get_endpoint()
        url = url.replace('/query', '/upload')
        return url

    def _get_query_url(self, is_select=True):
        """ """
        url = ''
        url = self.get_endpoint()
        if not is_select:
            url = url.replace('/query', '')
        return url

# -*- coding: utf-8 -*-

import os
import requests
from urllib.parse import quote, quote_plus
from app.drivers.store_driver import StoreDriver


class StoreDriverAgraph(StoreDriver):
    _class_file = __file__
    _name = 'agraph'
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
            # fuseki endpoint use different urls for query: select and others
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
        mime = self.get_file_mime(file_path)
        url = self._get_file_upload_url()

        url += '?'
        url += 'type=' + mime
        url += '&'
        url += 'uploadedFile=' + file_name

        if self._use_named_graph:
            url += '&'
            url += self._graph_name_field + '='
            url += quote(self.cook_graph_name(file_name))

        send_data['data'] = open(file_path, 'rb')

        send_data['headers']['Content-type'] = mime
        if auth:
            answer = self._post_req(url, send_data, auth['uname'], auth['usecret'])
        else:
            answer = self._post_req(url, send_data)
        if answer.ok:
            flg = True
        return flg

    def backup_to_file(self, file_path):
        flg = False
        """
        Скачивание файла
        :param url:
        :param target_file:
        :param uname:
        :param usecret:
        :return:
        """
        # https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
        # NOTE the stream=True parameter below
        url_args = {'stream': True}
        url = self._get_backup_url()
        if self._use_named_graph:
            export_type = self._get_export_type('N-Quads')
            if export_type is not None:
                url_args['headers'] = {}
                url_args['headers']['accept'] = export_type['content-type']
                # надо поменять расширение файла на првильное
                file_path = self.change_file_ext(file_path, export_type['file-ext'])
                file_name = file_path.split('/')[-1]
        if self.use_auth_admin:
            cred = self.get_auth_credential()
            url_args['auth'] = (cred[0], cred[1])
        try:
            with requests.get(url, **url_args) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)
            if os.path.exists(file_path):
                flg = True
                self._last_downloaded = file_path
        except Exception as ex:
            print('StoreDriverAgraph.backup_to_file.Error:', ex)
            flg = False
        return flg

    def _trg_delete_duplicate_statements(self):
        """ """
        """ statements/duplicates?mode=spo """
        flg = False
        url = self._get_backup_url()
        url += '/duplicates?mode=spo'
        send_data = {}
        if self.use_auth_admin:
            cred = self.get_auth_credential()
            send_data['auth'] = (cred[0], cred[1])
        answer = requests.delete(url, **send_data)
        if answer.ok:
            flg = True
        return flg

    def _trg_delete_graph_duplicate_statements(self):
        """ """
        """ statements/duplicates?mode=spog """
        flg = False
        url = self._get_backup_url()
        url += '/duplicates?mode=spog'
        send_data = {}
        if self.use_auth_admin:
            cred = self.get_auth_credential()
            send_data['auth'] = (cred[0], cred[1])
        answer = requests.delete(url, **send_data)
        if answer.ok:
            flg = True
        return flg

    def _get_export_type(self, name=''):
        export_type = None
        if self.export_types:
            if '' == name:
                export_type = self.export_types[0]
            else:
                for et in self.export_types:
                    if et['name'] == name:
                        export_type = et
                        break
        return export_type

    @staticmethod
    def change_file_ext(file, new_ext):
        dot_pos = file.rfind('.')
        base = file[:dot_pos+1]
        new_file = base + new_ext
        return new_file

    def _get_file_download_url(self):
        """ """
        url = ''
        url = self.get_endpoint()
        return url

    def _get_backup_url(self):
        """ """
        url = ''
        url = self.get_endpoint()
        url += '/statements'
        return url

    def _get_file_upload_url(self):
        """ """
        url = ''
        url = self.get_endpoint()
        url += '/statements'
        return url

    def _get_query_url(self, select_query=True):
        """ """
        url = ''
        url = self.get_endpoint()
        return url

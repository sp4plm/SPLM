# -*- coding: utf-8 -*-

import os
import requests


class StoreDriver:
    _class_file = __file__
    _debug_name = 'StoreDriver'
    _name = 'undefined'
    _graph_name_field = ''

    def __init__(self):
        self._endpoint_url = ''
        self._endpoint_parsed = None
        self._repository = ''
        self._use_named_graph = False
        self._use_auth = False
        self._store_user = ''
        self._store_secret = ''
        self._graph_name_prefix = 'graph'
        self._graph_name_prefix_iri = 'http://splm.portal.web/osplm/graph#'
        self._after_modify_storage_triggers = []
        self._last_downloaded = ''

    def query(self, text):
        """ """
        return self._exec_query(text)

    def _exec_query(self, query, endpoint=''):
        """ send a query to the triple store """
        fields = {}
        send_data = {}
        query_key = 'query'
        return_result = True
        if not (self._is_select_query(query) or self._is_construct_query(query)):
            # query_key = 'update'
            return_result = False
        if '' == endpoint:
            # fuseki endpoint use different urls for query: select and others
            endpoint = self._get_query_url(return_result) # read default TripleStoreUri
        fields[query_key] = query
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept':  'application/sparql-results+json'}
        if -1 < query.find('CONSTRUCT'):
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
        except:
            flg = False
        return flg

    def get_last_downloaded_file(self):
        return self._last_downloaded

    def upload_file(self, file_path):
        flg = False
        return flg

    def _post_req(self, url, send_data, uname='', usecret=''):
        """ Обертка для любого запроса POST"""
        answer = None
        if '' != uname and '' != usecret:
            send_data['auth'] = (uname, usecret)
        try:
            answer = requests.post(url, **send_data)
        except Exception as ex:
            answer_ex = str(ex)
            raise Exception(self._debug_name + '._post_req say: Cant not send post request! Exception: {}.'.format(answer_ex))
        return answer

    def _get_req(self, url, data, headers=None):
        send_data = {}
        if data:
            """"""
            send_data['data'] = data
        if headers:
            send_data['headers'] = headers
        answer = requests.get(url, **send_data)
        return answer

    @staticmethod
    def _is_select_query(text):
        flg = False
        # сперва надо отделить префиксы от запроса
        # разобьем по {
        parsed = text.split('{')
        # теперь в первом элементе ищем > последний закрывающий префикс
        parsed = parsed[0].split('>')
        # в последнем элементе начало тела запроса
        parsed = parsed[-1].strip()
        if -1 < parsed.lower().find('select'):
            flg = True
        return flg


    @staticmethod
    def _is_construct_query(text):
        flg = False
        # сперва надо отделить префиксы от запроса
        # разобьем по {
        parsed = text.split('{')
        # теперь в первом элементе ищем > последний закрывающий префикс
        parsed = parsed[0].split('>')
        # в последнем элементе начало тела запроса
        parsed = parsed[-1].strip()
        if -1 < parsed.lower().find('construct'):
            flg = True
        return flg



    @staticmethod
    def get_file_mime(file_path):
        mime_type = ''
        file_ext = ''
        file_ext = os.path.basename(file_path).split(os.path.extsep)[1]
        mime_list = {
            "ttl": "text/turtle; charset=utf-8",
            "n3": "text/n3; charset=utf-8",
            "nt": "text/plain",
            "rdf": "application/rdf+xml",
            "owl": "application/rdf+xml",
            "nq": "application/n-quads",
            "trig": "application/trig",
            "jsonld": "application/ld+json"
        }
        if file_ext in mime_list:
            mime_type = mime_list[file_ext]
        else:
            mime_type = mime_list['ttl']
        return mime_type

    def call_after_modify_storage_triggers(self):
        if 0 < len(self._after_modify_storage_triggers):
            try:
                for itri in self._after_modify_storage_triggers:
                    if callable(itri):
                        itri()
                    else:
                        print(self._debug_name + '.call_after_modify_storage_triggers: try call not function {}!'.format(itri))
            except Exception as ex:
                print(self._debug_name + '.call_after_modify_storage_triggers: call trigger exception/error: {}' .format(ex))
                # raise ex

    def _get_file_download_url(self):
        """ """
        url = ''
        url = self.get_endpoint()
        return url

    def _get_backup_url(self):
        """ """
        url = ''
        url = self.get_endpoint()
        return url

    def _get_file_upload_url(self):
        """ """
        url = ''
        url = self.get_endpoint()
        return url

    def _get_query_url(self, select_query=True):
        """ """
        url = ''
        url = self.get_endpoint()
        return url

    def set_auth_credential(self, uname, usecret):
        self._store_user = uname
        self._store_secret = usecret

    def get_auth_credential(self):
        return (self._store_user, self._store_secret)

    def set_graph_name_prefix(self, prefix):
        self._graph_name_prefix = prefix

    def set_graph_name_prefix_iri(self, iri):
        self._graph_name_prefix_iri = iri

    def cook_graph_name(self, suffix):
        return self._graph_name_prefix_iri + suffix

    @property
    def use_auth_admin(self):
        return self._use_auth

    @use_auth_admin.setter
    def use_auth_admin(self, flg):
        self._use_auth = bool(flg)

    @property
    def use_named_graph(self):
        return self._use_named_graph

    @use_named_graph.setter
    def use_named_graph(self, flg):
        self._use_named_graph = bool(flg)

    def set_repository(self, repo):
        self._repository = repo

    def get_repository(self):
        return self._repository

    def set_endpoint(self, uri):
        self._endpoint_url = uri

    def get_endpoint(self):
        return self._endpoint_url

    def get_headers(self):
        headers = {'Accept': 'application/sparql-results+json', "Content-Type": "application/x-www-form-urlencoded"}
        return headers

    def set_portal_onto_uri(self, uri):
        self._graph_name_prefix_iri = uri + '/' + self._graph_name_prefix + '#'

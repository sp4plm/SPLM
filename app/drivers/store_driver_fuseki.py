# -*- coding: utf-8 -*-

from app.drivers.store_driver import StoreDriver


class StoreDriverFuseki(StoreDriver):
    _class_file = __file__
    _name = 'fuseki'
    _graph_name_field = 'graph'
    
    def __init__(self):
        super().__init__()

    def cook_graph_name(self, suffix):
        return self._graph_name_prefix_iri + suffix

    def upload_file(self, file_path):
        flg = False
        return flg

    def backup_to_file(self, file_path):
        flg = False
        return flg

    def _get_file_download_url(self):
        """ """
        url = ''
        url = self._endpoint
        url = url.replace('/query', '/get')
        return url

    def _get_file_upload_url(self):
        """ """
        url = ''
        url = self._endpoint
        url = url.replace('/query', '/upload')
        return url

    def _get_query_url(self, is_select=True):
        """ """
        url = ''
        url = self._endpoint
        if not is_select:
            url = url.replace('/query', '')
        return url

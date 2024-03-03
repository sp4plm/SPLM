# -*- coding: utf-8 -*-
import os
from app.search_mgt.search_conf import SearchConf


class ModApi(SearchConf):
    _class_file = __file__
    _debug_name = 'SearchModApi'

    def make_search_link(self, _search):
        _link = ''
        from flask import url_for
        _link = url_for(self.MOD_NAME + '.search') + '/?arg=' + str(_search)
        return _link

    def make_code_link(self, _search):
        _link = ''
        from flask import url_for
        _link = url_for(self.MOD_NAME + '.__search_by_code', label_code=str(_search))
        return _link

# -*- coding: utf-8 -*-

import os

from app import CodeHelper


class Utils:
    _class_file=__file__
    _debug_name='user_mgt.Utils'

    @staticmethod
    def udata_2_xml(udata):
        _xml = ''
        _xml += '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'+"\r\n"
        _xml += '<Rows>'
        for ud in udata:
            _xml += '<Row>'+Utils.udata_2_xml_cells(ud)+'</Row>'
        _xml += '</Rows>'
        return _xml

    @staticmethod
    def udata_2_xml_cells(ud):
        udd = {}
        if not isinstance(ud, dict):
            udd = ud.to_dict()
        else:
            udd = ud
        _str = ''
        if 'name' in udd:
            _str += Utils.ufield_2_xml_cell(udd['name'])
        else:
            _str += Utils.ufield_2_xml_cell('')
        if 'login' in udd:
            _str += Utils.ufield_2_xml_cell(udd['login'])
        else:
            _str += Utils.ufield_2_xml_cell('')
        if 'email' in udd:
            _str += Utils.ufield_2_xml_cell(udd['email'])
        else:
            _str += Utils.ufield_2_xml_cell('')
        return _str

    @staticmethod
    def ufield_2_xml_cell(uf):
        _str = ''
        _str = str(uf)
        return '<cell>' + _str +' </cell>'

    @staticmethod
    def get_now():
        from datetime import datetime
        return datetime.now()

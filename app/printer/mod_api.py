# -*- coding: utf-8 -*-
import os
from .mod_env import ModEnv
from .table_report import TableReport
from .table_report2 import TableReport2
from .report import Report

"""

_test_report = {
    'name': 'Исходные требования проекта',
    'print': '/reports/reports/analytics/1?prefix=onto',
    'report_id': 1,
    'analytics_queries': ['mod_reports.analytics.contracts_reqs_cnt', 'mod_reports.analytics.normdoc_reqs_cnt', 'mod_reports.analytics.total_reqs_cnt'],
    'table_cols_names': ['Требования проекта', 'Всего требований'],
    'table_row_names': ['Требования ТЗ', 'Требования НТД', 'Итого'],
    'more': '/reports/analytics/requirements?prefix=onto',
    'dbgMode': '  ',
    'numbers': ['1066', '0', '1066'],
    'table': [
      ['<th class="TableRow_header" align="center" style="width:40%;">Требования проекта</th>', '<th class="TableRow_header" align="center" style="">Всего требований</th>'],
      ['<td style="width:40%;">Требования ТЗ</td>', '<td class="TableRow_not_header table_text_color_397927" align="center">1066</td>'],
      ['<td style="width:40%;">Требования НТД</td>', '<td class="TableRow_not_header table_text_color_397927" align="center">0</td>'],
      ['<th style="width:40%;text-align:left;" scope="col">Итого</th>', '<th class="report-main table_text_color_397927" scope="col">1066</th>']
    ],
    'html': '  <table class="simple-tbl report-data create_table_publics" width="80%"><tbody><tr><th class="TableRow_header" align="center" width="40%" style="width:40%;">Требования проекта</th><th class="TableRow_header" align="center" width="60%" style="">Всего требований</th></tr><tr><td style="width:40%;">Требования ТЗ</td><td class="TableRow_not_header table_text_color_397927" align="center">1066</td></tr><tr><td style="width:40%;">Требования НТД</td><td class="TableRow_not_header table_text_color_397927" align="center">0</td></tr><tr><th style="width:40%;text-align:left;" scope="col">Итого</th><th class="report-main table_text_color_397927" scope="col">1066</th></tr></tbody></table>'
  }
  
_test_report['report_data'] = [
        [
            {'value': 'Требования проекта', 'font-size': 14, 'bgcolor': '#d0e5f5', 'width': '40%', 'align': 'c', 'border': 1},
            {'value': 'Всего требований', 'font-size': 14, 'bgcolor': '#d0e5f5', 'width': '40%', 'align': 'h', 'border': 1}
        ],
        [
            {'value': 'Требования ТЗ', 'font-size': 12, 'align': 'l', 'width':40, 'height': 0, 'border': 1},
            {'value': 1066, 'font-size': 12, 'color': '#397927', 'font-style': 'b', 'align': 'c', 'width':40, 'height': 0, 'border': 1}
        ],
        [
            {'value': 'Требования НТД', 'font-size': 12, 'align': 'l', 'width':40, 'height': 0, 'border': 1},
            {'value': 0, 'font-size': 12, 'color': '#397927', 'font-style': 'b', 'align': 'c', 'width':40, 'height': 0, 'border': 1}
        ],
        [
            {'value': 'Итого', 'font-size': 12, 'font-style': 'b', 'align': 'r', 'width':40, 'height': 0, 'border': 1},
            {'value': 1066, 'font-size': 12, 'color': '#397927', 'font-style': 'b', 'align': 'c', 'width':40, 'height': 0, 'border': 1}
        ]
    ]
_test_report['logo1'] = os.path.join(_images, 'logo_rosatom.png')
_test_report['logo2'] = os.path.join(_images, 'proryv-logo.png')
_test_report['watermark'] = os.path.join(_images, 'logo_rosatom.png')
_test_report['project'] = 'Прорыв ОДЭК'
_test_report['width'] = '80%'
  
"""


class ModApi():
    _class_file = __file__
    _debug_name = 'PrinterModApi'

    def __init__(self):
        self._env = ModEnv()

    def table_report_new(self, _report_data):
        _report = TableReport2()
        arg = ''
        _k = 'logo1'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_logo_1(arg)  # (os.path.join(_images, 'logo_rosatom.png'))

        arg = ''
        _k = 'logo2'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_logo_2(arg)  # (os.path.join(_images, 'proryv-logo.png'))

        arg = ''
        _k = 'name'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_title(arg)

        arg = ''
        _k = 'project'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_project_name(arg)  # ('Прорыв')

        arg = ''
        _k = 'watermark'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_watermark(arg)  # (watermark['water_view'])

        arg = '80%'
        _k = 'width'
        if _k in _report_data:
            arg = _report_data[_k]
        arg = '90%'
        _report.set_table_width(arg)  # ('80%')

        arg = []
        _k = 'numbers'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_sign_data(arg)
        arg = []
        _k = 'report_data'
        if _k in _report_data:
            arg = _report_data[_k]
        else:
            _k = 'table'
            if _k in _report_data:
                arg = self._html_rows2report_data(_report_data[_k])
                # print(self._debug_name + '.table_report -> report_data(table) ', arg)
        _report.set_data(arg)

        arg = (0, 0, 0)
        arg = self._env.cfg.get('main.table_report.header_color')  # default settings in hex
        _k = 'header_color'
        if _k in _report_data:
            arg = _report_data[_k]
        if isinstance(arg, str) and arg.startswith('#'):
            try:
                arg = _report.hex2rgb(arg)
            except:
                pass
        _report.set_header_color(arg)

        arg = (255, 255, 255)  # (208, 240, 142)
        arg = self._env.cfg.get('main.table_report.header_bgcolor')  # default settings in hex
        _k = 'header_bgcolor'
        if _k in _report_data:
            arg = _report_data[_k]
        if isinstance(arg, str) and arg.startswith('#'):
            try:
                arg = _report.hex2rgb(arg)
            except:
                pass
        _report.set_header_bgcolor(arg)

        arg = 0
        arg = self._env.cfg.get('main.table_report.repeat_header')
        _k = 'repeat_header'
        if _k in _report_data:
            arg = _report_data[_k]
        if arg in ('0', 'off', 'Off', 'OFF'):
            arg = False
        if not isinstance(arg, bool):
            arg = True if arg else False
        _report.set_repeat_header(arg)

        return _report

    def table_report(self, _report_data):
        if 2.6 < TableReport.lib_version:
            # print('yesssss!')
            pass
            return self.table_report_new(_report_data)
        _report = TableReport()
        arg = ''
        _k = 'logo1'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_logo_1(arg)  # (os.path.join(_images, 'logo_rosatom.png'))

        arg = ''
        _k = 'logo2'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_logo_2(arg)  # (os.path.join(_images, 'proryv-logo.png'))

        arg = ''
        _k = 'name'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_title(arg)

        arg = ''
        _k = 'project'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_project_name(arg)  # ('Прорыв')

        arg = ''
        _k = 'watermark'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_watermark(arg)  # (watermark['water_view'])

        arg = '80%'
        _k = 'width'
        if _k in _report_data:
            arg = _report_data[_k]
        arg = '90%'
        _report.set_table_width(arg)  # ('80%')

        arg = []
        _k = 'numbers'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_sign_data(arg)
        arg = []
        _k = 'report_data'
        if _k in _report_data:
            arg = _report_data[_k]
        else:
            _k = 'table'
            if _k in _report_data:
                arg = self._html_rows2report_data(_report_data[_k])
                # print(self._debug_name + '.table_report -> report_data(table) ', arg)
        _report.set_data(arg)

        arg = (0, 0, 0)
        _k = 'header_color'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_header_color(arg)

        arg = (255, 255, 255)
        _k = 'header_bgcolor'
        if _k in _report_data:
            arg = _report_data[_k]
        _report.set_header_bgcolor(arg)
        # _report.set_html(_test_report['html'])
        # _report.print(_doc_pth)

        return _report

    def report(self):
        _report = Report()
        return _report

    @staticmethod
    def _html_rows2report_data(_rows):
        _data = []
        if _rows:
            _count_cell = len(_rows[0])
            for _r in _rows:
                # каждая строка - список ячеек html код ячейки - th or td
                _new_r = []
                _calc_w = ''
                _find_w = ''
                for _c in _r:
                    _col = ModApi._htmltag2dict(_c)
                    if 'width' in _col:
                        _find_w = _col['width']
                    else:
                        #  надо вычислить на основании найденной
                        # считаем что только для 1 указывается ширина
                        if _find_w.endswith('%'):
                            _perc = int(str(_find_w)[0:-1])
                            _empty = 100 - _perc
                            if 2 < _count_cell:
                                _w = _empty / (_count_cell - 1)
                                from decimal import Decimal
                                _t = round(Decimal(_w), 2)
                                _col['width'] = str(_t) + '%'
                            else:
                                _col['width'] = str(_empty) + '%'
                    _new_r.append(_col)
                _data.append(_new_r)
        return _data

    @staticmethod
    def _htmltag2dict(_html):
        _cnf = {}
        _tpl = {'value': '', 'font-size': 10, 'border': 1}
        _cnf = _tpl
        _t = _html[(_html.find('>') + 1):_html.find('</')]
        if -1 < _t.find('>'):
            # надо уточнить - остали  html теги
            _t = _t[(_t.find('>') + 1):]
        _cnf['value'] = _t
        _cnf['color'] = '#000000'
        _cnf['font-size'] = 10

        if _html.startswith('<th '):
            _cnf['font-style'] = 'B'
            _cnf['align'] = 'C'

        if -1 < _html.find('TableRow_header'):
            _cnf['font-style'] = 'B'
            _cnf['bgcolor'] = '#d0e5f5'
            # _cnf['font-size'] = 12
            _cnf['align'] = 'C'

        if -1 < _html.find('TableRow_not_header'):
            _cnf['font-style'] = 'B'

        if -1 < _html.find('width'):
            next_pos = _html.find('width') + len('width')
            if ':' == _html[next_pos]:
                # use style
                _stop = _html.find(';', next_pos)
                _cnf['width'] = _html[next_pos + 1:_stop]
            if '=' == _html[next_pos]:
                # use attribute
                _stop = _html.find('"', next_pos)
                _cnf['width'] = _html[next_pos + 1:_stop]

        if -1 < _html.find('align'):
            next_pos = _html.find('align') + len('align')
            if ':' == _html[next_pos]:
                # print('css align -> html', _html)
                _stop = _html.find(';', next_pos)
                _cnf['align'] = str(_html[next_pos + 1:_stop])[0]
            if '=' == _html[next_pos]:
                # print('attribute align -> html', _html)
                # print('attribute align -> next_pos', next_pos)
                _stop = _html.find('"', next_pos + 2)
                # print('attribute align -> _stop', _stop)
                # print('attribute align -> _html[next_pos] => ', _html[next_pos])
                _cnf['align'] = str(_html[next_pos + 2:_stop])[0]

        if -1 < _html.find('table_text_color_'):
            # так устанавливается цвет ячейки
            next_pos = _html.find('table_text_color_') + len('table_text_color_')
            _i = next_pos
            _len = len(_html)
            color = ''
            while _i < _len:
                _ch = _html[_i]
                if ' ' == _ch or '"' == _ch:
                    break
                color += _ch
                _i += 1
            # print('cell color -> ', color)
            _cnf['color'] = ModApi._normalize_color(color)

        # clearing
        if 'width' in _cnf:
            if 10 == _cnf['width'] or '10' == _cnf['width']:
                _cnf['width'] = '8%'
        return _cnf

    @staticmethod
    def _normalize_color(_color):
        _colors = {}
        _colors['red'] = 'FF0000'
        _colors['orange'] = 'FFA500'

        if _color in _colors:
            _color = _colors[_color]

        _color = '#' + _color

        return _color

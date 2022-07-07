# -*- coding: utf-8 -*-
import os
from datetime import datetime
from fpdf import XPos, YPos
from .document_fpdf import DocumentFpdf


class TableReport(DocumentFpdf):
    _class_file = __file__
    _debug_name = 'PrinterTableReport'

    def __init__(self):
        DocumentFpdf.__init__(self)
        self._main_title = 'Отчет'
        self._project_name = 'Проект'
        self._report_date_format = '%Y-%m-%d'
        self._data = None  # список списков
        self._html = ''
        self._title = ''
        self._report_date = ''
        self._table_w = ''
        self._calc_table_w = self.epw
        self._calc_col_widths = []
        self.__cur_col_width = 0
        self.__table_lh = self.font_size * 2.5
        self.__table_left_margin = 0
        self._sign_data = None
        self._last_tbl_cell = None
        self._row_start_x = 0
        self._row_end_x = 0
        self._row_start_y = 0
        self._row_end_y = 0

        self._report_orientation = "portrait"
        self._report_unit = "mm"
        self._report_format = "A4"
        self._report_pw = 210
        self._report_ph = 297
        self._report_lw = 297
        self._report_lh = 210

        self._table_mrx = []  #  список строк w, h, cells; cells -  список ячеек с размерами
        self._table_heads = []  # первая строка матрицы
        self._cur_process_sizes = None

    def set_sign_data(self, _data):
        self._sign_data = _data

    def _get_data_sign(self):
        numbers = '-'.join(self._sign_data)
        self._gen_sing(numbers)
        return self._sing

    def set_table_width(self, val):
        """
        Метод устанавливает размер таблицы принудительно процентах
        :param val:
        :return:
        """
        self._table_w = str(val)

    def __get_real_set_table_w(self):
        _width = self.epw
        _val = None
        _val = self._table_w
        if isinstance(self._table_w, str):
            if self._table_w.endswith('%'):
                _val = self._table_w[:-1]
                _val = round(float(int(_val)/100), 2)
            else:
                if self._table_w.isdigit():
                    _val = round(float(self._table_w), 2)
                    if 1 < _val:
                        _val = round(_val/100, 2)

        if isinstance(self._table_w, int) and 0 < self._table_w:
            _val = float(round(_val/100, 2))
        if isinstance(self._table_w, float):
            _val = self._table_w

        _width = self.epw * _val
        return _width

    def set_data(self, _data):
        """"""
        if not isinstance(_data, list):
            raise TypeError(_data)
        self._data = _data
        # теперь по первой строке узнаем ширину таблицы и ширину колонок
        self.__calc_table_sizes()
        # print(self._debug_name + '.set_data -> self._calc_table_w', self._calc_table_w)
        # print(self._debug_name + '.set_data -> self._calc_col_widths', self._calc_col_widths)
        # print(self._debug_name + '.set_data -> self.epw', self.epw)
        # print(self._debug_name + '.set_data -> self.eph', self.eph)
        if self.epw < self._calc_table_w:
            self._report_orientation = "landscape"
            #  надо пересчитать размеры колонок на эффективную ширину
            # _new_col_width = []
            # for _cw in self._calc_col_widths:
            #     _c_perc = round(_cw/self._calc_table_w, 2)
            #     _ncw = self.eph * _c_perc
            #     _new_col_width.append(_ncw)
            # # print(self._debug_name + '.set_data -> _new_col_width', _new_col_width)
            # print(self._debug_name + '.set_data -> self.epw, self._calc_table_w: ', self.epw, self._calc_table_w)
            # if _new_col_width:
            #     self._calc_col_widths = _new_col_width
            # else:
            # print(self._debug_name + '.set_data -> empty recalculated width! (_new_col_width)')

    def _get_datarow_widths(self, _ind):
        _list_width = []
        if self._data and _ind in self._data:
            pass
            _work_line = self._data[_ind]
            """
            {'value': '', 'font-size': 12, 'color': '', 'bgcolor': '', 'font-style': 'IBU', 'align': 'LCR',
            'width':0, height: 0, 'border': 1, 'border-color': ''
            }
            """
            for _c in _work_line:
                _w = self._get_str_width(_c['value'])
                _list_width.append(_w)
        return _list_width

    def _get_str_width(self, _some_str, _font_size=None, _font_style=None, _font_fam=None):
        _width = 0
        _old = []
        _old.append(self.font_family)
        _old.append(self.font_style)
        _old.append(self.font_size)
        if _font_fam is None:
            _font_fam = self._default_font_fam
        try:
            self.set_font(_font_fam, '')
        except Exception as ex:
            _font_fam = self._default_font_fam

        if _font_size is None:
            _font_size = self._default_font_size
        try:
            _font_size = int(_font_size)
        except Exception as ex:
            _font_size = self._default_font_size

        if _font_size is None:
            _font_style = ''
        else:
            if '' != _font_style:
                if 3 < len(_font_style):
                    _font_style = _font_style[0:3]
                _font_style = _font_style.upper()
                _t = ''
                for _s in _font_style:
                    if _s in 'IBU':
                        _t += _s
                _font_style = _t

        self.set_font_size(_font_size)
        self.set_font(self._default_font_fam, style=_font_style)
        self.get_string_width(_some_str)
        # возвращаем старые установки
        self.set_font(_old[0], _old[1], _old[2])
        return _width

    def __calc_table_sizes(self):
        if self._data:
            _headers = self._data[0]
            _total_w = 0
            # for _th in _headers:
            #     _col_w = 0
            #     _col_w = self.__calc_col_width(_th)
            #     self._calc_col_widths.append(_col_w)
            #     _total_w += _col_w
            #     if 'border' in _th:
            #         # надо прибавлять левую и правую границы
            #         _total_w += 2
            # self._calc_table_w = _total_w
            _tw = 0
            _th = 0

            # считаем первая строка - это заголовки
            # пытаемся расчитать как есть

            # есть интересная засада - заголовки могут быть большими, но сами данные будут маленькими по длине символов
            # следовательно надо проверить первыю строку данных

            _ci = 0
            _test_cw = []
            for _cth in _headers:
                _cs = self.__calc_col_sizes(_cth, _ci)
                _tw += _cs[0]
                _test_cw.append(_cs)
                _ci += 1

            _new_cols_w = None
            if _tw > self.epw:
                # print(self._debug_name + '.__calc_table_sizes ->need to recalc width!!!!!!')
                # print(self._debug_name + '.__calc_table_sizes -> _tw ', _tw)
                # print(self._debug_name + '.__calc_table_sizes -> self.epw ', self.epw)
                # print(self._debug_name + '.__calc_table_sizes -> self.eph ', self.eph)
                # print(self._debug_name + '.__calc_table_sizes -> self.w ', self.w)
                # print(self._debug_name + '.__calc_table_sizes -> self.h ', self.h)
                # print(self._debug_name + '.__calc_table_sizes -> self.l_margin ', self.l_margin)
                # print(self._debug_name + '.__calc_table_sizes -> self.r_margin ', self.r_margin)
                # print(self._debug_name + '.__calc_table_sizes -> self.t_margin ', self.t_margin)
                # print(self._debug_name + '.__calc_table_sizes -> self.b_margin ', self.b_margin)
                _h_2_epw = self.h - round(self.l_margin + self.r_margin)
                # print(self._debug_name + '.__calc_table_sizes -> calced _h_2_epw ', _h_2_epw)
                _new_cols_w = []
                for _cth in _test_cw:
                    _cp = round(_cth[0]/_tw, 2)
                    _ncw = _h_2_epw * _cp
                    _new_cols_w.append(_ncw)
                    # print(self._debug_name + '.__calc_table_sizes -> old_w, new_w ', _cth[0], _ncw)
            else:
                _new_cols_w = []
                if self._table_w:
                    _table_w = self.__get_real_set_table_w()
                    for _cth in _test_cw:
                        _cp = round(_cth[0]/_tw, 2)
                        _ncw = _table_w * _cp
                        _new_cols_w.append(_ncw)
                else:
                    for _cth in _test_cw:
                        _new_cols_w.append(_cth[0])

            for _r in self._data:
                _rs = self.__calc_row_sizes(_r, _new_cols_w)
                if _tw < _rs['w']:
                    _tw = _rs['w']
                _th += _rs['h']
                if not self._table_heads:
                    # обработали первую строку - разбираемся влазаем ли мы в страницу
                    self._table_heads = _rs['cells']
                self._table_mrx.append(_rs)
            # print(self._debug_name + '.__calc_table_sizes -> table size matrix ==============================')
            # print(self._debug_name + '.__calc_table_sizes -> table width: ', _tw)
            # print(self._debug_name + '.__calc_table_sizes -> table height: ', _th)
            # print(self._debug_name + '.__calc_table_sizes -> sizes matrix: ', self._table_mrx)
            # print(self._debug_name + '.__calc_table_sizes -> table size matrix ==============================')
            self._calc_table_w = _tw

    def __calc_row_sizes(self, _row, _widths=[]):
        _tpl = {}
        _tpl['w'] = 0
        _tpl['h'] = 0
        _tpl['cells'] = []
        _rs = _tpl
        _ci = 0
        for _c in _row:
            _master_w = _widths[_ci] if _widths else None
            _cs = self.__calc_col_sizes(_c, _ci, _master_w)
            _tpl['w'] += _cs[0]
            if _tpl['h'] < _cs[1]:
                _tpl['h'] = _cs[1]
            _rs['cells'].append(_cs)
            _ci += 1
        # print(self._debug_name + '.__calc_table_sizesizes -> result: ', _rs)
        return _rs

    def __calc_col_sizes(self, _cell, _i, _master_width=None):
        _cs = None
        """
        размеры ячеек считаем исключительно под контент
        """
        _val = ' '
        _val = str(_cell.get('value', _val))
        _width = 0
        _height = 0
        self.set_font(self._default_font_fam, '')
        _color = self.hex_to_rgb(_cell.get('color', '#000000'))
        self.set_text_color(*_color)
        _font_size = 12
        _font_size = _cell.get('font-size', _font_size)
        self.set_font_size(_font_size)
        _font_style = ''
        if 'font-style' in _cell:
            _t = _cell.get('font-style', '').strip()
            if '' != _t:
                _font_style = ''
                _t = _t.upper()[0:3]
                for _ch in _t:
                    if _ch in 'IBU':
                        _font_style += _ch
        self.set_font(self._default_font_fam, style=_font_style)
        if _master_width is None:
            # print(self._debug_name + '.__calc_col_sizes->calc with: ')
            _width = self.get_string_width(_val)
        else:
            # print(self._debug_name + '.__calc_col_sizes->master with: ')
            _width = _master_width
        line_height = self.font_size * 2.5
        # print(self._debug_name + '.__calc_col_sizes->self.font_size: ', self.font_size)
        # print(self._debug_name + '.__calc_col_sizes->_width: ', _width)
        # print(self._debug_name + '.__calc_col_sizes->line_height: ', line_height)
        # print(self._debug_name + '.__calc_col_sizes->_val: |' + _val + '|')
        _lines = []
        try:
            _lines = self.multi_cell(_width, line_height, str(_val), border=0, split_only=True, max_line_height=line_height)
        except Exception as ex:
            _lines.append(str(_val))
            print(self._debug_name + '.__calc_col_sizes->Exception: (', type(ex), ')', str(ex))

        _height = len(_lines) * line_height  # self.font_size
        # print(self._debug_name + '.__calc_col_sizes->len(_lines): ', len(_lines))
        _cs = (_width, _height)
        # print(self._debug_name + '.__calc_col_sizes->result: ', _cs)
        return _cs

    def __calc_col_width(self, _cell):
        _width = 0
        """
                {'value': '', 'font-size': 12, 'color': '', 'bgcolor': '', 'font-style': 'IBU', 'align': 'LCR',
                'width':0, height: 0, 'border': 1, 'border-color': ''
                }
                """
        if not _cell:
            return  # пока выходим

        # если ширину таблицы назначили и ширина ячейки в процентах то вычисляем
        # если ширину таблицы не назначили то считаем как есть
        _val = ''
        _val = str(_cell.get('value', _val))
        _col_width = 0
        self.set_font(self._default_font_fam, '')
        # _calc_cont_w = self.get_string_width(_val)
        # print(self._debug_name + '.__calc_col_width->_calc_cont_w (before styling): ', _calc_cont_w)

        # text-color -> _cell.get('color') -> hex
        _color = self.hex_to_rgb(_cell.get('color', '#000000'))
        self.set_text_color(*_color)
        # font-size -> _cell.get('font-size') -> pt
        _font_size = 12
        _font_size = _cell.get('font-size', _font_size)
        self.set_font_size(_font_size)

        # font-style -> _cell.get('font-style') -> string ' ' | 'IBU'
        _font_style = 'B'
        if 'font-style' in _cell:
            _t = _cell.get('font-style', '').strip()
            if '' != _t:
                _font_style = ''
                _t = _t.upper()[0:3]
                for _ch in _t:
                    if _ch in 'IBU':
                        _font_style += _ch
        # print(self._debug_name + '.__calc_col_width->_font_style: ', _font_style)
        self.set_font(self._default_font_fam, style=_font_style)

        # когда все украшательства выверены следует заняться шириной
        _col_width = 40
        # if 'width' in _cell:
        #     _tw = _cell.get('width')
        #     if isinstance(_tw, int):
        #         _col_width = int(_tw)
        #     elif isinstance(_tw, str):
        #         if _tw.endswith('%'):
        #             if 0 < self._table_w:
        #                 # print('_tw', _tw, type(_tw))
        #                 val = int(float(_tw[:-1]))
        #                 _col_width = self._table_w * (val / 100)
        #             else:
        #                 _col_width = _tw
        #         else:
        #             _col_width = int(_tw)
        # else:
        #     _col_width = self.get_string_width(_val)
        #     # print(self._debug_name + '.__calc_col_width->_col_width (not set height): ', _col_width)
        #     if 0 < self._table_w:
        #         _col_width = self._table_w * ((_col_width/self._table_w))
        #     else:
        #         _col_width += 2 * 2

        _col_width = self.get_string_width(_val)
        # print(self._debug_name + '.__calc_col_width->_col_width (not set height): ', _col_width)
        if 0 < self._table_w:
            _col_width = self._table_w * ((_col_width / self._table_w))
        else:
            _col_width += 2 * 2
        # print(self._debug_name + '.__calc_col_width->_calc_cont_w (+lr margin 2): ', _calc_cont_w)
        # print(self._debug_name + '.__calc_col_width->_col_width (result): ', _col_width)
        return _col_width

    def _set_report_date(self):
        _date = datetime.now().strftime(self._report_date_format)
        self._report_date = _date

    def set_report_date_format(self, format='%Y-%m-%d'):
        self._report_date_format = format

    def set_title(self, title):
        if title:
            self._title = str(title)

    def set_project_name(self, name):
        if name:
            self._project_name = str(name)

    def set_document_title(self, title):
        # заглушка - для блокирования изменения
        pass

    def set_html(self, html):
        if html:
            self._html = str(html)

    def _add_header(self):
        """
        Метод вставляет в отчет шапку
        :return:
        """
        self.set_text_color(0)
        if not self.pages:
            self.add_page(orientation=self._report_orientation, format=self._report_format)
        # print(self._debug_name + '._add_header->start')
        self.ln(6)
        # document name
        self.set_font("DejaVuSans", "B", 16)
        self.cell(0, 6, self._main_title, border=1, new_x="LMARGIN", new_y="NEXT", align="C", fill=False)
        # project name
        self.set_font_size(14)
        self.cell(0, 6, self._project_name, border=1, new_x="LMARGIN", new_y="NEXT", align="C", fill=False)
        # Performing a line break:
        self.ln(4)
        # report name
        self.set_font("DejaVuSans", "", 12)
        # у названия отчета может быть длинное название и содержать куски html -  переноса строк
        _val = self._title
        _val = _val.replace('<br />', "\n")
        _val = _val.replace('<br >', "\n")
        _val = _val.replace('<br>', "\n")
        _val = _val.replace('<hr>', "")
        _val = _val.replace('<hr >', "")
        _val = _val.replace('<hr /->', "")
        _width = self.get_string_width(_val)
        _width = self.epw
        _lh = self.font_size * 2.5
        _new_x = "LMARGIN"
        _new_y = "NEXT"
        _border = 1
        _align = "C"
        _lines = self.multi_cell(_width, _lh, _val, border=0, align=_align, fill=False, split_only=True,
                                 new_x=_new_x, new_y=_new_y, max_line_height=self.font_size)
        if 1 == len(_lines):
            _new_x = "LMARGIN"
            _new_y = "NEXT"
            self.cell(0, 6, _val, border=_border, new_x=_new_x, new_y=_new_y, align=_align, fill=False)
        else:
            _ch = len(_lines) * _lh
            self.multi_cell(_width, _lh, _val, border=_border, align=_align, fill=False,
                        new_x=_new_x, new_y=_new_y, max_line_height=self.font_size, )
        # report date
        self._set_report_date()
        self.cell(0, 6, self._report_date, border=1, new_x="LMARGIN", new_y="NEXT", align="C", fill=False)
        # Performing a line break:
        self.ln(4)

    # def print(self, _to):
    #     """
    #     Метод создает pdf документ по указанному пути _to
    #     :param _to: полное имя файла для вывода(сохранения)
    #     :return:
    #     """
    #     # print(self._debug_name + '.print->_to:', _to)
    #     self.__compile_content()
    #     self.output(_to)
    #
    # def stream(self):
    #     self.__compile_content()
    #     return self.output()

    def _compile_content(self):
        # print(self._debug_name + '.__compile_content->start')
        # print(self._debug_name + '.__compile_content->self', type(self))
        self._add_header()
        # теперь надо разобраться с данными
        if self._data:
            self._draw_table()
        else:
            if self._html:
                self.write_html(self._html)

    def _draw_table(self):
        self.set_text_color(0)
        if self._data:
            self.set_auto_page_break(False)
            """
            по идее каждая строка должна представлять собой список словарей
            каждый словарь - описание одной ячейки, обязательный ключ -> 'value'
            {'value': '', 'font-size': 12, 'color': '', 'bgcolor': '', 'font-style': 'IBU', 'align': 'LCR',
            'width':0, height: 0, 'border': 1
            }
            """
            self.ln(4)  # margin-top fon-size * 3 rows
            # для начала разберемся с заголовками - первая строка в дата
            _work = self._data
            _headers = _work.pop(0)
            _base_calc_w = self._calc_table_w
            _table_w = self.__get_real_set_table_w()
            if _base_calc_w < _table_w:
                _base_calc_w = _table_w
            else:
                _base_calc_w = 0
                for _c in self._table_mrx[0]['cells']:
                    _base_calc_w += _c[0]
            self.__table_left_margin = int((self.w - _base_calc_w)/2)
            # print(self._debug_name + '._draw_table->self._table_w: ', self._table_w)
            # print(self._debug_name + '._draw_table->self._table_w: ', self.__get_real_set_table_w())
            # print(self._debug_name + '._draw_table->self._calc_table_w: ', self._calc_table_w)
            # print(self._debug_name + '._draw_table->self.__table_left_margin: ', self.__table_left_margin)
            self.set_x(self.__table_left_margin)
            _col_i = 0
            _row_len = len(_headers)
            self._row_start_x = self.get_x()
            self._row_start_y = self.get_y()
            self._row_end_x = self._row_start_x
            _cell_wh = []
            for _th in _headers:
                # self.__cur_col_width = self._calc_col_widths[_col_i]
                self._cur_process_sizes = self._table_mrx[0]
                self.__cur_col_width = self._cur_process_sizes['cells'][_col_i][0]
                if _col_i == _row_len-1:
                    self._last_tbl_cell = True
                # print(self._debug_name + '._draw_table->self.__cur_col_width (th): ', self.__cur_col_width)
                _cwh = self._draw_table_hcell(_th)
                _cell_wh.append(_cwh)
                # print(self._debug_name + '._draw_table->_cwh (th): ', _cwh)
                _col_i += 1
                pass
            # self._row_end_y = self.get_y()
            # print(self._debug_name + '._draw_table->self.get_y() after row (th): ', self.get_y())
            for _cwh in _cell_wh:
                self.line(_cwh[0], _cwh[1], _cwh[0], self._row_end_y)
            # print(self._debug_name + '._draw_table->_cwh (last): ', _cwh)
            self.line(self._row_end_x, _cwh[1], self._row_end_x, self._row_end_y)
            # self.ln()
            self.line(self._row_start_x, self._row_start_y, self._row_end_x, self._row_start_y)
            if 0 == len(_work):
                self.line(self._row_start_x, self._row_end_y, self._row_end_x, self._row_end_y)
            self.set_y(self._row_end_y)
            _rows =0
            for _row in _work:
                _col_i = 0
                self._cur_process_sizes = self._table_mrx[_rows+1]
                # print(self._debug_name + '._draw_table->self.b_margin: ', self.b_margin)
                # print(self._debug_name + '._draw_table->self._cur_process_sizes[h]: ', self._cur_process_sizes['h'])
                # print(self._debug_name + '._draw_table->self._row_end_y: ', self._row_end_y)
                # print(self._debug_name + '._draw_table->self.eph: ', self.eph)
                # -15 нижний колонтитул
                if self._row_end_y + self._cur_process_sizes['h'] > self.eph-10:
                    self.add_page(same=True)
                    self._row_start_x = 0
                    self._row_start_y = 0
                    self._row_end_x = 0
                    self._row_end_y = 0
                self.set_x(self.__table_left_margin)
                _row_len = len(_row)
                self._row_start_x = self.get_x()
                self._row_start_y = self.get_y()
                self._row_end_x = self._row_start_x
                _cell_wh = []
                for _ci in _row:
                    # self.__cur_col_width = self._calc_col_widths[_col_i]
                    self.__cur_col_width = self._cur_process_sizes['cells'][_col_i][0]
                    if _col_i == _row_len-1:
                        self._last_tbl_cell = True
                    # print(self._debug_name + '._draw_table->self.__cur_col_width (th): ', self.__cur_col_width)
                    # print(self._debug_name + '._draw_table->self.__cur_col_width (th): ', self.__cur_col_width)
                    _cwh = self._draw_table_bcell(_ci)
                    _cell_wh.append(_cwh)
                    # print(self._debug_name + '._draw_table->_cwh (td): ', _cwh)
                    _col_i += 1
                # print(self._debug_name + '._draw_table->draw cells, line -> ', str(_rows))
                # self._row_end_y = self.get_y()
                # self.ln()  # self.ln(line_height)
                for _cwh in _cell_wh:
                    self.line(_cwh[0], _cwh[1], _cwh[0], self._row_end_y)
                self.line(self._row_end_x, _cwh[1], self._row_end_x, self._row_end_y)
                # print(self._debug_name + '._draw_table->draw vertical lines, line -> ', str(_rows))
                self.set_y(self._row_end_y)
                _rows += 1
                self.line(self._row_start_x, self._row_start_y, self._row_end_x, self._row_start_y)
                self.line(self._row_start_x, self._row_end_y, self._row_end_x, self._row_end_y)
                # if 2 == _rows:
                #     break
                # 40  расчетный колонтитул


            # self.line(self._row_start_x, self._row_end_y, self._row_end_x, self._row_end_y)
            self.set_x(self.l_margin)
            self.set_text_color(0)

    def _draw_table_hcell(self, _cell):
        """"""
        """
        {'value': '', 'font-size': 12, 'color': '', 'bgcolor': '', 'font-style': 'IBU', 'align': 'LCR',
        'width':0, height: 0, 'border': 1, 'border'
        }
        """
        if not _cell:
            return  # пока выходим
        _val = ''
        _val = str(_cell.get('value', _val))
        _col_width = 0
        _border = 1
        _border_color = (0,0,0)
        _align = 'C'
        _fill = False

        # _calc_cont_w = self.get_string_width(_val)
        # print(self._debug_name + '._draw_table_hcell->_calc_cont_w (before styling): ', _calc_cont_w)

        # text-color -> _cell.get('color') -> hex
        _color = self.hex_to_rgb(_cell.get('color', '#000000'))
        self.set_text_color(*_color)
        # font-size -> _cell.get('font-size') -> pt
        _font_size = 12
        _font_size = _cell.get('font-size', _font_size)
        self.set_font_size(_font_size)
        line_height = self.font_size * 2.5
        # background-color -> _cell.get('bgcolor') -> hex
        if 'bgcolor' in _cell:
            _tbgc = _cell.get('bgcolor', '')
            if _tbgc:
                _fill = True
                _bgcolor = self.hex_to_rgb(_cell.get('bgcolor'))
                self.set_fill_color(*_bgcolor)

        # try to set border-color
        self.set_draw_color(*_border_color)
        # self.set_line_width(0.3)
        # font-style -> _cell.get('font-style') -> string ' ' | 'IBU'
        _font_style = 'B'
        if 'font-style' in _cell:
            _t = _cell.get('font-style', '').strip()
            if '' != _t:
                _font_style = ''
                _t = _t.upper()[0:3]
                for _ch in _t:
                    if _ch in 'IBU':
                        _font_style += _ch
        # print(self._debug_name + '._draw_table_hcell->_font_style: ', _font_style)
        self.set_font(self._default_font_fam, style=_font_style)
        # align -> _cell.get('align') -> string 'LCR'
        if 'align' in _cell:
            _t = _cell.get('align', _align)  # default is C -> center
            _t = _t.strip()[0].upper()
            if _t in 'LCR':
                _align = _t

        # когда все украшательства выверены следует заняться шириной
        # _col_width = 40
        # if 'width' in _cell:
        #     _tw = _cell.get('width')
        #     if isinstance(_tw, int):
        #         _col_width = int(_tw)
        #     elif isinstance(_tw, str):
        #         if _tw.endswith('%'):
        #             _base_calc_w = self._calc_table_w
        #             if 0 < self._table_w:
        #                 _base_calc_w = self._table_w
        #             val = int(float(_tw[:-1]))
        #             _col_width = _base_calc_w * (val+4 / 100)
        #         else:
        #             _col_width = int(_tw)


        # calc width for content
        # _calc_cont_w = self.get_string_width(_val)
        # print(self._debug_name + '._draw_table_hcell->_calc_cont_w: ', _calc_cont_w)
        # add lr margins -> +2
        # _calc_cont_w += 2*2
        # print(self._debug_name + '._draw_table_hcell->_calc_cont_w (+lr margin 2): ', _calc_cont_w)
        # print(self._debug_name + '._draw_table_hcell->self.font_size: ', self.font_size)
        _lh = (self.font_size * 2.5)

        # print(self._debug_name + '._draw_table_hcell->self.__cur_col_width: ', self.__cur_col_width)
        _col_width = self.__cur_col_width
        _table_w = self.__get_real_set_table_w()
        if isinstance(_col_width, str):
            if _col_width.endswith('%'):
                _base_calc_w = self._calc_table_w
                if 0 < _table_w:
                    _base_calc_w = _table_w
                val = int(_col_width[:-1])
                _col_width = _base_calc_w * (val/ 100)
        elif isinstance(_col_width, float):
            if _table_w > self._calc_table_w:
                _t = round(_col_width/self._calc_table_w, 2)
                _col_width = _table_w * _t
        # print(self._debug_name + '._draw_table_hcell->_col_width: ', _col_width)
        # self.cell(_col_width, 7, _val, border=_border, align=_align, fill=_fill)
        #  new_x=0, new_y=0,
        # from docs -> Using `new_x=XPos.RIGHT, new_y=XPos.TOP, maximum height=pdf.font_size` is
        #         useful to build tables with multiline text in cells.
        _new_x = XPos.RIGHT
        _new_y = YPos.TOP
        # if self.__cur_col_width == self._calc_col_widths[0]:
        #     # first cell
        #     _new_x = XPos.LEFT
        #     _new_y = YPos.NEXT
        # print(self._debug_name + '._draw_table_hcell->_col_width: ', _col_width)
        _sx = self.get_x()
        _sy = self.get_y()
        _ex = 0
        self._row_end_x = self._row_end_x + _col_width
        _lines = self.multi_cell(_col_width, _lh, _val, border=0, align=_align, fill=_fill, split_only=True,
                        new_x=_new_x, new_y=_new_y, max_line_height=_lh)
        # print(self._debug_name + '._draw_table_hcell->_lines: ', _lines)
        _ex = self.get_x() + _col_width
        _len_lines = len(_lines)
        if 1 == _len_lines:
            _ch = len(_lines) * line_height
        else:
            _ch = len(_lines) * line_height  #  self.font_size
        _ey = self.get_y() + self._cur_process_sizes['h']
        # self.multi_cell(_col_width, _lh, _val, border=0, align=_align, fill=_fill,
        #                 new_x=_new_x, new_y=_new_y, max_line_height=_lh)
        self.multi_cell(_col_width, self._cur_process_sizes['h'], _val, border=0, align=_align, fill=_fill,
                        new_x=_new_x, new_y=_new_y, max_line_height=_lh)
        if _ey > self._row_end_y:
            self._row_end_y = _ey
        if self._last_tbl_cell:
            self.ln(_lh)
            self._last_tbl_cell = False
        return (_sx, _sy, _ex, _ey)

    def _draw_table_bcell(self, _cell):
        """"""
        """
        {'value': '', 'font-size': 12, 'color': '', 'bgcolor': '', 'font-style': 'IBU', 'align': 'LCR',
        'width':0, height: 0, 'border': 1, 'border'
        }
        """
        if not _cell:
            return  # пока выходим
        _val = ''
        _val = str(_cell.get('value', _val))
        _col_width = 0
        _border = 1
        _border_color = (0,0,0)
        _align = 'L'
        _fill = False

        # _calc_cont_w = self.get_string_width(_val)
        # print(self._debug_name + '._draw_table_bcell->_calc_cont_w (before styling): ', _calc_cont_w)

        # text-color -> _cell.get('color') -> hex
        _color = self.hex_to_rgb(_cell.get('color', '#000000'))
        self.set_text_color(*_color)
        # font-size -> _cell.get('font-size') -> pt
        _font_size = 12
        _font_size = _cell.get('font-size', _font_size)
        self.set_font_size(_font_size)
        line_height = self.font_size * 2.5
        # background-color -> _cell.get('bgcolor') -> hex
        if 'bgcolor' in _cell:
            _tbgc = _cell.get('bgcolor', '')
            if _tbgc:
                _fill = True
                _bgcolor = self.hex_to_rgb(_cell.get('bgcolor'))
                self.set_fill_color(*_bgcolor)

        # try to set border-color
        self.set_draw_color(*_border_color)
        # self.set_line_width(0.3)
        # font-style -> _cell.get('font-style') -> string ' ' | 'IBU'
        _font_style = ''
        if 'font-style' in _cell:
            _t = _cell.get('font-style', '').strip()
            if '' != _t:
                _t = _t.upper()[0:3]
                for _ch in _t:
                    if _ch in 'IBU':
                        _font_style += _ch
        # print(self._debug_name + '._draw_table_bcell->_font_style: ', _font_style)
        self.set_font(self._default_font_fam, style=_font_style)
        # align -> _cell.get('align') -> string 'LCR'
        if 'align' in _cell:
            _t = _cell.get('align', _align)  # default is C -> center
            _t = _t.strip()[0].upper()
            if _t in 'LCR':
                _align = _t

        # когда все украшательства выверены следует заняться шириной
        # _col_width = 40
        # if 'width' in _cell:
        #     _tw = _cell.get('width')
        #     if isinstance(_tw, int):
        #         _col_width = int(_tw)
        #     elif isinstance(_tw, str):
        #         if _tw.endswith('%'):
        #             _base_calc_w = self._calc_table_w
        #             if 0 < self._table_w:
        #                 _base_calc_w = self._table_w
        #             val = int(float(_tw[:-1]))
        #             _col_width = _base_calc_w * (val / 100)
        #         else:
        #             _col_width = int(_tw)


        # calc width for content
        # _calc_cont_w = self.get_string_width(_val)
        # print(self._debug_name + '._draw_table_bcell->_calc_cont_w: ', _calc_cont_w)
        # add lr margins -> +2
        # _calc_cont_w += 2*2
        # print(self._debug_name + '._draw_table_bcell->_calc_cont_w (+lr margin 2): ', _calc_cont_w)
        _lh = self.font_size * 2.5

        # self.cell(self.__cur_col_width, 7, _val, border=_border, align=_align, fill=_fill)
        #  new_x=0, new_y=0,
        # from docs -> Using `new_x=XPos.RIGHT, new_y=XPos.TOP, maximum height=pdf.font_size` is
        #         useful to build tables with multiline text in cells.
        _new_x = XPos.RIGHT
        _new_y = YPos.TOP
        # if self.__cur_col_width == self._calc_col_widths[0]:
        #     # first cell
        #     _new_x = XPos.LEFT
        #     _new_y = YPos.NEXT
        # print(self._debug_name + '._draw_table_bcell->self.__cur_col_width: ', self.__cur_col_width)
        _col_width = self.__cur_col_width
        _table_w = self.__get_real_set_table_w()
        if isinstance(_col_width, str):
            if _col_width.endswith('%'):
                _base_calc_w = self._calc_table_w
                if 0 < _table_w:
                    _base_calc_w = _table_w
                val = int(_col_width[:-1])
                _col_width = _base_calc_w * (val / 100)
        elif isinstance(_col_width, float):
            if _table_w > self._calc_table_w:
                _t = round(_col_width/self._calc_table_w, 2)
                _col_width = _table_w * _t
        # print(self._debug_name + '._draw_table_bcell->_col_width: ', _col_width)
        _sx = self.get_x()
        _sy = self.get_y()
        _ex = 0
        self._row_end_x = self._row_end_x + _col_width
        _lines = self.multi_cell(_col_width, _lh, _val, border=0, align=_align, fill=_fill, split_only=True,
                        new_x=_new_x, new_y=_new_y, max_line_height=self.font_size, )
        # print(self._debug_name + '._draw_table_bcell->_lines: ', _lines)
        _ex = self.get_x() + _col_width
        _len_lines = len(_lines)
        if 1 == _len_lines:
            _ch = len(_lines) * line_height + 1
        else:
            _ch = len(_lines) * self.font_size-1
        _ey = self.get_y() + self._cur_process_sizes['h']

        # self.multi_cell(_col_width, _lh, _val, border=0, align=_align, fill=_fill,
        #                 new_x=_new_x, new_y=_new_y, max_line_height=self.font_size)
        self.multi_cell(_col_width, self._cur_process_sizes['h'], _val, border=0, align=_align, fill=_fill,
                        new_x=_new_x, new_y=_new_y, max_line_height=_lh)

        # print(self._debug_name + '._draw_table_bcell->get_y() after cell: ', self.get_y())

        if _ey > self._row_end_y:
            self._row_end_y = _ey
        if self._last_tbl_cell:
            self.ln(_lh)
            self._last_tbl_cell = False# last cell
        return (_sx, _sy, _ex, _ey)

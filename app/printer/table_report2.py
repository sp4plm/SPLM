# -*- coding: utf-8 -*-
import os
from datetime import datetime
from fpdf import XPos, YPos, FPDFException
from .document_fpdf import DocumentFpdf
from fpdf.table import FontFace


class TableReport2(DocumentFpdf):
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

        self._header_color = (0,0,0)  # table header text color
        self._header_bgcolor = (255,255,255)  # table header background color
        self._repeat_header = True

    def set_repeat_header(self, _flg):
        if isinstance(_flg, bool):
            self._repeat_header = _flg

    def set_header_color(self, _rgb_tuple):
        if _rgb_tuple and isinstance(_rgb_tuple, tuple) and 3 == len(_rgb_tuple):
            self._header_color = _rgb_tuple

    def set_header_bgcolor(self, _rgb_tuple):
        if _rgb_tuple and isinstance(_rgb_tuple, tuple) and 3 == len(_rgb_tuple):
            self._header_bgcolor = _rgb_tuple

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

    def set_data(self, _data):
        """"""
        if not isinstance(_data, list):
            raise TypeError(_data)
        self._data = _data

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
            self.set_auto_page_break(True, self._footer_height)
            """
            по идее каждая строка должна представлять собой список словарей
            каждый словарь - описание одной ячейки, обязательный ключ -> 'value'
            {'value': '', 'font-size': 12, 'color': '', 'bgcolor': '', 'font-style': 'IBU', 'align': 'LCR',
            'width':0, height: 0, 'border': 1
            }
            """
            # для начала разберемся с заголовками - первая строка в дата
            _work = self._data
            _headers = _work[0]
            self.set_font("DejaVuSans", "", 12)

            _header_conf = {}
            _header_conf['color'] = self._header_color  # (0, 0, 0)
            _header_conf['fill_color'] = self._header_bgcolor  # (208, 240, 142)
            _header_conf['emphasis'] = 'BOLD'

            _tbl_conf = {}
            _tbl_conf['text_align'] ="CENTER"
            _tbl_conf['headings_style'] = FontFace(**_header_conf)
            # _tbl_conf['borders_layout'] = "INTERNAL"
            # set column width in percentages - 1%
            # надо подумать как вычислять или подставлять из конфигурации
            # _tbl_conf['col_widths'] = (15, 53, 15, 17)  # col_widths=(30, 30, 10, 30)
            _data_row = False
            _tbl_conf['first_row_as_headings'] = self._repeat_header
            with self.table(**_tbl_conf) as _tbl:
                _r_ind = 0
                for _dr in self._data:
                    row = _tbl.row()
                    _c_ind = 0
                    for _dc in _dr:
                        _is_image = False
                        _c_cfg = {}
                        _c_cfg['text'] = _dc['value']
                        if not self._repeat_header and 0 == _r_ind:
                            _c_cfg['align'] = 'CENTER'
                            _c_cfg['style'] = FontFace(**_header_conf)
                        if _is_image:
                            _c_cfg['img'] = _dc['value']
                            _c_cfg['img_fill_with'] = ''
                        # _c_cfg['colspan'] = 1
                        # первая колонка является
                        if 0 == _c_ind and _r_ind > 0:
                            _c_cfg['align'] = 'LEFT'
                        row.cell(**_c_cfg)
                        _c_ind += 1
                    _r_ind += 1

# -*- coding: utf-8 -*-

from datetime import datetime
from .document_fpdf import DocumentFpdf


class Report(DocumentFpdf):
    _class_file = __file__
    _debug_name = 'PrinterReport'

    def __init__(self):
        DocumentFpdf.__init__(self)
        # self._main_title = ''
        # self._project_name = ''
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

    def set_header_color(self, _rgb_tuple):
        if _rgb_tuple and isinstance(_rgb_tuple, tuple) and 3 == len(_rgb_tuple):
            self._header_color = _rgb_tuple

    def set_header_bgcolor(self, _rgb_tuple):
        if _rgb_tuple and isinstance(_rgb_tuple, tuple) and 3 == len(_rgb_tuple):
            self._header_bgcolor = _rgb_tuple

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

    def _add_conf(self):
        self.set_text_color(0)
        if not self.pages:
            self.add_page(orientation=self._report_orientation, format=self._report_format)
        self.set_font("DejaVuSans", "", 12)

    def _compile_content(self):
        self._add_conf()
        if self._html:
            self.write_html(self._html)

# -*- coding: utf-8 -*-
import os
from datetime import datetime
from fpdf import FPDF, HTML2FPDF, HTMLMixin, FPDF_VERSION

import PyPDF2


class DocumentFpdf(FPDF, HTMLMixin):
    _class_file = __file__
    _debug_name = 'PrinterDocumentFpdf'
    _fonts_src_name = 'fonts'
    _temps_dir_name = '_tmp'
    lib_version = float('.'.join([FPDF_VERSION.split('.')[0],FPDF_VERSION.split('.')[1]]))

    def __init__(self,
        orientation="portrait",
        unit="mm",
        format="A4"
    ):
        FPDF.__init__(self, orientation, unit, format)
        # print(self._debug_name + '.__init__->call()')
        self._main_title = 'Документ'
        self._init_fonts()
        self._logo_1 = ''
        self._logo_2 = ''
        self._sing = ''
        _now = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        self._filename = 'pdf_' + str(_now) + '.pdf'
        self._gen_sing(_now)
        # print(self._debug_name + '._init_ -> self.fonts', self.fonts.keys())
        self._watermark = ''
        self._default_font_fam = 'DejaVuSans'  # шрифты поддерживающие кирилический unicode
        self._default_font_size = 12  # pt
        self._footer_height = 15


    @staticmethod
    def hex2rgb(_hex):
        _hex = _hex.lstrip('#')
        _rgb = tuple(int(_hex[i:i+2], 16) for i in (0, 2, 4))
        return _rgb

    def print(self, _to):
        """
        Метод создает pdf документ по указанному пути _to
        :param _to: полное имя файла для вывода(сохранения)
        :return:
        """
        # print(self._debug_name + '.print->_to:', _to)
        self._compile_content()
        if os.path.exists(self._watermark):
            self.__apply_watermark(_to)
        else:
            self.output(_to)

    def stream(self):
        _tmp = self.__gen_temp_file()
        self.print(_tmp)
        _file_bites = None
        with open(_tmp, 'rb') as _fp:
            _file_bites = _fp
        os.unlink(_tmp)
        return _file_bites

    def set_document_title(self, title):
        if title:
            self._main_title = str(title)

    def set_watermark(self, _pth):
        self._watermark = str(_pth)  # ожидаем путь к файлу

    def __create_watermark(self):
        _cur_orient = self.cur_orientation[0].lower()
        _cur_format = 'A4'
        _pth = ''
        _name = os.path.basename(self._watermark)
        _name += _cur_format + _cur_orient
        _pth = os.path.join(self.__get_tmp_dir(), _name + '.pdf')
        if not os.path.exists(_pth):
            from .watermark_fpdf import WatermarkFpdf
            _my_watermark = WatermarkFpdf()
            _my_watermark.set_page_orientation(_cur_orient)
            _my_watermark.set_page_format(_cur_format)
            _my_watermark.set_background(self._watermark)
            # _my_watermark.set_image_opacity(0.2)
            _watermark = _my_watermark.print(_pth)
        return _pth

    def __apply_watermark(self, _to):
        # надо знать текущий page orientation
        # print(self._debug_name + '.__apply_watermark -> current orientation: ', self.cur_orientation)
        _watermark_pth = self.__create_watermark()
        # теперь надо создать временный файл с данными
        _tmp = ''
        _tmp = self.__gen_temp_file()
        self.output(_tmp)  # сбрасываем текущий контент в файл - create tempory content
        _text_f = open(_tmp, 'rb')
        _text = PyPDF2.PdfFileReader(_text_f)
        _water_f = open(_watermark_pth, 'rb')
        _watermark = PyPDF2.PdfFileReader(_water_f)
        pages_cnt = len(_text.pages)
        # print('count text pages: ', pages_cnt)
        _printer = PyPDF2.PdfFileWriter()
        for _pn in range(0, pages_cnt):
            # print('page num -> ', _pn)
            _cur_page = _text.pages[_pn]
            # print('_cur_page -> ', _cur_page)
            # print('_cur_page type -> ', type(_cur_page))
            _cur_page.merge_page(_watermark.pages[0])
            if _cur_page:
                _printer.add_page(_cur_page)

        with open(_to, 'wb') as _fp:
            _printer.write(_fp)

        _water_f.close()
        _text_f.close()
        os.unlink(_tmp)  # remove tempory content

    def _compile_content(self):
        # print(self._debug_name + '.__compile_content->start')
        # print(self._debug_name + '.__compile_content->self', type(self))
        pass

    def __gen_temp_file(self):
        _root = self.__get_tmp_dir()
        _filename = ''
        _filename = '_' + str(datetime.now().timestamp()) + '.tmp'
        _file = os.path.join(_root, _filename)
        return _file

    def __get_tmp_dir(self):
        _root = os.path.dirname(__file__)
        _pth = os.path.join(_root, self._temps_dir_name)
        if not os.path.exists(_pth):
            try: os.mkdir(_pth)
            except: pass
        return _pth

    def header(self):
        logo_margin_top = 8
        self.set_text_color(0)
        # print('epw -> ', str(self.epw))
        w1, w2 = self._px2mm(60), self._px2mm(140)
        # так как размеры логотипов разные, то надо автоматизировать вычиление коэффециентов
        # чтобы логотипы находились на границе 1 и 2 для первого лого и на границе 3 и 4 для воторого лого четвертей
        # print('1 logo width -> ', str(w1))
        # print('2 logo width -> ', str(w2))
        pic1_m = self._px2mm(30)
        # print('half for 1 logo -> ', str(pic1_m))
        pic2_m = self._px2mm(140)
        # print('half for 2 logo -> ', str(pic2_m))
        _q = self.epw/4
        # print('1/4 of epw -> ', str(_q))
        x1 = _q-pic1_m +15
        # print('x1 start for 1 logo -> ', str(x1))
        x2 = _q*3-pic2_m + 20
        # print('x2 start for 2 logo -> ', str(x2))
        if os.path.exists(self._logo_1):
            self.image(self._logo_1, w=w1, x=x1, y=logo_margin_top)
        if os.path.exists(self._logo_2):
            self.image(self._logo_2, w=w2, x=x2, y=logo_margin_top)
        self.ln(20)

    def footer(self):
        self.set_text_color(0)
        # Position cursor at 1.5 cm from bottom:
        _use_pos = 0 - self._footer_height
        self.set_y(_use_pos)
        # Setting font: helvetica italic 8
        # self.set_font("helvetica", "I", 8)
        self.set_font('DejaVuSans', '', 8)
        _code = self._get_data_sign()
        # print(self._debug_name + '.footer->_code', _code)
        self.cell(0, 10, f"Код отчёта: " + _code, 'T:2,B:1', align="L")
        # Moving cursor to the right:
        # self.cell(80)
        self.cell(0, 10, f"Страница: {self.page_no()} из {{nb}}", 'T:2,B:1', align="R")

    def _get_data_sign(self):
        if '' == self._sing:
            self._gen_sing()
        return self._sing

    def _gen_sing(self, base=''):
        if '' == base:
            base = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        from hashlib import sha256
        self._sing = sha256(base.encode('UTF-8')).hexdigest()

    def set_logo_1(self, pth):
        if os.path.exists(pth):
            self._logo_1 = pth

    def set_logo_2(self, pth):
        if os.path.exists(pth):
            self._logo_2 = pth

    def _init_fonts(self):
        # обязательно добавлять все 4 стиля шрифта, так как в html может быть любой
        family = 'DejaVuSans'
        style = ''
        fontkey = f"{family.lower()}{style}"
        # print(self._debug_name + '._init_fonts()')
        # print(self._debug_name + '._init_fonts -> self', self)
        if not fontkey in self.fonts:
            # print(self._debug_name + '._init_fonts -> try ad font:', fontkey)
            self.add_font(family, '', self._get_font('DejaVuSansCondensed.ttf'))
        style = 'B'
        fontkey = f"{family.lower()}{style}"
        if not fontkey in self.fonts:
            self.add_font(family, 'B', self._get_font('DejaVuSansCondensed-Bold.ttf'))
        style = 'I'
        fontkey = f"{family.lower()}{style}"
        if not fontkey in self.fonts:
            self.add_font(family, 'I', self._get_font('DejaVuSansCondensed-Oblique.ttf'))
        style = 'BI'
        fontkey = f"{family.lower()}{style}"
        if not fontkey in self.fonts:
            self.add_font(family, 'BI', self._get_font('DejaVuSansCondensed-BoldOblique.ttf'))

    def _get_font(self, file):
        _font_root = self._get_fonts_dir()
        _font = os.path.join(_font_root, file)
        return _font

    def _get_fonts_dir(self):
        _pth = os.path.dirname(self._class_file)
        _pth = os.path.join(_pth, self._fonts_src_name)
        return _pth

    def _px2mm(self, px=0):
        return float(px*0.264583)

    def _mm2px(self, mm=0):
        return float(mm*3.793627)

    def hex_to_rgb(self, value):
        """Return (red, green, blue) for the color given as #rrggbb."""
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

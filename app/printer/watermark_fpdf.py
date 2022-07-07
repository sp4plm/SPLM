# -*- coding: utf-8 -*-
import os
from fpdf import FPDF
from PIL import Image


class WatermarkFpdf():
    _class_file = __file__
    _debug_name = 'PrinterWatermarkFpdf'

    def __init__(self):
        self._driver = FPDF()
        self._opacity = 0.04
        self._iw = self._driver.epw
        self._image = ''
        self._page_orientation = 'p'
        self._page_format = 'A4'

    def _px2mm(self, px=0):
        return float(px*0.264583)

    def _mm2px(self, mm=0):
        return float(mm*3.793627)

    def set_background(self, _pth):
        if not os.path.exists(_pth):
            raise FileNotFoundError(_pth)
        self._image = _pth

    def set_image_opacity(self, val):
        if 0 > val:
            val = 0
        if 1 < val:
            # наверно надо разделить и сделать меньше 1
            val = 1
        self._opacity = float(val)

    def set_page_orientation(self, _orientation):
        self._page_orientation = 'p'  # portrait
        if 'p' == _orientation:
            self._page_orientation = _orientation
        if 'l' == _orientation:
            self._page_orientation = _orientation

    def set_page_format(self, _format):
        self._page_format = 'A4'

    def __compile_content(self):
        self._driver.set_auto_page_break(False)  # создаем одну страничку
        self._driver.add_page(orientation=self._page_orientation, format=self._page_format)
        _niw = 0
        # размер по узкой части
        _base_w = self._driver.epw
        if self._driver.epw < self._driver.eph:
            _base_w = self._driver.epw
        if self._driver.eph < self._driver.epw:
            _base_w = self._driver.eph
        # print(self._debug_name + '.__compile_content->_base_w:', _base_w)
        self._iw = _base_w*0.9  # после сброса отступов надо обновить
        self._driver.set_margin(0)
        _iy = 0
        _ix = 10
        if '' == self._image:
            self._image = os.path.join(os.path.dirname(__file__), 'images/logo.png')
        # print(self._debug_name + '.__compile_content->self._image:', self._image)
        if os.path.exists(self._image):
            # print(self._debug_name + '.__compile_content->self._iw:', self._iw, type(self._iw))
            # print(self._debug_name + '.__compile_content->self._driver.t_margin:', self._driver.t_margin, type(self._driver.t_margin))
            # print(self._debug_name + '.__compile_content->self._driver.r_margin:', self._driver.r_margin, type(self._driver.r_margin))
            # print(self._debug_name + '.__compile_content->self._driver.b_margin:', self._driver.b_margin, type(self._driver.b_margin))
            # print(self._debug_name + '.__compile_content->self._driver.l_margin:', self._driver.l_margin, type(self._driver.l_margin))
            _image = Image.open(self._image)
            _iw, _ih = _image.size
            # print(self._debug_name + '.__compile_content->self._driver.epw:', self._driver.epw, type(self._driver.epw))
            # print(self._debug_name + '.__compile_content->self._mm2px(self._driver.epw):', self._mm2px(self._driver.epw), type(self._mm2px(self._driver.epw)))
            # print(self._debug_name + '.__compile_content->self._driver.eph:', self._driver.eph, type(self._driver.eph))
            # print(self._debug_name + '.__compile_content->_iw:', _iw, type(_iw))
            # print(self._debug_name + '.__compile_content->_ih:', _ih, type(_ih))
            _img_new_w = int(self._mm2px(self._iw))
            # print(self._debug_name + '.__compile_content->_img_new_w:', _img_new_w, type(_img_new_w))
            _iw_ration = (_img_new_w/float(_iw))
            _img_new_h = int(float(_ih) * float(_iw_ration))
            # print(self._debug_name + '.__compile_content->_img_new_h:', _img_new_h, type(_img_new_h))
            _ix = int((self._driver.epw-self._px2mm(_img_new_w))/2)
            _ix = 0
            _iy = int((self._driver.eph-self._px2mm(_img_new_h))/2)
            _new_img = _image.resize((_img_new_w, _img_new_h), )
            with self._driver.local_context(fill_opacity=self._opacity):
                # print(self._debug_name + '.__compile_content->self._image:', self._image)
                # print(self._debug_name + '.__compile_content->_img_new_h:', _img_new_h)
                # print(self._debug_name + '.__compile_content->_ix:', _ix)
                # print(self._debug_name + '.__compile_content->_iy:', _iy)
                self._driver.image(self._image, w=self._driver.epw, x=_ix, y=_iy-10)
                # self._driver.image(_new_img, x=_ix, y=_iy)

    def print(self, _to):
        """
        Метод создает pdf документ по указанному пути _to
        :param _to: полное имя файла для вывода(сохранения)
        :return:
        """
        # print(self._debug_name + '.print->_to:', _to)
        self.__compile_content()
        self._driver.output(_to)

    def stream(self):
        self.__compile_content()
        return self._driver.output()

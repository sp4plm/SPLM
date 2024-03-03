# -*- coding: utf-8 -*-
from app.admin_mgt.admin_conf import AdminConf
from app.drivers.store_manager import StoreManager
from app.utilites.some_config import SomeConfig


class Utilites:

    @staticmethod
    def get_storage_driver():
        """
        Метод возвращает драйвер для работы с хранилищем

        :return: _driver
        """
        app_cfg = SomeConfig(AdminConf.get_configs_path())
        _endpoint = app_cfg.get("data_storages.EndPoints.main")
        _driver_name = app_cfg.get("data_storages.Drivers.main")
        _driver = None
        if '' == _driver_name:
            _driver_name = app_cfg.get("data_storages.Main.default_driver")
        if '' == _driver_name:
            raise Exception('Undefined store driver name -> "{}"!' . format(_driver_name))
        try:
            _driver = StoreManager.get_driver(_driver_name)
            _driver.set_endpoint(_endpoint)
        except Exception as ex:
            raise ex
        return _driver

    @staticmethod
    def get_file_editor():
        from app.kv_editor.mod_api import ModApi
        editor_api = ModApi()
        return editor_api

    @staticmethod
    def create_xicon_block(html='', title='', id='', xicon_close=True):
        """
        Метод создает html-блок с возможностью скрытия +/-

        :param str html: содержимое html блока
        :param str title: заголовок html блока
        :param str id: id html блока
        :param bool xicon_close: тип блока скрытый/раскрытый - True/False (по умолчанию скрытый)
        :return: html
        """
        xicon = "close" if xicon_close else "open"
        xicon_block = '''<div>
            <span class="header-section-toggler xicon-''' + xicon + ''' xicon-pos">&nbsp;</span>
            <h3 id="''' + id + '''" class="content-header">''' + title + '''</h3>''' + html + '''
        </div>'''
        return xicon_block

    @staticmethod
    def make_qrcode(url):
        import io
        import qrcode
        import base64

        qr = qrcode.QRCode(version=None,
                           error_correction=qrcode.constants.ERROR_CORRECT_L,
                           box_size=16,
                           border=2, )
        qr.add_data(url)
        qr.make(fit=True)
        buf = io.BytesIO()

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(buf)
        buf.seek(0)
        file = base64.b64encode(buf.getvalue()).decode("ascii")
        result = f"<img src='data:image/png;base64,{file}' width='200px' style='max-width: 200px !important; padding:20px'/>"

        return result

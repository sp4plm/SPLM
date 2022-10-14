# -*- coding: utf-8 -*-
import os
import json
import configparser
from shutil import rmtree

from time import time, strftime, localtime

from app.utilites.code_helper import CodeHelper
from app.utilites.jqgrid_helper import JQGridHelper


class ModUtils(object):
    _class_file = __file__
    _debug_name = 'PortaldataUtils'

    def __init__(self):
        pass

    def drop_publishing_pid_file(self):
        _flg = False
        _file = self.get_publishing_pid_file()
        if os.path.exists(_file):
            os.unlink(_file)
            _flg = not os.path.exists(_file)
        return _flg

    def set_publishing_pid(self, _pid):
        _file = self.get_publishing_pid_file()
        _flg = False
        if _file and not os.path.exists(_file):
            with open(_file, 'w', encoding='utf-8') as file_p:
                file_p.write('')
        with open(_file, 'w', encoding='utf-8') as file_p:
            file_p.write(str(_pid))
            _flg = True
        return _flg

    def get_publishing_pid(self):
        _file = self.get_publishing_pid_file()
        _pid = ''
        if os.path.exists(_file):
            with open(_file, 'r', encoding='utf-8') as file_p:
                _pid = file_p.read()
        return _pid

    def get_publishing_pid_file(self):
        _pth = ''
        try:
            _cfg = self.get_config()
            pid_name = ''
            pid_name = _cfg['Main']['publish_pid']
            from app import app_api
            _pth = app_api.get_mod_data_path(self.get_mod_name())
            _pth = os.path.join(_pth, pid_name)
        except Exception as ex:
            _pth = ''
            print(self._debug_name + '.get_publishing_pid_file.Exception: ' + str(ex))
        return _pth

    def get_publish_result_file(self):
        _cfg = self.get_config()
        from app import app_api
        _pth = app_api.get_mod_data_path(self.get_mod_name())
        _pth = os.path.join(_pth, _cfg['Main']['publishResultFile'])
        return _pth

    def get_navi(self, _user):
        _lst = self._get_navi_data()
        _navi = []
        if _lst:
            _web_pref = self.get_web_prefix()
            for _li in _lst:
                _miss = False
                if '' != _li['roles']:
                    _miss = True
                    if _user is not None:
                        _rl = _li['roles'].split(',')
                        # судя по реализации метод has_role использует теорию множеств - включает в себя
                        if _user.has_role(_rl):
                            _miss = False
                        # for _r in _li['roles'].split(','):
                        #     if _user.has_role(_r):
                        #         _miss = False
                if _miss:
                    continue
                if '/' != _li['href'][0]:
                    _li['href'] = _web_pref + '/' + _li['href']
                _navi.append(_li)
        return _navi

    def get_sections(self): pass

    def get_jqgrid_config(self):
        return JQGridHelper.get_jqgrid_config()

    def get_config(self):
        _file = self.get_config_file()
        _ini_parser = configparser.ConfigParser(inline_comment_prefixes=(';',))
        # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
        _ini_parser.optionxform = str
        _ini_parser.read(_file, encoding='utf8')
        _cfg = {}
        _cfg = _ini_parser
        if _cfg:
            """Теперь возьмем системные настройки по использованию именных графов"""
            from app import app_api
            _app_conf = app_api.get_app_config()
            _cfg['Main']['use_named_graphs'] = _app_conf.get('data_storages.Main.use_named_graphs')
        return _cfg

    def get_config_file(self):
        _root = self.get_cfg_path()
        _pth = os.path.join(_root, 'module.ini')
        return _pth

    def _get_navi_data(self):
        _pth = self.get_navi_file()
        _data = []
        if os.path.exists(_pth):
            with open(_pth, 'r', encoding='utf-8') as fp:
                try:
                    _data = json.load(fp)
                except Exception as ex:
                    print(self._debug_name + '.get_navi_data->Exception:', ex.args)
        return _data

    def get_navi_file(self):
        _root = self.get_cfg_path()
        _pth = os.path.join(_root, 'navi.json')
        return _pth

    def get_cfg_path(self):
        _root = self.get_mod_path()
        _pth = os.path.join(_root, '_cfg')
        return _pth

    def get_web_static_path(self):
        _root = self.get_mod_path()
        _pth = os.path.join(_root, 'static')
        return _pth

    def get_web_tpl_path(self):
        _root = self.get_mod_path()
        _pth = os.path.join(_root, 'templates')
        return _pth

    def get_mod_path(self):
        _pth = os.path.dirname(self._class_file)
        return _pth

    def get_mod_name(self):
        _pth = self.get_mod_path()
        _name = os.path.basename(_pth)
        return _name

    def get_web_prefix(self):
        _name = self.get_mod_name()
        _pref = '/' + _name.replace('_', '')
        return _pref

    def get_portal_mode_name(self):
        _name = 'publish'
        return _name

    def save_uploaded_file(self, http_file, file_name=''):
        flg = False
        if http_file:
            work_file = file_name
            if not os.path.exists(work_file):
                http_file.save(work_file)
                flg = True
        return flg

    def normalize_file_name(self, file_name):
        res = file_name
        res = '_'.join(res.split(' '))
        res = self.translit_rus_string(res)
        return res

    def reqform_2_dict(self, reqform):
        """"""
        _data = reqform.to_dict(flat=False)
        _normalized = {}
        for key in _data:
            """"""
            _pos = key.find('[')
            origin = ''
            _struct_k = ''
            _struct = None
            if -1 < _pos:
                """"""
                origin = key[:_pos]
                _struct_k = key[_pos-1:]
            else:
                _pos = key.find('{')
                if -1 < _pos:
                    origin = key[:_pos]
                    _struct_k = key[_pos - 1:]
                else:
                    origin = key
            if origin not in _normalized:
                _normalized[origin] = None
                #теперь надо создать структуру по ключу
        _normalized = _data
        return _normalized

    def translit_rus_string(self, ru_str):
        res = CodeHelper.translit_rus_string(ru_str)
        return res

    def is_empty_upload_temp(self, _check_path):
        if CodeHelper.check_dir(_check_path):
            file_map = 'set_map'
            files = CodeHelper.get_dir_content(_check_path)
            if 1 < len(files):
                return False
            catch_map = False
            if 1 == len(files):
                if file_map == files[0]:
                    catch_map = True
                if catch_map:
                    return True # файл но поскольку это файл карты то считаем пустой
                else:
                    return False # файл но не файл карты
            return True
        CodeHelper.is_empty_dir(_check_path) # запускаем исключение

    def clear_upload_temp(self, _check_path):
        if CodeHelper.check_dir(_check_path) and CodeHelper.is_empty_dir(_check_path):
            rmtree(_check_path)  # удаляем ненужную директорию

    def get_dt_from_filename(self, filename):
        """"""
        pdt = {'y': 0, 'mon': 0, 'd': 0, 'h': 0, 'min': 0, 's': 0}
        try_time = filename.replace('backup_', '')
        try_time = try_time.replace('-.ttl', '')

        a = try_time.split('_')
        # Y,Y,Y,Y,M,M,D,D
        # 0,1,2,3,4,5,6,7
        pdt['y'] = int(a[0][0:4])
        pdt['mon'] = int(a[0][4:6])
        pdt['d'] = int(a[0][6:])
        b = a[1].split('-')
        pdt['h'] = int(b[0])
        pdt['min'] = int(b[1])
        pdt['s'] = int(b[2])
        return pdt

    def get_tags_4_adddir(self):
        _tags = [{'tag': 'img', 'attribute': 'src'}]
        return _tags

    def get_mod_data_path(self):
        _name = self.get_mod_name()
        _pth = ''
        from app import app_api
        _pth = app_api.get_mod_data_path(_name)
        return _pth

    def get_section_cols(self, _sec):
        _fields = []
        _fields.append({'name': 'name', 'type': 'TEXT', 'default': ''})
        _fields.append({'name': 'mdate', 'type': 'TEXT', 'default': ''})
        if 'backups' == _sec:
            _fields.append({'name': 'comment', 'type': 'TEXT', 'default': ''})
        if 'data' == _sec:
            _fields.append({'name': 'result', 'type': 'TEXT', 'default': ''})
            _fields.append({'name': 'map', 'type': 'TEXT', 'default': ''})
        if 'res' == _sec:
            _fields.append({'name': 'deleted', 'type': 'INTEGER', 'default': 0})
        if 'maps' == _sec:
            _fields.append({'name': 'active', 'type': 'INTEGER', 'default': 0})
        if 'ontos' == _sec:
            _fields.append({'name': 'fullname', 'type': 'TEXT', 'default': ''})
            _fields.append({'name': 'result', 'type': 'TEXT', 'default': ''})
            _fields.append({'name': 'prefix', 'type': 'TEXT', 'default': ''})
        return _fields

    def get_tools_navi(self, _user):
        _lst = self._get_tools_navi_data()
        _navi = []
        if _lst:
            _web_pref = self.get_web_prefix()
            for _li in _lst:
                _miss = False
                if '' != _li['roles']:
                    _miss = True
                    if _user is not None:
                        _rl = _li['roles'].split(',')
                        # судя по реализации метод has_role использует теорию множеств - включает в себя
                        if _user.has_role(_rl):
                            _miss = False
                        # for _r in _li['roles'].split(','):
                        #     if _user.has_role(_r):
                        #         _miss = False
                if _miss:
                    continue
                if '/' != _li['href'][0]:
                    _li['href'] = _web_pref + '/' + _li['href']
                _navi.append(_li)
        return _navi

    def _get_tools_navi_data(self):
        _data = None
        _pth = self.get_tools_navi_file()
        _data = []
        if os.path.exists(_pth):
            with open(_pth, 'r', encoding='utf-8') as fp:
                try:
                    _data = json.load(fp)
                except Exception as ex:
                    print(self._debug_name + '._get_tools_navi_data->Exception:', ex.args)
        return _data

    def get_tools_navi_file(self):
        _root = self.get_cfg_path()
        _pth = os.path.join(_root, 'tools.json')
        return _pth

    def formated_time_mark(self, _tpl='%Y%m%d_%H-%M-%S'):
        return strftime(_tpl, localtime(time()))

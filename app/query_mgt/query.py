# -*- coding: utf-8 -*-
import json
import multiline
import os
import logging

from app import app
from app.utilites.utilites import Utilites

from app.drivers.store_driver import StoreDriver

from rdflib import Graph
from rdflib.plugins.sparql.results.jsonresults import JSONResult

# module = "query_mgt"

class Query:
    """
    Класс Query работает с запросам к triplestore
    """

    LOG_DIR = os.path.join(app.config['APP_DATA_PATH'], "logs")
    if not os.path.exists(LOG_DIR):
        try: os.mkdir(LOG_DIR)
        except: pass

    LOG_FILE = os.path.join(LOG_DIR, "Query.log")

    format_json = ".sparqt"

    # SPARQT_DIR = ""
    # TEMPLATE_PARAMS = ['_CMT_', '#VARS', '#TXT']

    def __init__(self):
        """
        Метод инициализирует класс Query. Определяет драйвер для обращения к хранилищу.
        Инициализирует логгер.

        :param str module_name: название модуля.
        """
        self.storage_driver = None

        self.logger = self.initLoggerComponent().getAppLogger()

        try:
            self.storage_driver = Utilites.get_storage_driver()

            # if module_name:
            #     from app.app_api import get_module_sparqt_dir
            #     self.SPARQT_DIR = get_module_sparqt_dir(module_name)
            #
            #     if not os.path.exists(self.SPARQT_DIR):
            #         os.mkdir(self.SPARQT_DIR)
        except:
            pass

    # logger
    def initLoggerComponent(self):
        """
        Метод возвращает класс logComponent для инициализации и поддержки функции логирования методов основного класса

        :return: logComponent
        """
        class logComponent:
            @staticmethod
            def getAppLogger(name: str = ''):
                log_name = 'Query'
                if '' != name:
                    log_name += '.' + name
                logger = logging.getLogger(log_name)
                logger.setLevel(logging.DEBUG)
                file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), self.LOG_FILE), 'w', 'utf-8')
                file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
                logger.addHandler(file_handler)
                return logger
        return logComponent

    # main function
    def runQuery(self, _query):
        """
        Метод выполняет post запрос к триплстору
        :param str _query: текст запроса

        :return _result: результат sparql запроса/строка с ошибкой
        :rtype: dict/str
        """
        _result = None
        response = None
        try:
            response = self.storage_driver._exec_query(_query)
        except Exception as e:
            _result =  "Request error: " + str(e)
            self.logger.error(_result)
            return _result
            
        try:
            _result = json.loads(response)
        except Exception as e:
            _result = "JSON.loads error: " + str(e) + "\n" + "Response: " + str(response)
            self.logger.error(_result)

        return _result

    def compileQueryResult(self, answer):
        """
        Метод обрабатывает результат запроса, приводя его к более удобному виду
        :param dict answer: результат sparql запроса

        :return FINAL_RESULT: обработанный результат запроса
        :rtype: list
        """
        try:
            FINAL_RESULT = []
            for binding_set in answer['results']['bindings']:
                FINAL_RESULT.append(
                    {var_name: binding_set[var_name]['value'] if var_name in binding_set else "" for var_name in
                     answer['head']['vars']}
                 )

            return FINAL_RESULT

        except Exception as e:
            return str(e)

    def query(self, _query):
        """
        Общий метод работы с запросами.
        В случае select запроса возвращает обработанный Python.List, в случае construct возвращает rdflib.Graph
        :param str _query: текст запроса

        :return FINAL_RESULT: результат
        :rtype: dict
        """
        FINAL_RESULT = []
        if not _query:
            return []

        try:
            answer = self.runQuery(_query)
            if isinstance(answer, str):
                return answer

            FINAL_RESULT = answer
            if StoreDriver()._is_select_query(_query):
                FINAL_RESULT = self.compileQueryResult(answer)
            if StoreDriver()._is_construct_query(_query):
                FINAL_RESULT = Graph()
                js = JSONResult(answer)
                for i in js:
                    FINAL_RESULT.add(i[:3])

        except Exception as e:
            return str(e)

        return FINAL_RESULT

    def compileQuery(self, code, params = {}):
        """
        Метод парсит код sparqt, компилирирует текст запроса и возвращает ответ от метода query
        :param str code: код запроса в формате <module>.<file>.<template>
        :param dict params: параметры для переменных в запросе в формате {VARNAME : VALUE}

        :return _query: текст запроса
        :rtype: str
        """
        try:
            from app.app_api import get_module_sparqt_dir

            delimeter = "."
            module, file, key_in_file = code.split(delimeter)

            self.SPARQT_DATA_PATH = get_module_sparqt_dir(module)
            _src_file = os.path.join(self.SPARQT_DATA_PATH, file + self.format_json)
            _src_file = self.__get_real_qfile(_src_file)
            input_json = open(_src_file, "r", encoding="utf-8")

            content = multiline.load(input_json, multiline=True)

            _txt = content[key_in_file]["#TXT"]
            _vars = content[key_in_file]["#VARS"]

            for item in _vars:
                pattern = _vars[item]['mark']
                if item in params and params[item] is not None:
                    _txt = _txt.replace(pattern, params[item])
                else:
                    _txt = _txt.replace(pattern, _vars[item]['default'])

            _query = _txt

            return _query
        except Exception as e:
            return str(e)

    def queryByCode(self, code, params={}):
        """
        Метод парсит код sparqt, компилирирует текст запроса и возвращает ответ от метода query
        :param str code: код запроса в формате <module>.<file>.<template>
        :param dict params: параметры для переменных в запросе в формате {VARNAME : VALUE}

        :return: результат запроса/ошибку
        :rtype: list/str
        """
        try:
            _query = self.compileQuery(code, params)
            return self.query(_query)
        except Exception as e:
            return str(e)

    def __get_real_qfile(self, file_path):
        """
        Метод возвращает путь до файла.
        Если файл редактируется впервые, то берется из ядра модуля.
        Если файл уже редактировался, то берется из cfg для пользователя

        :return _pth: фактический путь до sparqt-файла
        :rtype: str
        """
        _pth = file_path
        _root = self._get_app_root_dir()
        mod_name = file_path.replace(_root, '').lstrip(os.path.sep).split(os.path.sep)[0]
        _conf_path = self._get_app_conf_dir()
        if not file_path.startswith(_conf_path):
            _t = os.path.join(_conf_path, mod_name)
            if os.path.exists(_t):
                relative = file_path.replace(_root, '').lstrip(os.path.sep).replace(mod_name, '').lstrip(os.path.sep)
                _rp = os.path.join(_t, relative)
                if os.path.exists(_rp):
                    _pth = _rp
        return _pth

    @staticmethod
    def _get_app_conf_dir():
        """
        Метод возвращает полный путь до директории приложения с измененными конфигурационными файлами модулей (cfg)
        :return: путь до директории конфигурационных файлов
        """
        from app.app_api import get_app_cfg_path
        return get_app_cfg_path()

    @staticmethod
    def _get_app_root_dir():
        """
        Метод возвращает полный путь директории приложения
        :return: путь директории приложения
        """
        from app.app_api import get_app_root_dir
        return get_app_root_dir()
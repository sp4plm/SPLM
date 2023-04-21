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

module = "query_mgt"

class Query:
    """
    Класс Query работает с запросам к triplestore
    """

    LOG_DIR = os.path.join(app.config['APP_DATA_PATH'], "logs")
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    LOG_FILE = os.path.join(LOG_DIR, "Query.log")

    format_json = ".sparqt"

    SPARQT_DIR = ""
    TEMPLATE_PARAMS = ['_CMT_', '#VARS', '#TXT']

    def __init__(self, module_name = module):
        """
        Метод инициализирует класс Query. Определяет драйвер для обращения к хранилищу.
        Инициализирует логгер.

        :param str module_name: название модуля.
        """
        self.url = ""
        self.http_headers = ""
        self.namespaces = ""

        self.storage_driver = None

        self.logger = self.initLoggerComponent().getAppLogger()

        try:
            self.storage_driver = Utilites.get_storage_driver()

            if module_name:
                from app.app_api import get_module_sparqt_dir
                self.SPARQT_DIR = get_module_sparqt_dir(module_name)

                if not os.path.exists(self.SPARQT_DIR):
                    os.mkdir(self.SPARQT_DIR)
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
                file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), self.LOG_FILE), 'a', 'utf-8')
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

    def __get_real_qfile(self, file_path):
        """
        Метод возвращает путь до sparqt файла.
        Если файл редактируется впервые, то берется из ядра модуля.
        Если файл уже редактировался, то берется из cfg для пользователя

        :param file_path code: абсолютный путь до sparqt-файла из ядра модуля

        :return _pth: фактический путь до sparqt-файла
        :rtype: str
        """
        _pth = file_path
        _root = self.__get_app_root_dir()
        mod_name = file_path.replace(_root, '').lstrip(os.path.sep).split(os.path.sep)[0]
        _conf_path = self.__get_app_conf_dir()
        if not file_path.startswith(_conf_path):
            _t = os.path.join(_conf_path, mod_name)
            if os.path.exists(_t):
                relative = file_path.replace(_root, '').lstrip(os.path.sep).replace(mod_name, '').lstrip(os.path.sep)
                _rp = os.path.join(_t, relative)
                if os.path.exists(_rp):
                    _pth = _rp
        return _pth

    def __get_app_conf_dir(self):
        """
        Метод возвращает полный путь до директории приложения с измененными конфигурационными файлами модулей (cfg)
        :return: путь до директории конфигурационных файлов
        """
        from app.app_api import get_app_cfg_path
        return get_app_cfg_path()

    def __get_app_root_dir(self):
        """
        Метод возвращает полный путь директории приложения
        :return: путь директории приложения
        """
        from app.app_api import get_app_root_dir
        return get_app_root_dir()

    def queryByCode(self, code, params={}):
        """
        Метод парсит код sparqt, компилирирует текст запроса и возвращает ответ от метода query
        :param str code: код запроса в формате <module>.<file>.<template>
        :param dict params: параметры для переменных в запросе в формате {VARNAME : VALUE}

        :return: результат запроса
        :rtype: list
        """
        try:
            _query = self.compileQuery(code, params)
            return self.query(_query)
        except Exception as e:
            return str(e)

    def get_full_path_sparqt(self, file):
        """
        Метод возвращает абсолютный путь файла

        :param str file: название sparqt-файла без расширения.
        :return _pth: абсолютный путь до sparqt-файла
        :rtype: str
        """
        _pth = os.path.join(self.SPARQT_DIR, file + self.format_json)
        _pth = self.__get_real_qfile(_pth)
        return _pth

    def get_list_sparqt(self):
        """
        Метод возвращает список названий sparqt файлов без расширений

        :return files: список sparqt-файлов
        :rtype: list
        """
        files = []
        for file in os.listdir(self.SPARQT_DIR):
            if os.path.isfile(os.path.join(self.SPARQT_DIR, file)):
                files.append(os.path.splitext(file)[0])
        files.sort()
        return files

    def can_remove(self, file):
        """
        Метод проверяет можно ли удалять файл - то есть изначальный файл был отредактирован пользователем

        :param str file: название sparqt-файла без расширения.
        :return _flg: True/False
        :rtype: bool
        """
        _flg = False
        _pth = self.get_full_path_sparqt(file)
        _conf_path = self.__get_app_conf_dir()
        if _pth.startswith(_conf_path):
            _flg = True
        return _flg

    def can_remove_template(self, file, template):
        """
        Метод проверяет можно ли удалять шаблон - то есть изначальный шаблон был отредактирован пользователем

        :param str file: название sparqt-файла без расширения,
        :param str template: название шаблона в sparqt-файле file.
        :return _flg: True/False
        :rtype: bool
        """
        _flg = False
        _pth = self.get_full_path_sparqt(file)
        _conf_path = self.__get_app_conf_dir()
        if _pth.startswith(_conf_path):
            # получаем базовый путь файла
            base_path = os.path.join(self.SPARQT_DIR, file + self.format_json)
            base_templates = {}

            with open(base_path, "r", encoding="utf-8") as f:
                base_templates = multiline.load(f, multiline=True)

            if template in base_templates:
                base_tmpl = {}
                _obj = self.get_file_object_sparqt(file)
                if template in _obj:
                    if _obj[template] == base_templates[template]:
                        return False

            _flg = True
        return _flg

    def get_file_object_sparqt(self, file):
        """
        Метод возвращает содержимое sparqt файла

        :param str file: название sparqt-файла без расширения.
        :return templates: объект с шаблонами для текущего sparqt-файла
        :rtype: dict
        """
        templates = {}
        if not file:
            return {}

        with open(self.get_full_path_sparqt(file), "r", encoding="utf-8") as f:
            templates = multiline.load(f, multiline=True)

        return templates

    def edit_file_object_sparqt(self, file, templates):
        """
        Метод редактирует содержимое sparqt файла

        :param str file: название sparqt-файла без расширения,
        :param dict templates: объект с шаблонами для текущего sparqt-файла.

        """
        # согласно новой концепции сохранять редактируемый файл требуется в директорию общего конфига
        _conf_path = self.__get_app_conf_dir()  # директория конфигураций приложения
        _pth = self.get_full_path_sparqt(file)
        if not _pth.startswith(_conf_path):
            _root_path = self.__get_app_root_dir()
            relative = _pth.replace(_root_path, '').lstrip(os.path.sep).split(os.path.sep)
            #  принудительно заменяем путь сохранения
            _t = _conf_path
            for _s in relative:
                if _s == relative[-1]:
                    break
                _t += os.path.sep + _s
                if not os.path.exists(_t):
                    os.mkdir(_t)
            _pth = os.path.join(_t, relative[-1])
        with open(_pth, "w", encoding="utf-8") as f:
            json_text = json.dumps(templates, indent='\t', ensure_ascii=False)
            json_text = json_text.replace('\\n', '\n').replace('\\r', '')
            f.write(json_text)

    def delete_file_object_sparqt(self, file):
        """
        Метод удаляет sparqt-файл

        :param str file: название sparqt-файла без расширения.
        """
        if os.path.exists(self.get_full_path_sparqt(file)):
            os.remove(self.get_full_path_sparqt(file))

    def get_templates_names_sparqt(self, file):
        """
        Метод возвращает список названий шаблонов в sparqt-файле

        :param str file: название sparqt-файла без расширения.
        :return: список шаблонов
        :rtype: list
        """
        return list(self.get_file_object_sparqt(file).keys())


    def get_structure_codes_sparqt(self, file):
        """
        Метод возвращает список кодов запросов для sparqt-файла

        :param str file: название sparqt-файла без расширения.
        :return: список кодов запросов в формате <module>.<file>.<template>
        :rtype: list
        """
        return [module + "." + file + "." + key for key in self.get_templates_names_sparqt(file)]

    def get_template_sparqt(self, file, template_name):
        """
        Метод возвращает содержимое шаблона с ключом template_name в sparqt-файле file в формате Python.List

        :param str file: название sparqt-файла без расширения,
        :param str template_name: название шаблона.
        :return result: содержимое шаблона
        :rtype: list
        """
        if not template_name:
            return ["", "", ""]

        result = [self.get_file_object_sparqt(file)[template_name][item] for item in self.TEMPLATE_PARAMS]
        # #VARS
        # result[1] = json.dumps(result[1])

        var_s = ""
        for var in result[1]:
            var_s += var + "=" + result[1][var]['default']
            var_s += ","

        if var_s:
            var_s = var_s[:-1]

        result[1] = var_s

        return result

    def edit_template_sparqt(self, file, template_name, template_params):
        """
        Метод редактирует содержимое шаблона с ключом template_name в sparqt-файле file.

        :param str file: название sparqt-файла без расширения,
        :param str template_name: название шаблона,
        :param list template_params: новое содержимое шаблона
        """
        templates = self.get_file_object_sparqt(file)
        templates[template_name] = {self.TEMPLATE_PARAMS[i]: template_params[i] for i in range(0, len(template_params))}

        # #VARS
        if self.TEMPLATE_PARAMS[1] in templates[template_name]:

            var_s = templates[template_name][self.TEMPLATE_PARAMS[1]].split(",")
            dict_var_s = {}
            if templates[template_name][self.TEMPLATE_PARAMS[1]]:
                for var in var_s:
                    var = var.split("=")
                    dict_var_s[var[0]] = {"mark":"#{" + var[0] + "}","default": var[1]}

            templates[template_name][self.TEMPLATE_PARAMS[1]] = json.dumps(dict_var_s)

            templates[template_name][self.TEMPLATE_PARAMS[1]] = templates[template_name][self.TEMPLATE_PARAMS[1]].replace("\'", "\"")
            templates[template_name][self.TEMPLATE_PARAMS[1]] = json.loads(templates[template_name][self.TEMPLATE_PARAMS[1]])

        self.edit_file_object_sparqt(file, templates)

    def delete_template_sparqt(self, file, template):
        """
        Метод удаляет шаблон с ключом template в sparqt-файле file.

        :param str file: название sparqt-файла без расширения,
        :param str templat: название шаблона.
        """
        templates = self.get_file_object_sparqt(file)

        # удаляем изменения - получаем базовый шаблон
        base_path = os.path.join(self.SPARQT_DIR, file + self.format_json)
        base_templates = {}

        with open(base_path, "r", encoding="utf-8") as f:
            base_templates = multiline.load(f, multiline=True)

        if template in base_templates:
            templates[template] = base_templates[template]

        self.edit_file_object_sparqt(file, templates)

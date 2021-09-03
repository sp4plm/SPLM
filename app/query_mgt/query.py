# -*- coding: utf-8 -*-

import requests
import json
import multiline
import os
import logging

from app import app
from app.utilites.utilites import Utilites


from rdflib import Namespace

module = "query_mgt"

class Query:
    """
    Класс Query работает с запросам к triplestore
    """

    LOG_DIR = os.path.join(app.config['APP_DATA_PATH'], "logs")
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    LOG_FILE = os.path.join(LOG_DIR, "Query.log")
    SPARQT_DATA_PATH = os.path.join(app.config['APP_ROOT'], "app", "query_mgt", "sparqt", "")

    format_json = ".sparqt"

    SPARQT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sparqt")
    TEMPLATE_PARAMS = ['_CMT_', '#VARS', '#TXT']


    def __init__(self):
        self.url = ""
        self.http_headers = ""
        self.namespaces = ""

        self.url, self.http_headers, self.namespaces = Utilites.getQueryData()
        self.PREFIX = ''.join(["PREFIX " + key + ": <" + self.namespaces[key] + "> " for key in self.namespaces])

        self.logger = self.initLoggerComponent().getAppLogger()



    # logger
    def initLoggerComponent(self):
        """
        Метод возвращает класс logComponent для инициализации и поддержки функции логирования методов основного класса
        :return: logComponent
        """
        # TODO: Для расширения функциональности логирования статические части вынести в аттрибуты для изменения внешнего логера
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
        :param _query: string
        """
        try:
            response = requests.post(self.url, data={'query': _query}, headers=self.http_headers)
            if response.status_code != 200:
                self.logger.error("Request error: " + response.text)
                return []
        except Exception as e:
            self.logger.error("Request error: " + str(e))
            return []

        with response:
            return json.loads(response.text)


    def compileQueryResult(self, answer):
        """"""
        try:
            FINAL_RESULT = []
            for binding_set in answer['results']['bindings']:
                FINAL_RESULT.append(
                    {var_name: binding_set[var_name]['value'] if var_name in binding_set else "" for var_name in
                     answer['head']['vars']})

            return FINAL_RESULT

        except Exception as e:
            return []




    def query(self, _query):
        """
        Метод подставляет префиксы в запрос и форматирует ответ от триплстора
        :param _query: string
        :return: FINAL_RESULT
        """
        FINAL_RESULT = []
        if not _query:
            return []

        _query = self.PREFIX + " " + _query
        try:
            answer = self.runQuery(_query)

            FINAL_RESULT = self.compileQueryResult(answer)
            
        except:
            return []

        return FINAL_RESULT



    def compileQuery(self, code, params = {}):
        """
        Метод парсит код sparqt, компилирирует текст запроса и возвращает ответ от метода query
        :param code: string
        :param params: dict {VARNAME : VALUE}
        """
        try:
            from app.app_api import get_mod_decscription, get_mod_path

            delimeter = "."
            module, file, key_in_file = code.split(delimeter)
            g = get_mod_decscription(module)

            OSPLM = Namespace("http://splm.portal.web/osplm#")
            path_sparqt = ""
            for path in g.objects(predicate=OSPLM.hasPathForSPARQLquery):
                path_sparqt = path
                break

            self.SPARQT_DATA_PATH = os.path.join(get_mod_path(module), path_sparqt)
            input_json = open(os.path.join(self.SPARQT_DATA_PATH, file + self.format_json), "r", encoding="utf-8")

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
            return ""


    def queryByCode(self, code, params={}):
        """
        Метод парсит код sparqt, компилирирует текст запроса и возвращает ответ от метода query
        :param code: string
        :param params: dict {VARNAME : VALUE}
        """
        try:
            _query = self.compileQuery(code, params)
            return self.query(_query)
        except Exception as e:
            return []





    @classmethod
    def get_full_path_sparqt(self, file):
        """
        Метод возвращает абсолютный путь файла
        :param file: string
        :return: path
        """
        return os.path.join(self.SPARQT_DIR, file + self.format_json)

    @classmethod
    def get_list_sparqt(self):
        """
        Метод возвращает список названий sparqt файлов без расширений
        :return: files
        """
        files = []
        for file in os.listdir(self.SPARQT_DIR):
            if os.path.isfile(os.path.join(self.SPARQT_DIR, file)):
                files.append(os.path.splitext(file)[0])
        files.sort()
        return files

    @classmethod
    def get_file_object_sparqt(self, file):
        """
        Метод возвращает содержимое sparqt файла
        :param file: string
        :return: templates
        """
        if not file:
            return {}

        with open(self.get_full_path_sparqt(file), "r", encoding="utf-8") as f:
            templates = multiline.load(f, multiline=True)

        return templates

    @classmethod
    def edit_file_object_sparqt(self, file, templates):
        """
        Метод редактирует содержимое sparqt файла
        :param file: string
        :param templates: string
        """
        with open(self.get_full_path_sparqt(file), "w", encoding="utf-8") as f:
            json_text = json.dumps(templates, indent='\t', ensure_ascii=False)
            json_text = json_text.replace('\\n', '\n').replace('\\r', '')
            f.write(json_text)

    @classmethod
    def delete_file_object_sparqt(self, file):
        """
        Метод удаляет sparqt файл
        :param file: string
        """
        if os.path.exists(self.get_full_path_sparqt(file)):
            os.remove(self.get_full_path_sparqt(file))

    @classmethod
    def get_templates_names_sparqt(self, file):
        """
        Метод возвращает список ключей в sparqt файле
        :param file: string
        :return: list
        """
        return list(self.get_file_object_sparqt(file).keys())


    @classmethod
    def get_structure_codes_sparqt(self, file):
        """
        Метод возвращает список кодов запросов для sparqt файла
        :param file: string
        :return: list
        """
        return [module + "." + file + "." + key for key in self.get_templates_names_sparqt(file)]

    @classmethod
    def get_template_sparqt(self, file, template_name):
        """
        Метод возвращает объект с ключом template_name в sparqt файле
        :param file: string,
        :param template_name: string
        :return: result
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

    @classmethod
    def edit_template_sparqt(self, file, template_name, template_params):
        """
        Метод редактирует объект с ключом template_name в sparqt файле
        :param file: string,
        :param template_name: string,
        :param template_params: string
        """
        templates = self.get_file_object_sparqt(file)
        templates[template_name] = {self.TEMPLATE_PARAMS[i]: template_params[i] for i in range(0, len(template_params))}

        # #VARS
        if self.TEMPLATE_PARAMS[1] in templates[template_name]:

            var_s = templates[template_name][self.TEMPLATE_PARAMS[1]].split(",")
            dict_var_s = {}
            for var in var_s:
                var = var.split("=")
                dict_var_s[var[0]] = {"mark":"#{" + var[0] + "}","default": var[1]}

            templates[template_name][self.TEMPLATE_PARAMS[1]] = json.dumps(dict_var_s)

            templates[template_name][self.TEMPLATE_PARAMS[1]] = templates[template_name][self.TEMPLATE_PARAMS[1]].replace("\'", "\"")
            templates[template_name][self.TEMPLATE_PARAMS[1]] = json.loads(templates[template_name][self.TEMPLATE_PARAMS[1]])

        self.edit_file_object_sparqt(file, templates)

    @classmethod
    def delete_template_sparqt(self, file, template):
        """
        Метод удаляет объект с ключом template в sparqt файле
        :param file: string,
        :param template: string,
        """
        templates = self.get_file_object_sparqt(file)
        templates.pop(template)
        self.edit_file_object_sparqt(file, templates)

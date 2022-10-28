# -*- coding: utf-8 -*-
import json
import multiline
import os
import logging

from app import app
from app.utilites.utilites import Utilites

from app.drivers.store_driver import StoreDriver

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
        # TODO: Для расширения функциональности логирования статические части вынести в аттрибуты для изменения внешнего логера
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
        :param _query: string
        """
        try:
            response = self.storage_driver._exec_query(_query)
            # self.logger.info("This is the query string: \n" + _query)
            return json.loads(response)
        except Exception as e:
            self.logger.error("Request error: " + str(e))
            return []


    def compileQueryResult(self, answer):
        """"""
        try:
            FINAL_RESULT = []
            for binding_set in answer['results']['bindings']:
                FINAL_RESULT.append(
                    {var_name: binding_set[var_name]['value'] if var_name in binding_set else "" for var_name in
                     answer['head']['vars']}
                 )

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

        try:
            answer = self.runQuery(_query)

            FINAL_RESULT = answer
            if StoreDriver()._is_select_query(_query):
                FINAL_RESULT = self.compileQueryResult(answer)
            
        except Exception as e:
            return []

        return FINAL_RESULT



    def compileQuery(self, code, params = {}):
        """
        Метод парсит код sparqt, компилирирует текст запроса и возвращает ответ от метода query
        :param code: string
        :param params: dict {VARNAME : VALUE}
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
            return ""

    def __get_real_qfile(self, file_path):
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
        :param code: string
        :param params: dict {VARNAME : VALUE}
        """
        try:
            _query = self.compileQuery(code, params)
            return self.query(_query)
        except Exception as e:
            return []

    def get_full_path_sparqt(self, file):
        """
        Метод возвращает абсолютный путь файла
        :param file: string
        :return: path
        """
        _pth = os.path.join(self.SPARQT_DIR, file + self.format_json)
        _pth = self.__get_real_qfile(_pth)
        return _pth

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

    def can_remove(self, file):
        """
        Метод проверяет можно ли удалять файл - то есть изначальный файл был отредактирован пользователем
        :param file:
        :return:
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
        :param file:
        :return:
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
        :param file: string
        :return: templates
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
        :param file: string
        :param templates: string
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
        Метод удаляет sparqt файл
        :param file: string
        """
        if os.path.exists(self.get_full_path_sparqt(file)):
            os.remove(self.get_full_path_sparqt(file))

    def get_templates_names_sparqt(self, file):
        """
        Метод возвращает список ключей в sparqt файле
        :param file: string
        :return: list
        """
        return list(self.get_file_object_sparqt(file).keys())


    def get_structure_codes_sparqt(self, file):
        """
        Метод возвращает список кодов запросов для sparqt файла
        :param file: string
        :return: list
        """
        return [module + "." + file + "." + key for key in self.get_templates_names_sparqt(file)]

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
        Метод удаляет объект с ключом template в sparqt файле
        :param file: string,
        :param template: string,
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

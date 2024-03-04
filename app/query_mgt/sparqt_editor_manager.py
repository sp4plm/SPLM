# -*- coding: utf-8 -*-

import os
import json
import multiline
from app import app_api
from flask import request, redirect, url_for

from app.utilites.files_editor_manager import FilesEditorManager


class SparqtEditorManager(FilesEditorManager):
    """
    Создание менеджера редактирования файлов
    """

    MOD_CFG_PATH = ""

    module_name = ""

    format_json = ".sparqt"

    SPARQT_DIR = ""
    TEMPLATE_PARAMS = ['_CMT_', '#VARS', '#TXT']

    def __init__(self, module_name):
        self.module_name = module_name
        if module_name:
            from app.app_api import get_module_sparqt_dir
            self.SPARQT_DIR = get_module_sparqt_dir(module_name)

            if not os.path.exists(self.SPARQT_DIR):
                os.mkdir(self.SPARQT_DIR)

    def get_full_file_path(self, file):
        """
        Метод возвращает абсолютный путь файла

        :param str file: название sparqt-файла без расширения.
        :return _pth: абсолютный путь до sparqt-файла
        :rtype: str
        """
        _pth = os.path.join(self.SPARQT_DIR, file + self.format_json)
        _pth = self._get_real_qfile(_pth)
        return _pth

    def get_files(self):
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

    def can_remove_template(self, file, template):
        """
        Метод проверяет можно ли удалять шаблон - то есть изначальный шаблон был отредактирован пользователем

        :param str file: название sparqt-файла без расширения,
        :param str template: название шаблона в sparqt-файле file.
        :return _flg: True/False
        :rtype: bool
        """
        _flg = False
        _pth = self.get_full_file_path(file)
        _conf_path = self._get_app_conf_dir()
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

        with open(self.get_full_file_path(file), "r", encoding="utf-8") as f:
            templates = multiline.load(f, multiline=True)

        return templates

    def edit_file_object_sparqt(self, file, templates):
        """
        Метод редактирует содержимое sparqt файла

        :param str file: название sparqt-файла без расширения,
        :param dict templates: объект с шаблонами для текущего sparqt-файла.

        """
        # согласно новой концепции сохранять редактируемый файл требуется в директорию общего конфига
        _conf_path = self._get_app_conf_dir()  # директория конфигураций приложения
        _pth = self.get_full_file_path(file)
        if not _pth.startswith(_conf_path):
            _root_path = self._get_app_root_dir()
            relative = _pth.replace(_root_path, '').lstrip(os.path.sep).split(os.path.sep)
            #  принудительно заменяем путь сохранения
            _t = _conf_path
            for _s in relative:
                if _s == relative[-1]:
                    break
                _t += os.path.sep + _s
                if not os.path.exists(_t):
                    try:
                        os.mkdir(_t)
                    except:
                        pass
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
        if os.path.exists(self.get_full_file_path(file)):
            os.remove(self.get_full_file_path(file))

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
        return [self.module_name + "." + file + "." + key for key in self.get_templates_names_sparqt(file)]

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
                    dict_var_s[var[0]] = {"mark": "#{" + var[0] + "}", "default": var[1]}

            templates[template_name][self.TEMPLATE_PARAMS[1]] = json.dumps(dict_var_s)

            templates[template_name][self.TEMPLATE_PARAMS[1]] = templates[template_name][
                self.TEMPLATE_PARAMS[1]].replace("\'", "\"")
            templates[template_name][self.TEMPLATE_PARAMS[1]] = json.loads(
                templates[template_name][self.TEMPLATE_PARAMS[1]])

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

    @staticmethod
    def check_before_save(*args, **kwargs):
        """ Проверка по умолчанию всегда True """
        return True

    def create(self, url, blueprint_mod, check_before_save=None):
        """
        Метод создает три функции-маршрута для данного модуля: _list, _file, _template

        :param str url: наш url по которому будет редактор,
        :param Blueprint blueprint_mod: экземпляр класса blueprint в файле views текущего модуля.
        :param вуа check_before_save: метод проверяющий данные перед сохранением
        """
        _auth_decorator = app_api.get_auth_decorator()
        bm_name = blueprint_mod.name

        if callable(check_before_save):
            self.check_before_save = check_before_save

        _params = {
            "module": bm_name,
            "title": "Редактор SPARQL шаблонов для модуля " + bm_name
        }

        @blueprint_mod.route(url, methods=['GET', 'POST'])
        @_auth_decorator
        def _sparqt_list():
            """ Отображает список файлов sparqt """
            return app_api.render_page('/query_mgt/list.html', files=self.get_files(), **_params)

        @blueprint_mod.route(url + '/<file>', methods=["GET", "POST"])
        @_auth_decorator
        def _sparqt_templates(file=''):
            """
            Отображает список шаблонов в текущем sparqt-файле

            :param str file: название текущего sparqt-файла без расширения,
            :return: html-страница
            """
            if 'save' in request.form:
                if file and not os.path.exists(
                        self.get_full_file_path(file)):
                    self.edit_file_object_sparqt(file, {})
                else:
                    pass
                    # self.logger.error("Can't save sparqt file")
                return redirect(url_for(bm_name + '._sparqt_list'))

            elif 'delete' in request.form:
                self.delete_file_object_sparqt(file)
                return redirect(url_for(bm_name + '._sparqt_list'))

            else:
                return app_api.render_page('/query_mgt/templates.html',
                                           templates=self.get_templates_names_sparqt(file), file=file,
                                           can_remove=self.can_remove(file), **_params)

        @blueprint_mod.route(url + '/<file>/<template>', methods=["GET", "POST"])
        @_auth_decorator
        def _sparqt_editor(file, template=''):
            """
            Редактор шаблона в sparqt-файле

            :param str file: название текущего sparqt-файла без расширения,
            :param str template: название текущего шаблона в sparqt-файле,
            :return: html-страница
            """

            _render_data = {
                **_params,
                **{
                    "file": file,
                    "template": template,
                    "can_remove": self.can_remove_template(file, template),
                    "ajax_url": url_for("query.test_query")
                }
            }

            if 'save' in request.form:
                if os.path.exists(self.get_full_file_path(file)) and template in self.get_templates_names_sparqt(file):
                    # Проверка данных и сохранение
                    save_status = self.check_before_save()
                    if save_status is True:
                        self.edit_template_sparqt(file, template, [request.form['cmt'], request.form['vars'],
                                                                   request.form['txt']])
                    else:
                        # Если проверка данных не прошла, то возвращаемся обратно в форму
                        return app_api.render_page('/query_mgt/editor.html', **_render_data,
                                                   cmt=request.form['cmt'], vars=request.form['vars'],
                                                   txt=request.form['txt'], error=save_status)
                else:
                    pass
                    # self.logger.error(
                    #     "Can't save sparqt template \"" + request.form['template'] + "\" in file \"" + file + "\"")

                return redirect(url_for(bm_name + '._sparqt_templates', file=file))

            elif 'delete' in request.form:
                self.delete_template_sparqt(file, template)
                return redirect(url_for(bm_name + '._sparqt_templates', file=file))

            else:
                cmt, var, txt = self.get_template_sparqt(file, template)
                return app_api.render_page('/query_mgt/editor.html', **_render_data, cmt=cmt, vars=var, txt=txt)

# -*- coding: utf-8 -*-
import os
from app.query_mgt.query_conf import QueryConf
from app.query_mgt.sparqt_editor_manager import SparqtEditorManager

from app.utilites.utilites import Utilites
from app.admin_mgt.admin_conf import AdminConf
from app.utilites.some_config import SomeConfig


class ModApi(QueryConf):
    _class_file = __file__
    _debug_name = 'QueryUtilsApi'

    # Чтобы использовать в другом модуле нужно импортировать апи
    # query_mod_api = app_api.get_mod_api('query_mgt')
    # потом вызываем функцию create_sparqt_manager с заданными параметрами
    # Пример - query_mod_api.create_sparqt_manager("my_custom_sparqt", mod)
    # В dublin.ttl добавляем <SUBJECT> <http://splm.portal.web/osplm#hasPathForSPARQLquery> "<DIR_NAME>"^^<http://www.w3.org/2001/XMLSchema#string> .
    # Где вместо <SUBJECT> - uri модуля, <DIR_NAME> - папка от корня модуля где будут хранится шаблоны
    @staticmethod
    def create_sparqt_manager(__url, __mod):
        """
        Создает новые методы для интерфейса редактирования sparqt шаблонов.
        Для модуля blueprint : __mod под адресом : <base_mod_uri>/__URL

        :param str __url: наш url по которому будет SPARQTManager
        :param Blueprint __mod: экземпляр класса blueprint в файле views текущего модуля
        :return: метод реализующий редактор sparqt-файлов для модулей через интерфейс
        :rtype: def
        """
        module_name = os.path.basename(__mod.root_path)
        return SparqtEditorManager(module_name=module_name).create(__url, __mod)

    @staticmethod
    def jqgrid(cfg={}, query="", vars={}, data=None, title="", is_main_tz=False, xicon=True, xicon_close=True):
        """
        Метод возвращает html для создания jqgrid-таблицы

        :param dict cfg: настройки для таблицы
        :param str query: sparqt-запрос
        :param dict vars: параметры для sparqt-запроса
        :param list/pd.DataFrame data: уже готовые данные для таблицы
        :param str title: заголовок таблицы
        :param bool is_main_tz: является ли ТЗ в таблице основым ТЗ (только для TZ) - True/False (по умолчанию нет)
        :param bool xicon: тип таблицы с функцией скрытия или нет - True/False (по умолчанию с функцией)
        :param bool xicon_close: тип блока скрытый/раскрытый - True/False (по умолчанию скрытый)
        :return: html

        Examples
        --------
        return create_sparqt_manager(__URL, __mod)

        cfg = {
                "datatype": "local",
                "pager": '',
                "rowNum": 10,
                "rowList": [10, 20, 30],
                "sortname": "id",
                "sortorder": "desc",
                "viewrecords": True,
                "gridview": True,
                "autoencode": False,
                "autowidth": True,
                "colModel": [
                    {"label": "Документ", "index": "tz_lbl", "name": "tz_lbl", "width": 20, "align": "center", "search": True, "stype": 'text',
                     'formatter':'_2HtmlLink_frmt',
                     "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
                     },
                    {"label": "Наименование документа", "index": "name_val", "name": "name_val", "width": 60, "align": "center", "search": True, 'stype': 'text',
                     "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
                     },
                     {"label": "Дата начала работ", "index": "start_val", "name": "start_val", "width": 20, "align": "center", "search": True, 'stype': 'text',
                     "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
                     }
                ]
            }

        --------

        # <module>.<file>.<template>
        query = "mod_splm_nav.Organization.list_of_tz"

        --------

        vars = {'PREF': 'http://proryv2020.ru/req_onto#', 'URI': 'http://proryv2020.ru/odek/data#123', 'LANG': 'ru'}

        --------

        data = [
            {"tz" : "MFR.4.0010", "req" : "MFR.4.0010-3.2-0010-R"},
            {"tz" : "MFR.4.0010", "req" : "MFR.4.0010-3.2-0020-R"}
        ]

        """
        import random
        import string
        import re
        import json
        import pandas as pd
        from flask import url_for, g, request
        from app.app_api import tsc_query, get_useDBGMode, canExportReqs, get_mod_api

        _app_cfg = SomeConfig(AdminConf.get_configs_path())

        args = request.args.to_dict()
        # Если префикс онтологии не указан, то назначаем префикс по умолчанию "onto"
        prefix = "onto"
        if "prefix" in args:
            prefix = args["prefix"]
        pref_unquote = ''
        for p in get_mod_api('onto_mgt').get_prefixes():
            if p[0] == prefix:
                pref_unquote = p[1]

        cls_to_ref = []
        table_data = []

        # для переменной в js
        if not query:
            query = ''.join(random.choice(string.ascii_uppercase) for _ in range(15))

        if data is None:
            # ===== export2Excel ======
            cfg['export2Excel'] = '1' if canExportReqs() else '0'
            # ===== для dbgMode ======
            cfg['query'] = query
            cfg['dbgMode'] = '1' if get_useDBGMode() else '0'

            data = tsc_query(query, vars)

        df = None
        if data is not None and isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            return ""

        # выбираем переменные на обработку
        for col in cfg['colModel']:
            if 'formatter' in col and col['formatter'] == '_2HtmlLink_frmt':
                key = re.sub(r'_lbl$', '', col['index'])
                cls_to_ref.append(key)
                key_cls = key + "_cls"
                try:
                    df[key_cls] = df[key_cls].str.replace(pref_unquote, '', regex=True)
                except Exception as e:
                    pass

        for key, val in df.transpose().to_dict().items():
            for val_key in val:
                # обработка Организаций через запятую и добавление ссылок
                if "company_" in val[val_key]:
                    if " " in val[val_key] or ";" in val[val_key] or "," in val[val_key]:
                        orgs = val[val_key].split('; ')
                        comp = ""
                        for org_iter in range(0, len(orgs)):
                            org = orgs[org_iter].split(', ', 1)
                            comp += "<a href=" + url_for('splm_nav.uri_class', class_object=val[val_key + "_cls"],
                                                         uri=org[0], prefix=prefix) + ">" + org[1] + "</a>"

                            if org_iter < len(orgs) - 1:
                                comp += "; "

                        val[val_key] = comp

            for item in cls_to_ref:
                item_cls = item + "_cls"
                item_lbl = item + "_lbl"
                try:
                    _href = url_for('splm_nav.uri_class', class_object=val[item_cls], uri=val[item], prefix=prefix)
                    val[item_lbl] = '<a href="' + _href + '">' + val[item_lbl] + '</a>'
                except:
                    try:
                        val[item_lbl] = val[item]
                    except Exception as e:
                        pass
            table_data.append(val)
        cfg['data'] = table_data

        # Экспертиза
        _expertRole = _app_cfg.get('users.Roles.expertRole')
        if g.user and g.user.has_role(_expertRole):
            exp = ['Экспертиза', url_for('splm_nav.tasksource')]
            if query == 'mod_splm_nav.TZ.contract_per_contractor':
                if is_main_tz:
                    cfg['export4Act'] = exp + [url_for('splm_nav.ver_reptasks'), 3, True, 50]
            elif query == 'mod_splm_nav.TZ.contract_repdocs_fact':
                cfg['export4Act'] = exp + [url_for('splm_nav.doc_reptasks'), 3]

        # +/-
        # xicon_close

        # создаем html
        name = query.split(".")[-1]
        html = """
                <div class="table-box">
                    <div class="json-source" style="display:none">"{name}"</div>
                    <script type="text/javascript">
                        var {name} = {cfg};
                    </script>
                </div>
                """.format(cfg=json.dumps(cfg), name=name)

        if xicon:
            return Utilites.create_xicon_block(html=html, title=title, id=name, xicon_close=xicon_close)
        else:
            return html

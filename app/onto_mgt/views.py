# -*- coding: utf-8 -*-

# Модуль для управления онтологиями

import os
import json

from math import ceil
from flask import Blueprint, request, redirect, url_for, session
from app import app, app_api

MOD_NAME = 'onto'

mod = Blueprint(MOD_NAME, __name__, url_prefix='/onto', template_folder="templates", static_folder="static")

# onto_mgt
MODULE_FOLDER = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

# app/data/onto_mgt
MODULE_FOLDER = os.path.join(app.config['APP_DATA_PATH'], MODULE_FOLDER)
if not os.path.exists(MODULE_FOLDER):
    try: os.mkdir(MODULE_FOLDER)
    except: pass

NAVIGATION_GRAPH_PATH = os.path.join(MODULE_FOLDER, "navigation_graphs")
if not os.path.exists(NAVIGATION_GRAPH_PATH):
    try: os.mkdir(NAVIGATION_GRAPH_PATH)
    except: pass

from app.admin_mgt.mod_api import ModApi

mod.add_app_template_global(app_api.get_app_root_tpl, name='app_root_tpl')
mod.add_app_template_global(ModApi.get_root_tpl, name='admin_root_tpl')

from app.utilites.code_helper import CodeHelper
from datetime import datetime

from app.onto_mgt.files_managment import FilesManagment

from shutil import rmtree, copyfile

from flask import send_file

import re

from app.onto_mgt.ontology import Ontology

from app.app_api import compile_query, compile_query_result

from urllib.parse import quote, unquote

from rdflib import Graph, URIRef

import networkx as nx

from app.utilites.axiom_reader import getClassAxioms

from app.utilites.data_serializer import DataSerializer

_auth_decorator = app_api.get_auth_decorator()


USE_NAMED_GRAPHS = False
app_cfg = app_api.get_app_config()
try:
    USE_NAMED_GRAPHS = CodeHelper.conf_bool(app_cfg.get('data_storages.Main.use_named_graphs'))
except:
    pass


def js_code_tree(tree):
    """
	Метод строит дерево в html и добавляет ссылки для узлов
	"""
    if tree:
        parent_id = json.loads(tree)[0]['id']

        js = '''<script type="text/javascript">
        $(function() {
    
            $('#tree3').hide()
    
            $('#tree3').tree({
                saveState: 'tree3',
                data: %s
            });
    
    
            $('#tree3').bind(
                'tree.click',
                function(event) {
                    // The clicked node is 'event.node'
                    var node = event.node;
    
                    url = window.location.href.split('?')[0];
                    params = window.location.href.split('?')[1].split('&');
                    for (let i = 0; i < params.length; i++) {
                      p = params[i].split('=')
                      if (p[0] == "onto") {
                        url += "?" + params[i]
                        break
                      }
                    }
                    url += "&uri=" + encodeURIComponent(node.uri)
                    location.href = url
                }
            );
    
            $('#tree3').show()
    
    
        });
        </script>''' % (tree)
    else:
        js = ''

    return js


def get_className(ontology_class):
    """
    Метод отдает класс онтологии
    """
    prefixes = {"http://www.w3.org/2002/07/owl" : "owl"}
    try:
        ontology, ontology_class = ontology_class.split("#")
    except Exception as e:
        pass
        _ris = ontology_class.find('/')
        if -1 < _ris:
            _ris = ontology_class.rfind('/')  # уточняем последний справа
            ontology = ontology_class[:_ris]
            ontology_class = ontology_class[_ris+1:]
    if ontology in list(prefixes.keys()):
        ontology_class = prefixes[ontology] + ":" + ontology_class
    else:
        ontology_class = ":" + ontology_class
    return ontology_class


# 2 функции по рендеру таблицы ОТНОШЕНИЯ
def create_table(table):
    """
    Метод строит html таблицу
    """
    return '<table class="simple-tbl report-data create_table_publics"><tbody>' + ''.join(["<tr>" + ''.join(row) + "</tr>" for row in table]) + '</tbody></table>'


def compileTableRow(value, is_header, column, colors_class = "", total = False, base_width = ""):
    """
    Метод возвращает ряд для html таблицы. С его результатом работает метод create_table
    """
    base_width = 'width:' + (base_width if base_width else '40%') + ';'
    colors_class = colors_class if colors_class else "table_text_color_397927"

    if not isinstance(value, str):
        value = str(value)

    if total:
        if column == 1:
            return '<th style="' + base_width + 'text-align:left;" scope="col">' + value + '</th>'
        else:
            return '<th class="report-main ' + colors_class + '" scope="col">' + value + '</th>'

    if is_header:
        return '<th class="TableRow_header" align="center" style="' + (base_width if column == 1 else '') + '">' + value + '</th>'
    else:
        if column == 1:
            return '<td align="center" style="vertical-align: middle; ' + base_width + '">' + value + '</td>'
        else:
            return '<td class="TableRow_not_header ' + colors_class + '" align="center">' + value + '</td>'


# Создание дерева
def load_graph(gr):
    """
    Метод получает данные из графа
    """
    path = []

    qrslt = gr.query('SELECT ?s ?o { ?s ^rdfs:subClassOf ?o . filter (isIRI(?s) && isIRI(?o))} order by ?s')

    for row in qrslt:
        path.append([str(row[0]),str(row[1])])

    return path

def create_graph_by_node(node, g):
    """ Метод создает граф для дерева """

    ontology_file_format = "ttl"

    # Циклическая функция сбора подчиненных узлов
    def get_children(n):
        """ Метод возвращает всех детей узла """
        i = ''
        child = []
        for k in G.successors(n):
            i = Defrag(n) + '_' + Defrag(k)
            ch2 = sorted(get_children(k), key=lambda x: x['name'])
            k_cls = Ontology.ns2pref(k)
            child.append({'id' : i, 'name' : k_cls, 'uri' : k, 'children' : ch2})

        return child

    input = load_graph(g)

    G = nx.DiGraph()
    G.add_edges_from(input)

    ch1 = sorted(get_children(node), key=lambda x: x['name'])
    data = [{'id' : Defrag(node), 'name' : Ontology.ns2pref(node), "uri" : node, 'children' : ch1}]  # Начинаем создавать дерево с указанного узла

    return data


def Defrag(URL):
    if "#" in URL:
        q = URIRef(URL).partition("#")
        return q[2]
    else:
        _k = '/'
        if _k in URL:
            _t = URL.split(_k)[-1]
            # если вконце лишний символ был
            if not _t:
                _t = URL.split(_k)[-2]
            # Важно! Возможно придется отсекать чать в _t начиная с какого-либо символа, несоответствующего path в URL
            return _t
        return ""


def get_onto_data(prefix):
    """"""
    G = Ontology().getGraph(prefix)

    query_cls_string = """select ?term ?term_lbl ?term_cls ?term_comm ?term_dfnt {
                                    ?term rdfs:subClassOf* owl:Thing .
                                    ?term a ?term_cls .
                                    Optional {?term rdfs:label ?term_lbl . }
                                    Optional { ?term rdfs:comment ?term_comm . }
                                    }
                               """

    data_cls = {}
    for row in G.query(query_cls_string):
        data_cls[Defrag(str(row[0]))] = [["URI", str(row[0])], ["Наименование", str(row[1])],
                                               ["Класс", str(row[2])], ["Комментарий", str(row[3])]]

    query_prd_string = """select ?term ?term_lbl ?term_cls ?term_dom ?term_rng ?term_comm
                                    {?term a owl:ObjectProperty .
                                    ?term a ?term_cls .
                                    Optional { ?term rdfs:label ?term_lbl . }
                                    Optional { ?term rdfs:domain ?term_dom . } 
                                    Optional { ?term rdfs:range ?term_rng . } 
                                    Optional { ?term rdfs:comment ?term_comm . }
                                    }
                               """
    data_prd = {}
    for row in G.query(query_prd_string):
        data_prd[Defrag(str(row[0]))] = [["URI", str(row[0])], ["Наименование", str(row[1])],
                                               ["Класс", str(row[2])], ["Domain", str(row[3])], ["Range", str(row[4])],
                                               ["Комментарий", str(row[5])]]

    data = {}
    data['Классы онтологии'] = data_cls
    data['Предикаты онтологии'] = data_prd

    return data


@mod.route('/nav_ontology')
@_auth_decorator
def nav_ontology():
    """
    Метод отвечает за навигацию по файлу онтологии и возвращает информацию об отношениях, аксиомах и экземплярах класса
    """
    _ontology = Ontology()
    _ontology.get_all_prefixes()  # fill class variable
    owl_Thing = "http://www.w3.org/2002/07/owl#Thing"

    _onto = unquote(request.args.get('onto') if request.args.get('onto') else "")
    uri = unquote(request.args.get('uri') if request.args.get('uri') else "")
    if not uri:
        uri = owl_Thing

    df = FilesManagment()
    onto_path = df.get_dir_realpath("ontos")

    onto_file = os.path.join(onto_path, _onto)

    if _onto not in session:
        graph = Graph().parse(onto_file, format=None)

        navigation_graph_file = os.path.join(NAVIGATION_GRAPH_PATH, _onto)
        DataSerializer().dump(navigation_graph_file, graph)

        session[_onto] = navigation_graph_file
    else:
        if os.path.exists(session[_onto]):
            graph = DataSerializer().restore(session[_onto])
        else:
            graph = Graph().parse(onto_file, format=None)
            DataSerializer().dump(os.path.join(NAVIGATION_GRAPH_PATH, _onto), graph)

    graph = _ontology.normalize_classes_tree(graph)  # make owl:Thing is classes hierarchy root

    TREE = json.dumps(create_graph_by_node(owl_Thing, graph))

    relations_code = "onto_mgt.onto.subject_nav_onto"
    RELATIONS = compile_query_result( json.loads( graph.query(compile_query(relations_code, {"URI" : uri})).serialize(format="json").decode("utf-8") )  )


    firstPKey = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    secondPKey = 'http://www.w3.org/2000/01/rdf-schema#label'

    subject_P = {}
    subject_O = {}
    subject_P_O = {}

    for item in RELATIONS:
        if item['p'] == firstPKey:
            firstPKey_data = item
        elif item['p'] == secondPKey:
            secondPKey_data = item
        else:
            if item['p'] not in list(subject_P.keys()):
                subject_P[item['p']] = item['p_lbl'] if 'p_lbl' in list(item.keys()) and item['p_lbl'] else item['p']

            if item['o'] not in list(subject_O.keys()):
                subject_O[item['o']] = item['o_lbl'] if 'o_lbl' in list(item.keys()) and item['o_lbl'] else item['o']

            subject_P_O[item['o']] = item['p']

    total_subject_P_O = {}
    for p_item in subject_P:
        total_subject_P_O[p_item] = [key for key in subject_P_O if subject_P_O[key] == p_item]

    table_cols_names = ["Свойство", "Значение", "Язык"]
    table_cols_names = [compileTableRow(table_cols_names[i], True, i + 1) for i in range(0, len(table_cols_names))]
    table_data = []
    for p_item in subject_P:
        for item in total_subject_P_O[p_item]:
            row = [subject_P[p_item], subject_O[item], ""]
            table_data.append([compileTableRow(row[i], False, i + 1) for i in range(0, len(row))])

    relations_html = create_table([table_cols_names] + table_data)

    base_uri = Ontology().getBaseUri(onto_file)
    AXIOMS = getClassAxioms(URIRef(uri), graph, base_uri + "#")

    table_data = []
    def get_values_from_dict(d):
        for v in d.values():
            if isinstance(v, dict):
                yield from get_values_from_dict(v)
            else:
                yield v
    list_ax = list(get_values_from_dict(AXIOMS))

    for ax in range(0, len(list_ax)):
        list_ax[ax] = re.sub(r"\n", "<br>", list_ax[ax])
        row = [str(ax + 1), list_ax[ax]]
        table_data.append([compileTableRow(row[i], False, i + 1) for i in range(0, len(row))])

    axioms_html = create_table(table_data)

    instances_query = "SELECT ?instance ?instance_lbl WHERE { ?instance a <%s> . OPTIONAL { ?instance rdfs:label ?instance_lbl . } }" % (uri)
    INSTANCES = compile_query_result( json.loads( graph.query(instances_query).serialize(format="json").decode("utf-8") )  )

    instances_html = ""
    for instance in INSTANCES:
        instances_html += "<li>" + (instance['instance_lbl'] if 'instance_lbl' in instance and instance['instance_lbl'] else instance['instance']) + "</li>"

    instances_html = "<div>" + "<ul>" + instances_html + "<ul>" + "</div>"


    return app_api.render_page("/onto_mgt/nav_ontology.html", relations = relations_html, axioms = axioms_html, instances = instances_html, js = js_code_tree(TREE), class_name = Ontology.ns2pref(uri))


@mod.route('/ontologies')
@_auth_decorator
def ontologies():
    """ Метод отдает структуру таблицы онтологий и рисует ее """
    _base_url = '/' + MOD_NAME

    # Таблица онтологий
    cols_ontos = [
        {"label": "", "index": "toolbar", "name": "toolbar", "width": 10, "sortable": False, "search": False},
        # {name: 'Type', index: 'Type', label: 'Type', hidden: True, sortable: False}
        {"label": "Тип", "index": "Type", "name": "Type", "hidden": True, "search": False},
        {"label": "ID", "index": "id", "name": "id", "hidden": True, "search": False},
        {"label": "Имя", "index": "name", "name": "Name", "width": 35, "search": True, "stype": 'text',
         "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
         },
        {"label": "Префикс", "index": "prefix", "name": "prefix", "width": 43, "align": "left",
         "search": True, 'stype': 'text',
         "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
         },
        {"label": "Дата загрузки", "index": "loaddate", "name": "loaddate", "width": 12, "align": "center",
         "search": True, 'stype': 'text',
         "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
         }
    ]

    cfg_ontos = {
        "datatype": "json",
        "mtype": "POST",
        "colModel": [],
        "pager": '',
        "rowNum": 10,
        "rowList": [10, 20, 30],
        "sortname": "id",
        "sortorder": "desc",
        "viewrecords": True,
        "gridview": True,
        "jsonReader": {"repeatitems": False},
        "autoencode": True,
        "autowidth": True,
        "caption": "",
        "toolbar": [True, "top"],
        "width": 1024
    }
    cfg_ontos['colModel'] = cols_ontos
    cfg_ontos['url'] = url_for("onto.get_files")


    return app_api.render_page("/onto_mgt/ontos.html", tbl = json.dumps(cfg_ontos))


@mod.route('/ontologies/print_onto')
@_auth_decorator
def print_onto():
    """
    Функция вывода онтологии для просмотра и печати
    """
    argms = request.args.to_dict()

    if 'prefix' in argms.keys():
        data = get_onto_data(argms['prefix'])
    elif 'filename' in argms.keys():
        data = Ontology().get_ontodata_by_file(argms['filename'])
    else:
        data = {'Ошибка! Префикс онтологии не указан.': {"": ""}}

    return app_api.render_page('/onto_mgt/print_onto.html', data=data)


@mod.route('/ontologies/print_onto/result', methods=["GET"])
@_auth_decorator
def print_onto_result():
    """ Печать классов онтологии """
    _printer = app_api.get_mod_api('printer')
    _pdf_tool = _printer.report()

    data = {}
    argms = request.args.to_dict()
    if 'prefix' in argms:
        data = get_onto_data(argms['prefix'])

    html = ""
    for type_key, type_val in data.items():
        for key, val in type_val.items():
            html += '<table width="100%" border="0" style="border-collapse:collapse;">'
            html += """
                <thead>
                <tr>
                    <th bgcolor="#efefef">Элемент: {key}</th>
                </tr>
                </thead>""".format(key=key)

            html += "<tbody>"
            for row in val:
                html += """
                    <tr>
                        <td>{k}</td>
                        <td>{v}</td>
                    </tr>
                """.format(k=row[0], v=row[1])
            html += "</tbody>"
            html += "</table>"

    _pdf_tool.set_html(html)

    _pdf_dir = os.path.join(MODULE_FOLDER, "pdf", "")
    if not os.path.exists(_pdf_dir):
        try: os.mkdir(_pdf_dir)
        except: pass

    _pdf_file = "pdf_" + datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + ".pdf"
    _pdf = os.path.join(_pdf_dir, _pdf_file)

    _pdf_tool.print(_pdf)

    _file = send_file(_pdf, download_name=_pdf_file, as_attachment=False)
    # удаляем файл из памяти
    os.remove(_pdf)
    return _file


@mod.route('/getFiles/ontos', methods=['GET', 'POST'])
@_auth_decorator
def get_files():
    """ Метод получает информацию о загруженных онтология """
    dir_name = "ontos"

    answer = {'rows': [], 'page': 1, 'records': 20, 'total': 1}
    page = 1 # get the requested page
    limit = 20 # get how many rows we want to have into the grid
    sidx = 'Name' # get index row - i.e. user click to sort
    sord = 'asc' # get the direction
    search_flag = False
    filters = ''
    # row = {'id': '', 'toolbar': '', 'Type': '', 'Name': '', 'loaddate': '', 'usemap': '', 'loadresult': ''}
    columns_map = {'id': 'name', 'toolbar': 'name', 'Type': 'name', 'name': 'name', 'Name': 'name', 'prefix' : 'name', 'loaddate': 'mdate', 'usemap': 'map', 'loadresult': 'result'}
    # теперь добавим колонки для медиа
    # backups
    columns_map['cmt'] = 'comment'

    if request.method == "GET":
        page = int(request.args['page']) if 'page' in request.args else page
        limit = int(request.args['rows']) if 'rows' in request.args else limit
        sidx = request.args['sidx'] if 'sidx' in request.args else sidx
        sord = request.args['sord'] if 'sord' in request.args else sord
        if '_search' in request.args:
            search_flag = not ('false' == request.args['_search']) # инверсия от значения
        filters = request.args['filters'] if 'filters' in request.args else filters

    if request.method == "POST":
        page = int(request.form['page']) if 'page' in request.form else page
        limit = int(request.form['rows']) if 'rows' in request.form else limit
        sidx = request.form['sidx'] if 'sidx' in request.form else sidx
        sord = request.form['sord'] if 'sord' in request.form else sord
        if '_search' in request.form:
            search_flag = not ('false' == request.form['_search']) # инверсия от значения
        filters = request.form['filters'] if 'filters' in request.form else filters

    offset = 0 if 1==page else (page-1)*limit

    file_list = []

    df = FilesManagment()
    file_list = df.get_dir_source(dir_name)
    if file_list:
        _dir_path = os.path.dirname(file_list[0]['fullname'])
        if search_flag:
            file_list = apply_jqgrid_filters(file_list, filters)

        """ теперь после поиска надо отсортировать """
        file_list = df.sort_files(file_list, sord, columns_map[sidx])
        file_list1 = file_list[offset:offset + limit] if len(file_list) > limit else file_list
       
        rows = []
        from app.onto_mgt.ontology import Ontology
        _onto = Ontology()
        for item in file_list1:
            row = {'id': '', 'toolbar': '', 'Type': '', 'Name': '', 'prefix' : '', 'loaddate': ''}

            _file_prefs = []
            _file_prefs_s = ''
            _c_file = os.path.join(_dir_path.rstrip(os.path.sep), item['name'])
            _file_prefs = _onto.get_prefixes_from_file(_c_file)
            if _file_prefs:
                _file_prefs_s = _onto.prefixes_to_str(_file_prefs)

            row['id'] = item['name']
            row['Name'] = item['name']
            row['prefix'] = item['prefix'] if 'prefix' in item else ""
            row['prefix'] = _file_prefs_s
            row['loaddate'] = item['mdate'] if 'mdate' in item else ""
            row['Type'] = 'f'
            rows.append(row)

    if file_list:
        answer['page'] = page
        answer['records'] = len(file_list)
        answer['total'] = ceil(answer['records'] / limit)
        answer['rows'] = rows
    return json.dumps(answer)


@mod.route('/loadFiles/ontos', methods=['GET', 'POST'])
@_auth_decorator
def upload_files():
    """ загружаем файлы в определенную директорию """
    dir_name = "ontos"

    answer = {'Msg': '', 'Data': None, 'State': 404}
    args = {"method": "POST"}
    if request.method == "POST":
        appended = []
        answer['Msg'] = 'Нет файлов для сохранения.'
        if request.files and 'File[]' in request.files:
            file = None # type: werkzeug.datastructures.FileStorage
            errors = []

            _existed = []
            _upload_dir = 'temp_upload_' + str(datetime.now())
            _tmp_path = os.path.dirname(os.path.abspath(__file__))
            _tmp_path = os.path.join(_tmp_path, _upload_dir)
            meta = FilesManagment()
            if meta.set_current_dir(dir_name):
                path = meta.get_current_dir()
                flg = False
                cnt = 0
                data = []

                for file in request.files.getlist('File[]'):
                    flg = False
                    if bool(file.filename):
                        # file_bytes = file.read(MAX_FILE_SIZE)
                        # args["file_size_error"] = len(file_bytes) == MAX_FILE_SIZE
                        # сохранялись пустые файлы
                        # решение:
                        # https://stackoverflow.com/questions/28438141/python-flask-upload-file-but-do-not-save-and-use
                        # # snippet to read code below
                        file.stream.seek(0)  # seek to the beginning of file
                        try:
                            secure_name = normalize_file_name(file.filename)
                            file_name = os.path.join(path, secure_name)
                            # для начала надо проверить существует ли файл с таким же именем

                            if os.path.exists(file_name):
                                # появился дубликат - создаем директорию загрузки если ее нет
                                if not os.path.exists(_tmp_path):
                                    try: os.mkdir(_tmp_path)
                                    except: pass
                                file_existed = []
                                file_existed.append(secure_name) # имя файла дубликата
                                file_existed.append(file_name) # полное имя файла под замену

                                _tmp_name = os.path.join(_tmp_path, secure_name + '_tmp')
                                if os.path.exists(_tmp_name):
                                    os.unlink(_tmp_name)
                                flg = save_uploaded_file(file, _tmp_name)
                                file_existed.append(_tmp_name) # новый загружаемый файл
                                file_existed.append(_tmp_path) # рабочая директория загрузки
                                _existed.append(file_existed)


                                FN = _tmp_name
                            else:
                                flg = save_uploaded_file(file, file_name)

                                FN = file_name

                            #######################
                            # Блок добавлен maxef для проверки уникальности префиксов и baseURI загружаемых онтологий
                            #######################

                            _can_upload = Ontology().can_upload_onto_file(FN, True)
                            if not _can_upload[0]:
                                _error_info = _can_upload[1]
                                # удаляем только что загруженный файл!
                                os.remove(FN)
                                _msg = 'Невозможно загрузить файл из-за коллизии префиксов!'
                                _msg += 'Для префикса ' + _error_info['short'] + ' в загружаемом файле попытка '
                                _msg += 'переопределить его URI с ' + _error_info['exist'] + ' на'
                                _msg += ' ' + _error_info['checked']
                                answer['Msg'] = _msg
                                errors.append(_msg)
                                return json.dumps(answer)

                            # Проверка base_uri
                            # _baseURI = Ontology().getBaseUri(FN)
                            # _prefix = Ontology().getOntoPrefix(FN)
                            #
                            #
                            # for item in meta.get_dir_source(dir_name):
                            #     if "fullname" in item:
                            #         if Ontology().getBaseUri(item['fullname']) == _baseURI:
                            #             # удаляем только что загруженный файл!
                            #             os.remove(FN)
                            #
                            #             answer['Msg'] = 'Невозможно загрузить файл. Такой baseURI ({}) уже существует в {}'.format(_baseURI, item['name'])
                            #             errors.append('Невозможно загрузить файл. Такой baseURI ({}) уже существует в {}'.format(_baseURI, item['name']))
                            #             return json.dumps(answer)
                            #
                            #     if "prefix" in item:
                            #         if Ontology().getOntoPrefix(item['fullname']) == _prefix:
	                        #             # удаляем только что загруженный файл!
	                        #             os.remove(FN)
                            #
	                        #             answer['Msg'] = 'Невозможно загрузить файл. Такой префикс ({}) уже существует в {}'.format(item["prefix"], item['name'])
	                        #             errors.append('Невозможно загрузить файл. Такой префикс ({}) уже существует в {}'.format(item["prefix"], item['name']))
	                        #             return json.dumps(answer)


                        except Exception as ex:
                            answer['Msg'] = 'Cann`t upload file: {}. Error: {}'.format(file.filename, ex)
                            errors.append('Cann`t upload file: {}. Error: {}'.format(file.filename, ex))
                        if flg:
                            cnt += 1
                            data.append(secure_name)

                if 0 < cnt:
                    answer['State'] = 200
                    answer['Msg'] = ''
                    answer['Data'] = data
                    # теперь синхронизируем описание директории
                    meta.sync_description()
                    
                    
                if 0 < len(_existed):
                    answer['Existed'] = _existed
                    answer['State'] = 200
                    answer['Msg'] = ''
            else:
                answer['Msg'] = 'Неизвестная директория -> "' + dir_name + '"!'
            # проверяем создана ли директория и если создана и пустая удаляем
            if CodeHelper.check_dir(_tmp_path) and CodeHelper.is_empty_dir(_tmp_path):
                rmtree(_tmp_path) # удаляем ненужную директорию
    return json.dumps(answer)


@mod.route('/removeFile/ontos', methods=['GET', 'POST'])
@_auth_decorator
def remove_file():
    """ сохраняем изменения связанные с файлом """
    dir_name = "ontos"

    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    if 'POST' == request.method:
        name = request.form['file'].strip() if 'file' in request.form else ''


        meta = FilesManagment()
        if meta.set_current_dir(dir_name):
            path = meta.get_current_dir()
            if '' != name:
                flg = False

                flg = meta.remove_file(name, dir_name)
                if flg:
                    file_info = meta.get_item_description(dir_name, name)
                    if 'result' in file_info and '' != file_info['result']:
                        if USE_NAMED_GRAPHS:
                            meta.set_current_dir('res')
                            meta.set_file_description(file_info['result'], {'deleted': True})
                            meta.set_current_dir(dir_name)
                        else:
                            meta.remove_item('res', file_info['result'])
                    
                    answer['State'] = 200
                    answer['Msg'] = ''
                    answer['Data'] = {'file': name}
                    meta.sync_description()
                else:
                    msg = ''
                    if '' != answer['Msg']:
                        msg = ' (' +answer['Msg'] + ')'
                    answer['Msg'] = 'Не удалось удалить файл "{}"!{}'.format(name,msg)
                    # а что если залипло описание
                    find_files = meta.search_files_by_descr(dir_name, {'name': name})
                    # если нашли файлы в описании
                    if find_files:
                        meta.sync_description()
                        find_files = meta.search_files_by_descr(dir_name, {'name': name})
                        if 0 == len(find_files):
                            answer['State'] = 200
                            answer['Msg'] = ''
                            answer['Data'] = {'file': name}

            # удаляем конфигурацию из navigation_graphs
            meta.remove_file(name, NAVIGATION_GRAPH_PATH)

        else:
            answer['Msg'] = 'Неизвестная директория -> ' + dir_name + '!'
    return json.dumps(answer)


@mod.route('/removeSelection/ontos', methods=['POST'])
@_auth_decorator
def remove_selection():
    """ сохраняем изменения связанные с файлом """
    dir_name = "ontos"

    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    if 'POST' == request.method:
        # все значения полей под тменами полей делает списками
        # требуется если для одного поля требуется обработать несколько значений
        form_dict = request.form.to_dict(flat=False)
        items = form_dict['items[]'] if 'items[]' in form_dict else []
        deleted = []

        meta = FilesManagment()
        if meta.set_current_dir(dir_name):
            path = meta.get_current_dir()
            rp = ''
            for fi in items:
                rp = os.path.join(path, fi)
                if not os.path.exists(rp):
                    continue
                if os.path.isdir(rp):
                    rmtree(rp, ignore_errors=True)
                else:
                    flg = False
                    os.unlink(rp)

                    file_info = meta.get_item_description(dir_name, fi)
                    if '' != file_info['result']:
                        if USE_NAMED_GRAPHS:
                            meta.set_current_dir('res')
                            meta.set_file_description(file_info['result'], {'deleted': True})
                            meta.set_current_dir(dir_name)
                        else:
                            meta.remove_item('res', file_info['result'])
                    meta.set_current_dir(dir_name)
                deleted.append(fi)

                # удаляем конфигурацию из navigation_graphs
                meta.remove_file(fi, NAVIGATION_GRAPH_PATH)

                """ end loop of deleted items """
            if 0 < len(deleted):
                answer['State'] = 200
                answer['Msg'] = ''
                answer['Data'] = {'deleted': deleted, 'all': items}
                meta.sync_description()
            else:
                answer['Msg'] = 'Не удалось удалить данные!'
        else:
            answer['Msg'] = 'Неизвестная директория -> ' + dir_name + '!'
    return json.dumps(answer)


@mod.route('/downloadFile/ontos', methods=['GET', 'POST'])
@_auth_decorator
def download_file():
    """ отдаем файл на скачивание """
    dir_name = "ontos"


    errorMsg = 'Неизвестный файл для скачивания!'
    if request.method == "GET":
        filename = request.args['file']
        path = ''
        meta = FilesManagment()
        if meta.set_current_dir(dir_name):
            path = meta.get_current_dir()

        download_file = os.path.join(path, filename)
        if os.path.exists(download_file):
            download_file_name = filename
            mime = 'application/octet-stream'
            file_ext = ''
            test = filename.split('.')
            file_ext = test[len(test)-1]
            _mime = CodeHelper.get_mime4file_ext(file_ext)
            if '' != _mime:
                mime = _mime
            return send_file(download_file, mimetype=mime,
                             as_attachment=True, attachment_filename=download_file_name)
    return app_api.render_page("errors/404.html", message=errorMsg)


@mod.route('/accept_newfile/ontos', methods=['POST'])
@_auth_decorator
def accept_new_file():
    """ Метод принимает новый файл в случае совпадения имен """
    dir_name = "ontos"

    answer = {'Msg': '', 'Data': None, 'State': 404}
    recive_data = reqform_2_dict(request.form)
    files = recive_data['exfiles'] if 'exfiles' in recive_data else list(recive_data.values())
    meta = FilesManagment()
    answer['Msg'] = 'No files'
    if files:
        answer['Msg'] = 'Catch files'
        _upload_temp = files[0][3]
        proc = []
        existed_names = []
        for item in files:
            if not os.path.exists(item[1]):
                continue
            existed_names.append(item[0])
            """ copy from 2 to 1 """
            
            # сперва удаляем 1
            os.unlink(item[1])
            # затем копируем 2 в 1
            copyfile(item[2], item[1])
            # удаляем 2
            if not os.path.exists(item[2]):
                continue
            os.unlink(item[2])
            proc.append(item[0])
        
        answer['Data'] = proc
        answer['State'] = 200
        answer['Msg'] = ''
        # проверим пуста ли временная директория загрузки файлов
        if is_empty_upload_temp(_upload_temp):
            rmtree(_upload_temp) # удаляем поскольку пуста
    return json.dumps(answer)


@mod.route('/reject_newfile/ontos', methods=['POST'])
@_auth_decorator
def reject_new_file():
    """ Метод игнорирует новый файл в случае совпадения имен """
    dir_name = "ontos"


    answer = {'Msg': '', 'Data': None, 'State': 404}
    recive_data = reqform_2_dict(request.form)
    files = recive_data['exfiles'] if 'exfiles' in recive_data else list(recive_data.values())
    meta_data = FilesManagment()
    answer['Msg'] = 'No files'
    if files:
        answer['Msg'] = 'Catch files'
        _upload_temp = files[0][3]
        proc = []
        for item in files:
            if not os.path.exists(item[2]):
                continue
            """ remove 2 """
            os.unlink(item[2])
            proc.append(item[0])
        answer['Data'] = proc
        answer['State'] = 200
        answer['Msg'] = ''
        # проверим пуста ли временная директория загрузки файлов
        if is_empty_upload_temp(_upload_temp):
            rmtree(_upload_temp) # удаляем поскольку пуста
    return json.dumps(answer)


def is_empty_upload_temp(_check_path):
    """ Метод проверяет содержимое директории """
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


def reqform_2_dict(reqform):
    """"""
    _data = reqform.to_dict(flat=False)
    _normalized = {}
    for key in _data:
        """"""
        _pos = key.find('[')
        origin = ''
        _struct_k = ''
        _struct = None
        root_list = False
        root_dict = False
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


def map_file_descr_property(col):
    """ Описание свойств """
    prop = ''
    cols = {'toolbar': '', 'id': 'name', 'name': 'name', 'Name': 'name', 'prefix' : 'name',
            'loaddate': 'mdate', 'usemap': 'map', 'loadresult': 'result'}
    cols = {'id': 'name', 'toolbar': 'name', 'Type': 'name', 'name': 'name', 'Name': 'name', 'prefix' : 'prefix',
                   'loaddate': 'mdate', 'usemap': 'map', 'loadresult': 'result'}
    # теперь добавим колонки для медиа
    # backups
    cols['cmt'] = 'comment'
    if col in cols:
        prop = cols[col]
    return prop

"""
# operations
# 'cn' - содержит | поиск подстроки в строке
# 'nc' - не содержит | поиск подстроки в строке инверсия
# 'eq' - равно | прямое сравнение
# 'ne' - не равно | инверсия прямого сравнения
# 'bw' - начинается | позиция 0 искомого вхождения
# 'bn' - не начинается | инверсия от 0 позиции
# 'ew' - заканчивается на | подстрока является концом строки
# 'en' - не заканчивается на | инверсия что подстрока является концом строки
"""
def apply_filter_rule(item, rule):
    """ непосредственное сравнение со значением с использованием операции """
    flg = False
    # {"field":"name","op":"cn","data":"15-22"}
    field = map_file_descr_property(rule['field'])
    oper = rule['op']
    val = rule['data']
    if 'cn' == oper:
        # 'cn' - содержит | поиск подстроки в строке
        flg = (-1 < item[field].find(val))
    elif 'nc' == oper:
        # 'nc' - не содержит | поиск подстроки в строке инверсия
        flg = (-1 == item[field].find(val))
    elif 'eq' == oper:
        # 'eq' - равно | прямое сравнение
        flg = (val == item[field])
    elif 'ne' == oper:
        # 'ne' - не равно | инверсия прямого сравнения
        flg = (val != item[field])
    elif 'bw' == oper:
        # 'bw' - начинается | позиция 0 искомого вхождения
        flg = item[field].startswith(val)
    elif 'bn' == oper:
        # 'bn' - не начинается | инверсия от 0 позиции
        flg = not (item[field].startswith(val))
    elif 'ew' == oper:
        # 'ew' - заканчивается на | подстрока является концом строки
        flg = (item[field].endswith(val))
    elif 'en' == oper:
        # 'en' - не заканчивается на | инверсия что подстрока является концом строки
        flg = not (item[field].endswith(val))
    return flg


def is_respond_to_rules(item, rules, group_op):
    """ сравнение значения с помощью операции """
    flg = False
    count = 0
    #  [{"field":"name","op":"cn","data":"15-22"}]
    for rule in rules:
        if apply_filter_rule(item, rule):
            count += 1
    if 'AND' == group_op and len(rules) == count:
        flg = True
    if 'OR' == group_op and 0 < count:
        flg = True
    return flg


def apply_jqgrid_filters(source_list, filters):
    """ прменение поиска по файлам """
    result_list = []
    f_params = json.loads(filters)
    # filters	{"groupOp":"AND","rules":[{"field":"name","op":"cn","data":"15-22"}]}
    for item in source_list:
        flg = is_respond_to_rules(item, f_params['rules'], f_params['groupOp'])
        if flg:
            result_list.append(item)
    return result_list



def save_uploaded_file(http_file, file_name=''):
    flg = True
    if http_file:
        work_file = file_name
        if not os.path.exists(work_file):
            http_file.save(work_file)
            flg = True
    return flg



def normalize_file_name(file_name):
    res = file_name
    res = '_'.join(res.split(' '))
    res = translit_rus_string(res)
    return res


def translit_rus_string(ru_str):
    res = CodeHelper.translit_rus_string(ru_str)
    return res

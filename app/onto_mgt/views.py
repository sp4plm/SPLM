# -*- coding: utf-8 -*-
import os
import json
from math import ceil

from flask import Blueprint, render_template, request, redirect, url_for
from app import app, app_api
from flask_login import login_required

MOD_NAME = 'onto'


mod = Blueprint(MOD_NAME, __name__, url_prefix='/onto', template_folder="templates")

from app.admin_mgt.mod_api import ModApi

mod.add_app_template_global(app_api.get_app_root_tpl, name='app_root_tpl')
mod.add_app_template_global(ModApi.get_root_tpl, name='admin_root_tpl')



from app.utilites.code_helper import CodeHelper
from datetime import datetime

from app.onto_mgt.files_managment import FilesManagment

from shutil import rmtree, copyfile

from app.utilites.some_config import SomeConfig
from flask import send_file

import re

from app.onto_mgt.ontology import Ontology




from app.app_api import tsc_query, compile_query, compile_query_result

from urllib.parse import quote, unquote

from rdflib import Graph

@mod.route('/navigation')
#@login_required
def onto_navigation():
    owl_Thing = "http://www.w3.org/2002/07/owl#Thing"


    _onto = unquote(request.args.get('onto') if request.args.get('onto') else "")
    uri = unquote(request.args.get('uri') if request.args.get('uri') else "")

    # codes = get_structure_codes_sparqt("navigation")
    codes = ["query_mgt.navigation.object", "query_mgt.navigation.subject", "query_mgt.navigation.base"]


    if _onto:
        df = FilesManagment()
        onto_path = df.get_dir_realpath("ontos")

        g = Graph().parse(os.path.join(onto_path, _onto), format='ttl')


        if not uri:
        	uri = owl_Thing

        result = {code: compile_query_result( json.loads( g.query(compile_query(code, {"URI" : uri})).serialize(format="json").decode("utf-8") )  ) for code in codes}
    else:
        result = {code: tsc_query(code, {"URI": uri}) for code in codes}




    navigation_base = codes[2]
    navigation_subject = codes[1]
    navigation_object = codes[0]


    navigation_base = result[navigation_base][0] if result[navigation_base] else {}

    navigation_base_uri = navigation_base['o'] if 'o' in navigation_base else ""
    if _onto:
        navigation_base['href'] = url_for('onto.onto_navigation', uri = navigation_base_uri, onto = _onto)
    else:
        navigation_base['href'] = url_for('onto.onto_navigation', uri = navigation_base_uri)


    # ПЕРЕХОД В КАРТОЧКУ УЗЛА
    # if 'o_cls' in navigation_base:
    #     current_class = get_className(navigation_base['o_cls'])
    #     current_class_base = current_class
    #     while not os.path.exists(os.path.join(templates_path, current_class + ".html")):
    #         QUERY = "SELECT ?parent WHERE { %s:%s rdfs:subClassOf ?parent .}" % (ONTOLOGY_NAME, current_class)
    #         parent = _query(QUERY)
    #         if parent:
    #             current_class = get_className(parent[0]['parent'])
    #         else:
    #             break

    #     my_class_object = get_class(current_class_base)
    #     if my_class_object:
    #         navigation_base['href'] = url_for('onto.uri_class', class_object = current_class_base, uri = navigation_base_uri)


    # SUBJECT

    firstPKey = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    secondPKey = 'http://www.w3.org/2000/01/rdf-schema#label'

    firstPKey_data = {}
    secondPKey_data = {}

    subject_P = {}
    subject_O = {}
    subject_P_O = {}

    for item in result[navigation_subject]:
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



    # OBJECT

    object_P = {}
    object_S = {}
    object_P_S = {}

    for item in result[navigation_object]:
        if item['p'] not in list(object_P.keys()):
            object_P[item['p']] = item['p_lbl'] if 'p_lbl' in list(item.keys()) and item['p_lbl'] else item['p']

        if item['s'] not in list(object_S.keys()):
            object_S[item['s']] = item['s_lbl'] if 's_lbl' in list(item.keys()) and item['s_lbl'] else item['s']

        object_P_S[item['s']] = item['p']


    total_object_P_S = {}
    for p_item in object_P:
        total_object_P_S[p_item] = [key for key in object_P_S if object_P_S[key] == p_item]

    if 'o_lbl' not in firstPKey_data and 'o' in firstPKey_data:
        firstPKey_data['o_lbl'] = firstPKey_data['o']
    if 'p_lbl' not in secondPKey_data and 'p' in secondPKey_data:
        secondPKey_data['p_lbl'] = secondPKey_data['p']


    return render_template("/onto_navigation.html",
       base=navigation_base,
       firstPKey=firstPKey_data,
       secondPKey=secondPKey_data,
       total_subject_P_O=total_subject_P_O,
       subject_P=subject_P,
       subject_O=subject_O,
       total_object_P_S=total_object_P_S,
       object_P=object_P,
       object_S=object_S,
       onto = _onto
    )




@mod.route('/ontologies')
#@login_required
def ontologies():
	_base_url = '/' + MOD_NAME

	cols_ontos = [
		{"label": "", "index": "toolbar", "name": "toolbar", "width": 40, "sortable": False, "search": False},
		# {name: 'Type', index: 'Type', label: 'Type', hidden: True, sortable: False}
		{"label": "Тип", "index": "Type", "name": "Type", "hidden": True, "search": False},
		{"label": "ID", "index": "id", "name": "id", "hidden": True, "search": False},
		{"label": "Имя", "index": "name", "name": "Name", "width": 90, "search": True, "stype": 'text',
		 "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
		 },
		{"label": "Дата загрузки", "index": "loaddate", "name": "loaddate", "width": 40, "align": "center",
		 "search": True, 'stype': 'text',
		 "searchoptions": {"sopt": ['cn', 'nc', 'eq', 'ne', 'bw', 'bn', 'ew', 'en']}
		 }
	]

	cfg_ontos = {
		"datatype": "json",
		"mtype": "POST",
		# "colNames": ["-", "id", "Имя", "Дата загрузки", "Карта", "Результат"],
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

	return render_template("/ontos.html", tbl = json.dumps(cfg_ontos))









@mod.route('/getFiles/ontos', methods=['GET', 'POST'])
# @login_required
def get_files():
    """ААААААААААААААААААААААААААААААААААА"""


    dir_name = "ontos"


    answer = {'rows': [], 'page': 1, 'records': 20, 'total': 1}
    page = 1 # get the requested page
    limit = 20 # get how many rows we want to have into the grid
    sidx = 'Name' # get index row - i.e. user click to sort
    sord = 'asc' # get the direction
    search_flag = False
    filters = ''
    # row = {'id': '', 'toolbar': '', 'Type': '', 'Name': '', 'loaddate': '', 'usemap': '', 'loadresult': ''}
    columns_map = {'id': 'name', 'toolbar': 'name', 'Type': 'name', 'name': 'name', 'Name': 'name', 'loaddate': 'mdate', 'usemap': 'map', 'loadresult': 'result'}
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
    # print(file_list)
    if file_list:
        if search_flag:
            file_list = apply_jqgrid_filters(file_list, filters)

        """ теперь после поиска надо отсортировать """
        file_list = df.sort_files(file_list, sord, columns_map[sidx])
        file_list1 = file_list[offset:offset + limit] if len(file_list) > limit else file_list
        """
        array( "label" => "", "index" => "toolbar", "name" => "toolbar", "width" => 120, "sortable" => false),
        array( "label" => "ID", "index" => "id", "name" => "id", "width" => 55 , "hidden" => true),
        array( "label" => "Имя", "index" => "name", "name" => "Name", "width" => 90 ),
        array( "label" => "Дата загрузки", "index" => "loaddate", "name" => "loaddate", "width" => 80, "align" => "center" )
        //array( "name" => "usemap", "width" => 80, "align" => "center" ),
        //array( "name" => "loadresult", "width" => 80, "align" => "center" )
        """

        rows = []
        for item in file_list1:
            row = {'id': '', 'toolbar': '', 'Type': '', 'Name': '', 'loaddate': ''}

            row['id'] = item['name']
            row['Name'] = item['name']
            
            row['loaddate'] = item['mdate'] if 'mdate' in item else ""

            row['Type'] = 'f'
            # if item.is_dir():
            #    row['Type'] = 'd'
            rows.append(row)

    if file_list:
        answer['page'] = page
        answer['records'] = len(file_list)
        answer['total'] = ceil(answer['records'] / limit)
        answer['rows'] = rows
    return json.dumps(answer)







@mod.route('/loadFiles/ontos', methods=['GET', 'POST'])
# # @login_required
def upload_files():
    """ загружаем файлы в определенную директорию """

    dir_name = "ontos"


    answer = {'Msg': '', 'Data': None, 'State': 404}
    args = {"method": "POST"}
    # print('Start upload')
    if request.method == "POST":
        # print('Catch post')
        appended = []
        # answer = {'Status': 500, 'msg': 'No files to save!'}
        answer['Msg'] = 'Нет файлов для сохранения.'
        if request.files and 'File[]' in request.files:
            # print('Catch files')
            file = None # type: werkzeug.datastructures.FileStorage
            errors = []

        
            _existed = []
            _upload_dir = 'temp_upload_' + str(datetime.now())
            _tmp_path = os.path.dirname(os.path.abspath(__file__))
            _tmp_path = os.path.join(_tmp_path, _upload_dir)
            meta = FilesManagment()
            if meta.set_current_dir(dir_name):
                # print('Set directory', dir_name)
                path = meta.get_current_dir()
                flg = False
                cnt = 0
                data = []


                for file in request.files.getlist('File[]'):
                    flg = False
                    # print('try file:', file.filename)
                    if bool(file.filename):
                        # print('save file:', file.filename)
                        # file_bytes = file.read(MAX_FILE_SIZE)
                        # args["file_size_error"] = len(file_bytes) == MAX_FILE_SIZE
                        # сохранялись пустые файлы
                        # решение:
                        # https://stackoverflow.com/questions/28438141/python-flask-upload-file-but-do-not-save-and-use
                        # # snippet to read code below
                        file.stream.seek(0)  # seek to the beginning of file
                        try:
                            # print('try save upload')
                            secure_name = normalize_file_name(file.filename)
                            # print('secure_name', secure_name)
                            file_name = os.path.join(path, secure_name)
                            # print('try save file', file_name)
                            # для начала надо проверить существует ли файл с таким же именем

                            if os.path.exists(file_name):
                                # появился дубликат - создаем директорию загрузки если ее нет
                                if not os.path.exists(_tmp_path):
                                    os.mkdir(_tmp_path)
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



                            # Проверка base_uri
                            _baseURI = getBaseUri(FN)

                            for item in meta.get_dir_source(dir_name):
                                if "fullname" in item:
                                    if getBaseUri(item['fullname']) == _baseURI:
                                    	# удаляем только что загруженный файл!
                                        os.remove(FN)

                                        answer['Msg'] = 'Невозможно загрузить файл. Такой baseURI ({}) уже существует в {}'.format(_baseURI, item['name'])
                                        errors.append('Невозможно загрузить файл. Такой baseURI ({}) уже существует в {}'.format(_baseURI, item['name']))
                                        return json.dumps(answer)




                        except Exception as ex:
                            print(ex)
                            answer['Msg'] = 'Cann`t upload file: {}. Error: {}'.format(file.filename, ex)
                            errors.append('Cann`t upload file: {}. Error: {}'.format(file.filename, ex))
                        if flg:
                            cnt += 1
                            data.append(secure_name)
                            # TODO: Включаем функциональность по добавлению медиа данных для файла если есть
                            

                # print('count saved', cnt)
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
# @login_required
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
            # print('file to remove', name)
            if '' != name:
                flg = False

                flg = meta.remove_file(name, dir_name)
                # print('file is removed', str(flg))
                if flg:
                    # print('Operation dir', dir_name)
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
        else:
            answer['Msg'] = 'Неизвестная директория -> ' + dir_name + '!'
    return json.dumps(answer)









@mod.route('/removeSelection/ontos', methods=['POST'])
# @login_required
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
                """"""
                rp = os.path.join(path, fi)
                if not os.path.exists(rp):
                    continue
                if os.path.isdir(rp):
                    """"""
                    rmtree(rp, ignore_errors=True)
                else:
                    """"""
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
                """ end loop of deleted items """
            if 0 < len(deleted):
                """"""
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
# @login_required
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
            # print('Catch download file: ' + download_file)
            return send_file(download_file, mimetype=mime,
                             as_attachment=True, attachment_filename=download_file_name)
    return render_template("errors/404.html", message=errorMsg)








@mod.route('/accept_newfile/ontos', methods=['POST'])
# @login_required
def accept_new_file():

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
# @login_required
def reject_new_file():

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





def getBaseUri(file_name):
    # Проверка base_uri
    _baseURI = ""
    mfile = open(file_name, "r", encoding="utf-8")
    for line in mfile.readlines():
        baseURI = re.findall(r'^\s*#\s*baseURI:\s*(.*)\s*$', line.strip())
        if baseURI:
            _baseURI = baseURI[0]

    mfile.close()
    return _baseURI






def is_empty_upload_temp(_check_path):
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
    prop = ''
    cols = {'toolbar': '', 'id': 'name', 'name': 'name', 'Name': 'name',
            'loaddate': 'mdate', 'usemap': 'map', 'loadresult': 'result'}
    cols = {'id': 'name', 'toolbar': 'name', 'Type': 'name', 'name': 'name', 'Name': 'name',
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
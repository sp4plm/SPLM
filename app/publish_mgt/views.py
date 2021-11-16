# -*- coding: utf-8 -*-

"""
Модуль публикации данных
"""
import os
import json
from math import ceil
from shutil import copyfile, rmtree
from datetime import datetime

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for

from app import app_api
from app.utilites.jqgrid_helper import JQGridHelper
from app.utilites.code_helper import CodeHelper
from app.admin_mgt.decorators import requires_auth
from .data_backuper import DataBackuper
from .data_publish_logger import DataPublishLogger
from .data_publisher import DataPublisher
from .files_managment_view import FilesManagmentView
from .files_managment import FilesManagment
from .module_conf import PublishModConf

# теперь надо получить API административного модуля
from ..utilites.extend_processes import ExtendProcesses

admin_mod_api = None
admin_mod_api = app_api.get_mod_api('admin_mgt')

mod = Blueprint(PublishModConf.MOD_NAME, __name__, url_prefix=PublishModConf.MOD_WEB_ROOT,
                static_folder=PublishModConf.get_web_static_path(),
                template_folder=PublishModConf.get_web_tpl_path())

_auth_decorator = app_api.get_auth_decorator()


@mod.route('/', methods=['GET'], defaults={'sidenav_view': 'files', 'view_item': 'data'})
@mod.route('/index', methods=['GET'], defaults={'sidenav_view': 'files', 'view_item': 'data'})
@mod.route('/<sidenav_view>', methods=['GET'])
@mod.route('/<sidenav_view>/<view_item>', methods=['GET'])
@_auth_decorator
def index(sidenav_view='files', view_item='data', tool_action=None):
    app_cfg = app_api.get_app_config()

    tmpl_vars = {}
    tmpl_vars['project_name'] = 'Semantic PLM'
    tmpl_vars['title'] = 'Инструмент публикации данных'
    tmpl_vars['page_title'] = 'Инструмент публикации данных'
    tmpl_vars['page_side_title'] = ''
    tmpl_vars['inavi'] = []
    tmpl_vars['dir_name'] = ''
    # надо получить текущего пользователя и получить его роли
    view = FilesManagmentView()
    if g.user:
        data_admin_role = app_cfg.get('data_storages.Manage.adminRole')
        data_oper_role = app_cfg.get('data_storages.Manage.operRole')
        if g.user.has_role(data_oper_role):
            view.set_data_role(data_oper_role)
        if g.user.has_role(data_admin_role):
            view.set_data_role(data_admin_role)
    dirs_list = []
    dirname = view_item
    view.set_current(dirname)
    dirs_list = view.get_navi()
    tbl_json = json.dumps(view.get_jqgrid_config())
    cur_page_title = ""
    for ni in dirs_list:
        if ni['current']:
            cur_page_title = ni['label']
            break

    tmpl_vars['title'] += ":: " + cur_page_title
    tmpl_vars['page_title'] = cur_page_title
    tmpl_vars['tbl'] = tbl_json
    tmpl_vars['dir_name'] = dirname
    tmpl_vars['inavi'] = dirs_list

    return render_template(PublishModConf.get_root_tpl(), **tmpl_vars)


@mod.route('/publish', methods=['POST'])
@_auth_decorator
def publish_proc():
    """"""
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    if 'POST' == request.method:
        # portal_op_modes = OperationMods()
        # if PortalSettings.check_publish_pid_exists():
        #     answer['State'] = 201
        #     answer['Msg'] = 'Процесс публикации уже запущен!'
        #     return json.dumps(answer) # выходим так как процесс запущем

        meta = FilesManagment()

        root_path = os.path.dirname(__file__)
        script = os.path.join(root_path, 'data_publish_process.py')

        check_errors = ''
        check_errors = get_publish_error_file()
        CodeHelper.add_file(check_errors)

        data = None
        data = ExtendProcesses.run(script, [], check_errors)
        # output, errors = data.communicate()
        # print('OUTPUT: =========>', output)
        # print('ERRORS: =========>', errors)
        # По идее надо выполнить код управлением режимами портала и включить режим
        # обновления данных
        # pid_file = PortalSettings.get_publishing_pid_file()
        # with open(pid_file, 'w') as file_p:
        #     file_p.write(str(data))

        answer['State'] = 200
        answer['Msg'] = 'Процесс запущен!'
        answer['Data'] = {'process': str(data)}

    return json.dumps(answer)


def get_publish_error_file():
    check_errors = ''
    data_path = PublishModConf.DATA_PATH
    check_name = 'publish-subproc.errors'
    check_errors = os.path.join(data_path, check_name)
    return check_errors


@mod.route('/publish_proc/step', methods=['POST'])
@_auth_decorator
def publish_process_step():
    """"""
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    if 'POST' == request.method:
        # portal_op_modes = OperationMods()
        # if not PortalSettings.check_publish_pid_exists():
        #     """"""
        #     answer['State'] = 301
        #     answer['Msg'] = 'Процесс публикации незапущен!'
        #     answer['Data'] = None
        #     return json.dumps(answer)

        # требуется получить файл, где содержится актуальное состояние о публикации данных
        process_logger = DataPublishLogger()
        # прочитать содержимое файла
        file_content = process_logger.get_state()
        # вернуть содержимое клиенту
        answer['State'] = 200
        answer['Msg'] = 'Процесс публикации продолжается!'
        answer['Data'] = file_content

        if 'crash_message' in file_content['process'] and '' != file_content['process']['crash_message']:
            answer['State'] = 302
            answer['Msg'] = file_content['process']['crash_message']

        check_errors = ''
        check_errors = get_publish_error_file()
        # надо проверить - если файл не пустой
        file_size = os.stat(check_errors).st_size
        if file_size > 1:
            answer['State'] = 501 # в js будем обрабатывать как аварийное завершение публикации
            answer['Msg'] = 'Ошибка в исполнении! Аварийное завершение публикации'
    return json.dumps(answer)


@mod.route('/publish_proc/error_break', methods=['POST'])
@_auth_decorator
def publish_process_break():
    """"""
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    if 'POST' == request.method:
        # portal_op_modes = OperationMods()
        answer['State'] = 301
        answer['Msg'] = 'Процесс публикации завершен аварийно!'
        answer['Data'] = None
        # if PortalSettings.check_publish_pid_exists():
        #     """"""
        #     pid_file = PortalSettings.get_publishing_pid_file()
        #     os.unlink(pid_file)
        #     check_errors = ''
        #     check_errors = get_publish_error_file()
        #     # надо проверить - если файл не пустой
        #     file_size = os.stat(check_errors).st_size
        #     if file_size > 1:
        #         answer['State'] = 301
        #         answer['Msg'] = CodeHelper.read_file(check_errors)
        #         answer['Data'] = None
    return json.dumps(answer)


@mod.route('/publish_proc/done', methods=['POST'])
@_auth_decorator
def publish_process_done():
    """"""
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    if 'POST' == request.method:
        # portal_op_modes = OperationMods()
        # требуется получить файл, где содержится актуальное состояние о публикации данных
        process_logger = DataPublishLogger()
        if process_logger.get('process.Done'):
            answer['State'] = 200
            answer['Msg'] = 'Процесс публикации завершен!'
            answer['Data'] = ''
            # теперь надо удалить файл pid процесса публикации чтобы все заработало
            # if PortalSettings.check_publish_pid_exists():
            #     pid_file = PortalSettings.get_publishing_pid_file()
            #     os.unlink(pid_file)
            return json.dumps(answer)

        answer['State'] = 301
        answer['Msg'] = process_logger.get('error')[-1]
        answer['Data'] = None
    return json.dumps(answer)


def find_file_in_list(dlist, fname):
    result = None
    if dlist:
        for fi in dlist:
            if fname == fi['name']:
                result = fi
    return result


@mod.route('/getFiles/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def get_files(dir_name=''):
    """hhhh"""
    answer = {'rows': [], 'page': 1, 'records': 20, 'total': 1}
    page = 1 # get the requested page
    limit = 20 # get how many rows we want to have into the grid
    sidx = 'Name' # get index row - i.e. user click to sort
    sord = 'asc' # get the direction
    search_flag = False
    filters = ''

    _app_cfg = app_api.get_app_config()
    USE_NAMED_GRAPHS = False
    USE_NAMED_GRAPHS = CodeHelper.conf_bool(_app_cfg.get('data_storages.Main.use_named_graphs'))

    columns_map = FilesManagmentView.get_columns_map()
    jq_grid = JQGridHelper()
    jq_grid.set_map(columns_map)

    if request.method == "GET":
        page = int(request.args['page']) if 'page' in request.args else page
        limit = int(request.args['rows']) if 'rows' in request.args else limit
        sidx = request.args['sidx'] if 'sidx' in request.args else sidx
        sord = request.args['sord'] if 'sord' in request.args else sord
        if '_search' in request.args:
            search_flag = not ('false' == request.args['_search']) # инверсия от значения
        filters = request.args['filters'] if 'filters' in request.args else filters

        if search_flag and '' == filters:
            """ значит ищем супер поиском """
            filters = jq_grid.search_to_filter_json(request.args)

    if request.method == "POST":
        page = int(request.form['page']) if 'page' in request.form else page
        limit = int(request.form['rows']) if 'rows' in request.form else limit
        sidx = request.form['sidx'] if 'sidx' in request.form else sidx
        sord = request.form['sord'] if 'sord' in request.form else sord
        if '_search' in request.form:
            search_flag = not ('false' == request.form['_search']) # инверсия от значения
        filters = request.form['filters'] if 'filters' in request.form else filters

        if search_flag and '' == filters:
            """ значит ищем супер поиском """
            filters = jq_grid.search_to_filter_json(request.form)

    offset = 0 if 1==page else (page-1)*limit

    file_list = []

    df = FilesManagment()
    file_list = df.get_dir_source(dir_name)
    # print(file_list)
    if file_list:
        if search_flag:
            file_list = jq_grid.apply_jqgrid_filters(file_list, filters)

        """ теперь после поиска надо отсортировать """
        file_list = df.sort_files(file_list, sord, columns_map[sidx])
        file_list1 = file_list[offset:offset + limit] if len(file_list) > limit else file_list

        rows = []
        for item in file_list1:
            row = {'id': '', 'toolbar': '', 'Type': '', 'Name': '', 'loaddate': ''}
            if 'data' == dir_name:
                if USE_NAMED_GRAPHS and df.is_deleted(item):
                    continue
                row['loadresult'] = item['result']
            if 'backups' == dir_name:
                row['cmt'] = item['comment'] if 'comment' in item else ''
            row['id'] = item['name']
            row['Name'] = item['name']
            row['loaddate'] = item['mdate']
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


@mod.route('/backupData', methods=['GET'])
@_auth_decorator
def make_backup():
    """"""
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    meta = FilesManagment()
    portal_cfg = app_api.get_app_config()
    if meta.set_current_dir('backups'):
        endpoint = portal_cfg.get('data_storages.EndPoints.main')
        data_backuper = DataBackuper()
        data_backuper.use_named_graph = CodeHelper.conf_bool(portal_cfg.get('data_storages.Main.use_named_graphs'))
        backup_file = os.path.join(meta.get_dir_realpath('backups'), data_backuper.generate_filename())
        flg_backup = data_backuper.create(backup_file)
        if flg_backup:
            # создали файл резервной копии - надо синхронизировать директорию
            meta.set_current_dir('backups')
            meta.sync_description()
            # теперь укажем что даннаая резервная копия была сделана руками
            call_args = {'comment': 'Cоздана по команде пользователя'}
            name = os.path.basename(backup_file)
            name = os.path.basename(data_backuper.get_last_downloaded_file())
            info_flg = meta.set_file_description(name, call_args)
            # print('update info: ', info_flg)
            answer['State'] = 200
            answer['Msg'] = ''
        else:
            answer['Msg'] = 'Неудалось создать файл резервной копии!'
    else:
        answer['Msg'] = 'Неизвестная директория -> backups!'
    return json.dumps(answer)


@mod.route('/rollbackBackup/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def rollback_backup(dir_name):
    """ восстанавливаем резервную копию """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    if 'POST' == request.method:
        meta = FilesManagment()
        if meta.set_current_dir('backups'):
            portal_cfg = app_api.get_app_config()
            fileroll = request.form['bfile'] if 'bfile' in request.form else ''
            file = os.path.join(meta.get_dir_realpath('backups'), fileroll)
            endpoint = portal_cfg.get('data_storages.EndPoints.main')
            data_backuper = DataBackuper()
            data_backuper.use_named_graph = CodeHelper.conf_bool(portal_cfg.get('data_storages.Main.use_named_graphs'))
            # сперва сделаем резервную копию
            backup_file = os.path.join(meta.get_dir_realpath('backups'), data_backuper.generate_filename())
            flg_backup = data_backuper.create(backup_file)
            if flg_backup:
                meta.set_current_dir('backups')
                meta.sync_description()
                # теперь укажем что даннаая резервная копия была сделана руками
                call_args = {'comment': 'Cоздана автоматически перед восстановлением из резервной копии {}'.format(fileroll)}
                name = os.path.basename(backup_file)
                name = os.path.basename(data_backuper.get_last_downloaded_file())
                meta.set_file_description(name, call_args)
            flg = data_backuper.restore(file)
            answer['Msg'] = 'Не удалось восстановить резервную копию {}!'.format(fileroll)
            if flg:
                answer['State'] = 200
                answer['Msg'] = 'Резрвная копия {} восстановлена успешно!'.format(fileroll)
                # надо выставить метку публикации мекой даты резервной копии -так как данные
                # $pdt['y'] .'-' .$pdt['mon'] .'-'.$pdt['d'].' '.$pdt['h'].':'.$pdt['min'].':'.$pdt['s'];
                pdt = _get_dt_from_filename(fileroll)
                new_publish_time = datetime(pdt['y'], pdt['mon'], pdt['d'], pdt['h'], pdt['min'], pdt['s'])
                data_publisher = DataPublisher()
                data_publisher.set_backup_time_to_publish(new_publish_time.timestamp())
        else:
            answer['Msg'] = 'Неизвестная директория -> backups!'
    return json.dumps(answer)


@mod.route('/removeSelection/<dir_name>', methods=['POST'])
@_auth_decorator
def remove_selection(dir_name):
    """ сохраняем изменения связанные с файлом """
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
                """"""
                os.unlink(rp)
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


@mod.route('/removeFile/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def remove_file(dir_name):
    """ сохраняем изменения связанные с файлом """
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


@mod.route('/editFile/<dir_name>', methods=['POST'])
@_auth_decorator
def edit_file(dir_name):
    """ сохраняем изменения связанные с файлом """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    if 'POST' == request.method:
        meta = FilesManagment()
        if meta.set_current_dir(dir_name):
            path = meta.get_current_dir()
            name = request.form['FileName'].strip() if 'FileName' in request.form else ''
            # TODO: переписать редактирование файла
            oname = request.form['OldName'] if 'OldName' in request.form else ''
            if request.files and 'File' in request.files:
                """ замена файла """
                # file = request.files['File']
                # flg = meta.edit_file(oname, name, file, dir_name)
                # if bool(file.filename):
                #     name = file.filename if '' == name else name
                #     # file_bytes = file.read(MAX_FILE_SIZE)
                #     # if len(file_bytes) >= MAX_FILE_SIZE:
                #     #     answer['Msg'] = 'File size error! (Max Size: {})'.format(MAX_FILE_SIZE)
                #     #     answer['State'] = 400
                #     #     file = None
                #     flg1 = meta.remove_file(name, dir_name)
                #
                # else:
                #     answer['Msg'] = 'File name error: undefined uploaded file!'
                #     answer['State'] = 400
                #     file = None
            else:
                """ простое переименование """
                # answer['State'] = 200
                # answer['Msg'] = ''
                # answer['Data'] = {'file': oname}
                # if oname != name and '' != name:
                #     meta.rename_file(oname, name, dir_name)
                #     answer['Data'] = {'file': name}
        else:
            answer['Msg'] = 'Неизвестная директория -> ' + dir_name + '!'
    return json.dumps(answer)


@mod.route('/downloadFile/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def download_file(dir_name):
    """ отдаем файл на скачивание """
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
            from flask import send_file
            return send_file(download_file, mimetype=mime,
                             as_attachment=True, attachment_filename=download_file_name)
    return render_template("errors/404.html", message=errorMsg)


@mod.route('/loadFiles/<dir_name>', methods=['POST'])
@_auth_decorator
def upload_files(dir_name):
    """ загружаем файлы в определенную директорию """
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
            # теперь надо поддержать функциональность для медиа
            errors = []
            _existed = []
            _upload_dir = 'temp_upload_' + str(datetime.now())
            _tmp_path = PublishModConf.DATA_PATH
            _tmp_path = os.path.join(_tmp_path, _upload_dir)
            meta = FilesManagment()
            if meta.set_current_dir(dir_name):
                # print('Set directory', dir_name)
                path = meta.get_current_dir()
                flg = False
                cnt = 0
                data = []
                # print(request.files.getlist('File'))
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
                            secure_name = _normalize_file_name(file.filename)
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
                                flg = _save_uploaded_file(file, _tmp_name)
                                file_existed.append(_tmp_name) # новый загружаемый файл
                                file_existed.append(_tmp_path) # рабочая директория загрузки
                                _existed.append(file_existed)
                            else:
                                flg = _save_uploaded_file(file, file_name)
                        except Exception as ex:
                            answer['Msg'] = 'Cann`t upload file: {}. Error: {}'.format(file.filename, ex)
                            errors.append('Cann`t upload file: {}. Error: {}'.format(file.filename, ex))
                        if flg:
                            cnt += 1
                            data.append(secure_name)
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


def str_key_2_struct(str_key, val):
    """"""
    ll = len(str_key)
    _struct = None
    list_k = ''
    dict_k = ''
    read_list_k = False
    read_dict_k = False
    for chi in range(0, ll):
        if '[' == str_key[chi]:
            # start list
            _struct = []
            read_list_k = True
        if ']' == str_key[chi]:
            read_list_k = False
        if '{' == str_key[chi]:
            # start list
            _struct = []
            read_dict_k = True
        if '}' == str_key[chi]:
            read_dict_k = False
        if read_list_k:
            list_k += str_key[chi]
        if read_dict_k:
            dict_k += str_key[chi]


def clear_upload_temp(_check_path):
    if CodeHelper.check_dir(_check_path) and CodeHelper.is_empty_dir(_check_path):
        rmtree(_check_path)  # удаляем ненужную директорию


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

@mod.route('/accept_newfile/<dir_name>', methods=['POST'])
@_auth_decorator
def accept_new_file(dir_name):
    answer = {'Msg': '', 'Data': None, 'State': 404}
    # print(request.form)
    _app_cfg = app_api.get_app_config()
    USE_NAMED_GRAPHS = False
    USE_NAMED_GRAPHS = CodeHelper.conf_bool(_app_cfg.get('data_storages.Main.use_named_graphs'))
    recive_data = reqform_2_dict(request.form)
    # print(recive_data)
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
        if 'data' == dir_name:
            dir_files = meta.get_dir_source(dir_name)
            save_map = os.path.join(_upload_temp, 'set_map')
            map = ''
            map = CodeHelper.read_file(save_map)
            call_args = {'map': map}
            for fi in dir_files:
                # имя файла не в загружаемых и не в повторках(дубликатах, созданных)
                if fi['name'] not in existed_names:
                    continue
                #print('Operate file - ', fi['name'])
                # теперь надо разобраться с результатом
                file_info = meta.get_item_description(dir_name, fi['name'])
                if '' != file_info['result']:
                    #print('Catch result')
                    meta_res = FilesManagment()
                    meta_res.set_current_dir('res')
                    if USE_NAMED_GRAPHS:
                        #print('Used Named')
                        call_args2 = {'deleted': True}
                        flg = meta_res.set_file_description(file_info['result'], call_args2)
                        #print('Try update description {} - set {} | Result: {}'.format(file_info['result'], str(call_args2), str(flg)))
                        meta.set_current_dir(dir_name)
                    else:
                        #print('remove item')
                        meta_res.remove_item('res', file_info['result'])
                    #print('End operate with result file')
                    call_args['result'] = ''
                    flg = meta.set_file_description(fi['name'], call_args)
                    #print('Try update description {} - set {} | Result: {}'.format(fi['name'], str(call_args), str(flg)))
                #print('Operate one file DONE =========================================!')
        answer['Data'] = proc
        answer['State'] = 200
        answer['Msg'] = ''
        # проверим пуста ли временная директория загрузки файлов
        if is_empty_upload_temp(_upload_temp):
            rmtree(_upload_temp) # удаляем поскольку пуста
    return json.dumps(answer)


@mod.route('/reject_newfile/<dir_name>', methods=['POST'])
@_auth_decorator
def reject_new_file(dir_name):
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


@mod.route('/getDirSource/<dir_name>', methods=['GET', 'POST'])
@_auth_decorator
def get_dir_source(dir_name):
    """ выбираем файлы для отображения в таблице """
    answer = []
    meta_data = FilesManagment()
    files = meta_data.get_dir_source(dir_name)
    if files:
        for fi in files:
            if 'maps' == dir_name:
                is_active = False
                is_active = fi['active'] if 'active' in fi else False
                if not is_active:
                    continue
            answer.append(fi['name'])
    return json.dumps(answer)


@mod.route('/getLastPublishTime', methods=['GET'])
@_auth_decorator
def get_last_publish_time():
    answer = {}

    data_publisher = DataPublisher()
    _time = data_publisher.get_last_publish_time()
    answer['State'] = 200
    answer['Msg'] = ''
    answer['publish_time'] = _time
    return json.dumps(answer)


@mod.route('/getLastBackupTime', methods=['GET'])
@_auth_decorator
def get_last_backup_time():
    answer = {}
    meta = FilesManagment()
    files = meta.get_dir_source('backups')
    answer['State'] = 200
    answer['Msg'] = ''
    answer['backup_time'] = '--'
    if files:
        """ sorting by mdate and get last """
        files = sorted(files, key=lambda x: x['mdate'])
        try_date = files[-1]['name']
        pdt = _get_dt_from_filename(try_date)
        mon = pdt['mon']
        if 10 > mon:
            mon = '0' + str(mon)
        d = pdt['d']
        if 10 > d:
            d = '0' + str(d)
        answer['State'] = 200
        answer['Msg'] = ''
        answer['backup_time'] = str(pdt['y']) +'-' +str(mon) +'-'+str(d)+' '+str(pdt['h'])+':'+str(pdt['min'])+':'+str(pdt['s'])
    return json.dumps(answer)


def _get_dt_from_filename(filename):
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


def _normalize_file_name(file_name):
    res = file_name
    res = '_'.join(res.split(' '))
    res = _translit_rus_string(res)
    return res


def _translit_rus_string(ru_str):
    res = CodeHelper.translit_rus_string(ru_str)
    return res


def _edit_file(self, file_name, new_name='', http_file=None, dirname=''):
    path = self._get_path(dirname)
    file = os.path.join(path, file_name)
    flg = False
    if os.path.exists(file):
        # заменить
        if http_file is not None:
            # только замена
            if '' == new_name or new_name == file_name:
                new_name = file_name # для переименования нового загруженного файла
            try:
                self.save_uploaded_file(http_file, dirname)
                flg = True
            except Exception as ex:
                flg = False
                # print(str(ex))
                raise Exception(str(ex))
            if flg:
                flg = self.remove_file(file_name, dirname) # удалять надо если сохранили
            # если удалили старый файл и сохранили новый
            if flg:
                # теперь для переименования мы должны использовать
                # имя сохраненного файла
                file_name = self.secure_file_name(http_file.filename)
        # переименование
        if '' != new_name:
            flg = self.rename_file(file_name, new_name, dirname)
    return flg


def _rename_file(self, file, new_name, parent_dir=''):
    path = self._get_path()
    if '' != parent_dir:
        path += os.path.sep + parent_dir
    if '' != file:
        file = os.path.join(path, file)
    if '' != new_name:
        new_name = self.secure_file_name(new_name)
        new_name = os.path.join(path, new_name)
    return self._rename_fsi(file, new_name)


def _remove_file(self, name, dirname=''):
    dirname = self._get_path(dirname)
    file = os.path.join(dirname, name)
    flg = False
    if os.path.exists(file) and os.path.isfile(file):
        os.remove(file)
        flg = True
    return flg


def _save_uploaded_file(http_file, file_name=''):
    flg = True
    if http_file:
        work_file = file_name
        if not os.path.exists(work_file):
            http_file.save(work_file)
            flg = True
    return flg

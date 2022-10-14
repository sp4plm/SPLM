# -*- coding: utf-8 -*-

"""
Встроенный модуль управления данными портала
"""
import json
import os
from math import ceil
from shutil import copyfile, rmtree
from datetime import datetime

from flask import Blueprint, g, request
from app import app_api
from .data_backuper import DataBackuper
from .data_publisher import DataPublisher
from .section_view import SectionView
from ..utilites.code_helper import CodeHelper
from ..utilites.extend_processes import ExtendProcesses
from ..utilites.jqgrid_helper import JQGridHelper

from .mod_utils import ModUtils
from .files_management import FilesManagement
from .data_publish_logger import DataPublishLogger

_mod_name = ModUtils().get_mod_name()
_w_pth = app_api.get_mod_data_path(_mod_name)
if not os.path.exists(_w_pth):
    os.mkdir(_w_pth)

mod = Blueprint(_mod_name, __name__,
                url_prefix=ModUtils().get_web_prefix(),
                static_folder=ModUtils().get_web_static_path(),
                template_folder=ModUtils().get_web_tpl_path())

_auth_decorator = app_api.get_auth_decorator()

# { publishing


@mod.route('/publish', methods=['POST'])
@_auth_decorator
def publish_proc():
    """"""
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'

    # portal_op_modes = OperationMods()
    # if PortalSettings.check_publish_pid_exists():
    #     answer['State'] = 201
    #     answer['Msg'] = 'Процесс публикации уже запущен!'
    #     return json.dumps(answer) # выходим так как процесс запущем

    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)
    _mod_utils = ModUtils()

    root_path = os.path.dirname(__file__)
    script = os.path.join(root_path, 'data_publish_process.py')

    check_errors = ''
    check_errors = __get_publish_error_file()
    CodeHelper.add_file(check_errors)

    data = None
    data = ExtendProcesses.run(script, [], check_errors)
    # output, errors = data.communicate()
    # print('OUTPUT: =========>', output)
    # print('ERRORS: =========>', errors)
    # По идее надо выполнить код управлением режимами портала и включить режим
    # обновления данных
    _mod_utils.set_publishing_pid(data.pid)
    # pid_file = _mod_utils.get_publishing_pid_file()
    # with open(pid_file, 'w') as file_p:
    #     file_p.write(str(data))

    answer['State'] = 200
    answer['Msg'] = 'Процесс запущен!'
    answer['Data'] = {'process': str(data)}

    return json.dumps(answer)


def __get_publish_error_file():
    check_errors = ''
    _mod_utils = ModUtils()
    data_path = app_api.get_mod_data_path(_mod_utils.get_mod_name())
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
        check_errors = __get_publish_error_file()
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
        _admin_mgt_api = app_api.get_mod_api('admin_mgt')
        _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
        _portal_mode = None
        _mode_name = ModUtils().get_portal_mode_name()
        if _portal_modes_util is not None:
            _portal_mode = _portal_modes_util.get_current(_mode_name)
        if _portal_mode is not None:
            try:
                _portal_mode.disable()
            except Exception as ex:
                if _portal_modes_util is not None:
                    _portal_modes_util.drop(_portal_mode)
            pass

        _pub_file_result = ModUtils().get_publish_result_file()
        publish_result = None
        if os.path.exists(_pub_file_result):
            from app.mod_portaldata.process_logger import ProcessLogger
            publish_result = ProcessLogger()
            publish_result.set_log_file(_pub_file_result)
            publish_result.write('Процесс публикации завершен с ошибкой:')

        ModUtils().drop_publishing_pid_file()

        check_errors = ''
        check_errors = __get_publish_error_file()
        # надо проверить - если файл не пустой
        file_size = os.stat(check_errors).st_size
        if file_size > 1:
            if publish_result is not None:
                publish_result.write(CodeHelper.read_file(check_errors))
            answer['State'] = 301
            answer['Msg'] = CodeHelper.read_file(check_errors)
            answer['Data'] = None
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

            _admin_mgt_api = app_api.get_mod_api('admin_mgt')
            _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
            _portal_mode = None
            _mode_name = ModUtils().get_portal_mode_name()
            if _portal_modes_util is not None:
                _portal_mode = _portal_modes_util.get_current(_mode_name)
            if _portal_mode is not None:
                try:
                    _portal_mode.disable()
                except Exception as ex:
                    if _portal_modes_util is not None:
                        _portal_modes_util.drop(_portal_mode)
                pass
            ModUtils().drop_publishing_pid_file()
            return json.dumps(answer)

        answer['State'] = 301
        answer['Msg'] = process_logger.get('error')[-1]
        answer['Data'] = None
    return json.dumps(answer)


@mod.route('/publishing')
@_auth_decorator
def __publish_proc_info():
    _tpl_vars = {}
    _tpl_vars['title'] = "Информация о процессе публикации данных"
    _tpl_vars['base_url'] = mod.url_prefix
    _tpl_name = os.path.join('portaldata_mgt', 'process.html')
    return app_api.render_page(_tpl_name, **_tpl_vars)
# } publishing


@mod.route('/removeSelection/<section>', methods=['POST'])
@_auth_decorator
def remove_selection(section):
    """ сохраняем изменения связанные с файлом """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    # все значения полей под тменами полей делает списками
    # требуется если для одного поля требуется обработать несколько значений
    form_dict = request.form.to_dict(flat=False)
    items = form_dict['items[]'] if 'items[]' in form_dict else []
    deleted = []

    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)
    _mod_utils = ModUtils()
    path = _fm.get_section_path(section)
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
            # теперь синхронизируем описание директории
            _fm.sync_section_content(section)
        else:
            answer['Msg'] = 'Не удалось удалить данные!'
    return json.dumps(answer)


@mod.route('/removeFile/<section>', methods=['POST'])
@_auth_decorator
def remove_file(section):
    """ сохраняем изменения связанные с файлом """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'

    name = request.form['file'].strip() if 'file' in request.form else ''

    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)
    _mod_utils = ModUtils()
    path = _fm.get_section_path(section)
    portal_cfg = app_api.get_app_config()
    # print('file to remove', name)
    if '' != name:
        flg = False
        flg = _fm.remove_section_file(section, name)
        # print('file is removed', str(flg))
        if flg:
            # print('Operation dir', dir_name)
            answer['State'] = 200
            answer['Msg'] = ''
            answer['Data'] = {'file': name}
        else:
            msg = ''
            if '' != answer['Msg']:
                msg = ' (' +answer['Msg'] + ')'
            answer['Msg'] = 'Не удалось удалить файл "{}"!{}'.format(name,msg)
            # а что если залипло описание
            # find_files = meta.search_files_by_descr(dir_name, {'name': name})
            # # если нашли файлы в описании
            # if find_files:
            #     meta.sync_description()
            #     find_files = meta.search_files_by_descr(dir_name, {'name': name})
            #     if 0 == len(find_files):
            #         answer['State'] = 200
            #         answer['Msg'] = ''
            #         answer['Data'] = {'file': name}
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
    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)
    _mod_utils = ModUtils()
    files = _fm.get_section_content('backups')
    answer['State'] = 200
    answer['Msg'] = ''
    answer['backup_time'] = '--'
    if files:
        """ sorting by mdate and get last """
        files = sorted(files, key=lambda x: x['mdate'])
        try_date = files[-1]['name']
        pdt = _mod_utils.get_dt_from_filename(try_date)
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


@mod.route('/getDirSource/<section>', methods=['GET', 'POST'])
@_auth_decorator
def get_dir_source(section):
    """ выбираем файлы для отображения в таблице """
    answer = []
    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)
    _mod_utils = ModUtils()
    files = _fm.get_section_content(section)
    if files:
        for fi in files:
            if 'maps' == section:
                is_active = False
                is_active = fi['active'] if 'active' in fi else False
                if not is_active:
                    continue
            answer.append(fi['name'])
    return json.dumps(answer)


# custom backup section {


@mod.route('/backupData', methods=['GET'])
@_auth_decorator
def make_backup():
    """"""
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    section = 'backups'
    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)
    _mod_utils = ModUtils()
    path = _fm.get_section_path(section)
    portal_cfg = app_api.get_app_config()
    flg_backup = False
    endpoint = portal_cfg.get('data_storages.EndPoints.main')
    # data_backuper = DataBackuper()
    # data_backuper.use_named_graph = CodeHelper.conf_bool(portal_cfg.get('data_storages.Main.use_named_graphs'))
    # backup_file = os.path.join(meta.get_dir_realpath('backups'), data_backuper.generate_filename())
    # flg_backup = data_backuper.create(backup_file)
    if flg_backup:
    #     # создали файл резервной копии - надо синхронизировать директорию
    #     meta.set_current_dir('backups')
    #     meta.sync_description()
    #     # теперь укажем что даннаая резервная копия была сделана руками
    #     call_args = {'comment': 'Cоздана по команде пользователя'}
    #     name = os.path.basename(backup_file)
    #     name = os.path.basename(data_backuper.get_last_downloaded_file())
    #     info_flg = meta.set_file_description(name, call_args)
        # print('update info: ', info_flg)
        answer['State'] = 200
        answer['Msg'] = ''
    else:
        answer['Msg'] = 'Неудалось создать файл резервной копии!'
    return json.dumps(answer)


@mod.route('/rollbackBackup', methods=['POST'], defaults={'section': ''})
@mod.route('/rollbackBackup/<section>', methods=['POST'])
@_auth_decorator
def rollback_backup(section=''):
    """ восстанавливаем резервную копию """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['State'] = 500
    answer['Msg'] = 'Нет данных'
    if 'POST' == request.method:
        section = 'backups'
        _w_pth = app_api.get_mod_data_path('portaldata_mgt')
        _fm = FilesManagement(_w_pth)
        _mod_utils = ModUtils()
        path = _fm.get_section_path(section)
        _cfg = _mod_utils.get_config()
        if os.path.exists(path):
            portal_cfg = app_api.get_app_config()
            fileroll = request.form['bfile'] if 'bfile' in request.form else ''
            file = os.path.join(path, fileroll)
            endpoint = portal_cfg.get('data_storages.EndPoints.main')
            data_backuper = DataBackuper()
            data_backuper.use_named_graph = CodeHelper.conf_bool(_cfg['Main']['use_named_graphs'])
            # сперва сделаем резервную копию
            backup_file = os.path.join(path, data_backuper.generate_filename())
            flg_backup = data_backuper.create(backup_file)
            if flg_backup:
                _fm.sync_section_content(section)
                # теперь укажем что даннаая резервная копия была сделана руками
                call_args = {'comment': 'Cоздана автоматически перед восстановлением из резервной копии {}'.format(fileroll)}
                name = os.path.basename(backup_file)
                name = os.path.basename(data_backuper.get_last_downloaded_file())
                _fm.update_section_file(section, name, call_args)
            flg = data_backuper.restore(file)
            answer['Msg'] = 'Не удалось восстановить резервную копию {}!'.format(fileroll)
            if flg:
                answer['State'] = 200
                answer['Msg'] = 'Резрвная копия {} восстановлена успешно!'.format(fileroll)
                # надо выставить метку публикации мекой даты резервной копии -так как данные
                # $pdt['y'] .'-' .$pdt['mon'] .'-'.$pdt['d'].' '.$pdt['h'].':'.$pdt['min'].':'.$pdt['s'];
                pdt = _mod_utils.get_dt_from_filename(fileroll)
                new_publish_time = datetime(pdt['y'], pdt['mon'], pdt['d'], pdt['h'], pdt['min'], pdt['s'])
                data_publisher = DataPublisher()
                data_publisher.set_backup_time_to_publish(new_publish_time.timestamp())
        else:
            answer['Msg'] = 'Неизвестная директория -> backups!'
    return json.dumps(answer)
# custom backup section }


@mod.route('/accept_newfile/<section>', methods=['POST'], strict_slashes=False)
@_auth_decorator
def accept_new_file(section):
    answer = {'Msg': '', 'Data': None, 'State': 404}
    # print(request.form)
    _mod_utils = ModUtils()
    _app_cfg = app_api.get_app_config()
    _cfg = _mod_utils.get_config()
    USE_NAMED_GRAPHS = False
    USE_NAMED_GRAPHS = CodeHelper.conf_bool(_cfg['Main']['use_named_graphs'])
    recive_data = _mod_utils.reqform_2_dict(request.form)
    # print(recive_data)
    files = recive_data['exfiles'] if 'exfiles' in recive_data else list(recive_data.values())
    # meta = FilesManagment()
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
        if _mod_utils.is_empty_upload_temp(_upload_temp):
            rmtree(_upload_temp, ignore_errors=True) # удаляем поскольку пуста
    return json.dumps(answer)


@mod.route('/reject_newfile/<section>', methods=['POST'], strict_slashes=False)
@_auth_decorator
def __reject_new_files(section):
    answer = {'Msg': '', 'Data': None, 'State': 404}
    _mod_utils = ModUtils()
    recive_data = _mod_utils.reqform_2_dict(request.form)
    files = recive_data['exfiles'] if 'exfiles' in recive_data else list(recive_data.values())
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
        if _mod_utils.is_empty_upload_temp(_upload_temp):
            rmtree(_upload_temp, ignore_errors=True) # удаляем поскольку пуста
    return json.dumps(answer)


@mod.route('/loadFiles/<section>', methods=['POST'], strict_slashes=False)
@_auth_decorator
def __upload_files(section):
    """ загружаем файлы в определенную директорию """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    args = {"method": "POST"}
    answer['Msg'] = 'Нет файлов для сохранения.'
    if request.files and 'File[]' in request.files:
        # print('Catch files')
        file = None # type: werkzeug.datastructures.FileStorage
        errors = []  # ошибки при попытке сохранить фалы

        _upload_dir = 'temp_upload_' + str(datetime.now())

        _w_pth = app_api.get_mod_data_path('portaldata_mgt')
        _fm = FilesManagement(_w_pth)
        _tmp_path = os.path.join(_w_pth, _upload_dir)
        _mod_utils = ModUtils()
        path = _fm.get_section_path(section)
        errors = []  # ошибки при попытке сохранить фалы
        _existed = []  # список загружаемых файлов совпадающих по имени
        cnt = 0  # подсчет количество успешно сохраненных файлов
        data = []  # список имен, успешно сохраненных файлов
        # print(request.files.getlist('File'))
        for file in request.files.getlist('File[]'):
            flg = False
            # print('try file:', file.filename)
            if bool(file.filename):
                # print('save file:', file.filename)
                # file_bytes = file.read(MAX_FILE_SIZE)
                # args["file_size_error"] = len(file_bytes) == MAX_FILE_SIZE
                # сохранялись пустые файлы ???
                # решение:
                # https://stackoverflow.com/questions/28438141/python-flask-upload-file-but-do-not-save-and-use
                # # snippet to read code below
                file.stream.seek(0)  # seek to the beginning of file
                try:
                    # print('try save upload')
                    secure_name = _mod_utils.normalize_file_name(file.filename)
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

                        file_name = os.path.join(_tmp_path, secure_name + '_tmp')
                        if os.path.exists(file_name):
                            os.unlink(file_name)
                        file_existed.append(file_name) # новый загружаемый файл
                        file_existed.append(_tmp_path) # рабочая директория загрузки
                        _existed.append(file_existed)
                    flg = _mod_utils.save_uploaded_file(file, file_name)
                except Exception as ex:
                    answer['Msg'] = 'Cann`t upload file: {}. Error: {}'.format(file.filename, ex)
                    print('Uplad file exception: ' + str(ex.args))
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
            _fm.sync_section_content(section)
        if 0 < len(_existed):
            answer['Existed'] = _existed
            answer['State'] = 200
            answer['Msg'] = ''
    # проверяем создана ли директория и если создана и пустая удаляем
    if CodeHelper.check_dir(_tmp_path) and CodeHelper.is_empty_dir(_tmp_path):
        rmtree(_tmp_path) # удаляем ненужную директорию

    return json.dumps(answer)


@mod.route('/downloadFile/<section>', methods=['GET'])
@_auth_decorator
def download_file(section):
    """ отдаем файл на скачивание """
    errorMsg = 'Неизвестный файл для скачивания!'
    filename = request.args['file']
    path = ''
    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)
    _mod_utils = ModUtils()
    path = _fm.get_section_path(section)
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
    return app_api.render_page(os.path.join('errors', '404.html'), message=errorMsg)


@mod.route('/section/<section>', methods=['GET'], strict_slashes=False)
@_auth_decorator
def __section_view(section):
    _tpl_var = {}
    _tpl_var['title'] = 'Инструмент публикации данных'
    _tpl_var['page_title'] = section
    _tpl_var['page_side_title'] = ''
    _tpl_var['inavi'] = []
    _tpl_var['dir_name'] = ''
    _tpl_var['dir_name'] = section
    _tpl_name = ''
    _html = 'portaldata_mgt'

    _mod_utils = ModUtils()

    _tpl_var['pub_result_messages'] = []
    _publish_result = _mod_utils.get_publish_result_file()
    if os.path.exists(_publish_result):
        _lines = []
        with open(_publish_result, 'r', encoding='UTF-8') as  _fh:
            _lines = _fh.readlines()
        if _lines:
            _tpl_var['pub_result_messages'] = _lines

    _cfg = _mod_utils.get_config()
    _cur_user = None
    if g.user:
        _cur_user = g.user
    _tpl_var['inavi'] = _mod_utils.get_navi(_cur_user)
    _current_navi = {}
    for _n in _tpl_var['inavi']:
        if _n['href'].endswith('/' + section):
            _current_navi = _n
            break
    if _current_navi:
        _tpl_var['page_title'] = _current_navi['label']

    _cur_section = SectionView(section)
    _view_tbl = _cur_section.get_jqgrid_config()
    _view_tbl['url'] = mod.url_prefix + '/' + _view_tbl['url'].lstrip('/')
    # теперь нужно составить представление для каждой секции
    # знаем что каждая секция это реестр файлов
    # следовательно каждое представление это таблица с общими и \частными калонками и частной функциональностью
    # общие колонки - имя файла и дата загрузки

    _tpl_var['base_url'] = mod.url_prefix
    _tpl_var['tbl'] = json.dumps(_view_tbl)
    _tpl_name = os.path.join('portaldata_mgt', 'index.html')
    return app_api.render_page(_tpl_name, **_tpl_var)


@mod.route('/section/<section>/list', methods=['POST'], strict_slashes=False)
@_auth_decorator
def __section_list(section):
    _answer = {'rows': [], 'page': 1, 'records': 20, 'total': 1}
    page = 1 # get the requested page
    limit = 20 # get how many rows we want to have into the grid
    sidx = 'Name' # get index row - i.e. user click to sort
    sord = 'asc' # get the direction
    search_flag = False
    filters = ''
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _cur_section = SectionView(section)

    USE_NAMED_GRAPHS = CodeHelper.conf_bool(_cfg['Main']['use_named_graphs'])

    columns_map = _cur_section.get_columns_map()
    jq_grid = JQGridHelper()
    jq_grid.set_map(columns_map)
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

    if not search_flag:
        filters = None

    offset = 0 if 1==page else (page-1)*limit

    _records = [] # список записей реестра секции
    # testing code {

    # get section path
    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)

    _records = _fm.get_section_content(section, filters, start=offset, count=limit, sort=columns_map[sidx], sord=sord)
    _count = _fm.count_section_content(section, filters)

    # testing code }

    rows = []
    for item in _records:
        row = {'id': '', 'toolbar': '', 'Type': '', 'Name': '', 'loaddate': ''}
        # if 'res' == section:
        #     if USE_NAMED_GRAPHS and _cur_section.is_deleted(item):
        #         continue
        #     row['loadresult'] = item['result']
        if 'backups' == section:
            row['cmt'] = item['comment'] if 'comment' in item else ''
        row['id'] = item['name']
        row['Name'] = item['name']
        row['loaddate'] = item['mdate']
        row['Type'] = 'f'
        rows.append(row)

    if _records:
        _answer['page'] = page
        _answer['records'] = _count
        _answer['total'] = ceil(_answer['records'] / limit)
        _answer['rows'] = rows
    return json.dumps(_answer)


@mod.route('/', methods=['GET'], strict_slashes=False)
@_auth_decorator
def __index():
    _tpl_var = {}
    _tpl_var['title'] = 'Инструмент публикации данных'
    _tpl_var['page_title'] = 'Инструмент публикации данных'
    _tpl_var['page_side_title'] = ''
    _tpl_var['inavi'] = []
    _tpl_var['dir_name'] = ''
    _tpl_name = ''
    _html = 'portaldata_mgt'
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    # print('views.__index->_cfg', _cfg)
    # print('views.__index->_cfg[\'Main\'][\'work_sections\']', _cfg['Main']['work_sections'])
    _cur_user = None
    if g.user:
        _cur_user = g.user
    _tpl_var['inavi'] = _mod_utils.get_navi(_cur_user)
    #  на основании навигации можно вывести описание блока для каждого пункта
    _tpl_name = os.path.join('portaldata_mgt', 'index.html')
    return app_api.render_page(_tpl_name, **_tpl_var)

# tools {


@mod.route('/tools/publish_result/export', methods=['POST', 'GET'])
def __export_publish_result():
    _answer = {'Msg': '', 'Data': None, 'State': 500}
    _mod_utils = ModUtils()
    _pub_file_result = _mod_utils.get_publish_result_file()
    _answer['Msg'] = 'Отсутствует файл с результатом!'
    publish_result = None
    if os.path.exists(_pub_file_result):
        _lines = []
        _answer['State'] = 300
        _answer['Msg'] = 'Файл с результатом публикации пуст!'
        with open(_pub_file_result, 'r', encoding='UTF-8') as _fh:
            _lines = _fh.readlines()
        if _lines:
            _answer['State'] = 200
            _answer['Msg'] = ''
            _answer['Data'] = _lines
    return json.dumps(_answer)


@mod.route('/tools/publish_result/clear', methods=['POST', 'GET'])
def __clear_publish_result():
    _answer = {'Msg': '', 'Data': None, 'State': 500}
    _mod_utils = ModUtils()
    _pub_file_result = _mod_utils.get_publish_result_file()
    _answer['Msg'] = 'Отсутствует файл с результатом!'
    publish_result = None
    if os.path.exists(_pub_file_result):
        _lines = []
        _answer['State'] = 300
        _answer['Msg'] = ''
        with open(_pub_file_result, 'w', encoding='UTF-8') as _fh:
            _fh.write('')
        os.unlink(_pub_file_result)
        _answer['State'] = 200
        _answer['Msg'] = 'Clear and remove publish result file!'
    return json.dumps(_answer)


@mod.route('/tools/drop_publish')
def __drop_publish():
    """
    Функция для сброса процесса публикации
    :return:
    """
    _html_lst = []
    _html = ''
    _html_lst.append('Try drop current publication!')
    from app.mod_portaldata.process_logger import ProcessLogger
    from app.mod_portaldata.data_publish_logger import DataPublishLogger
    _mod_utils = ModUtils()
    _pid = _mod_utils.get_publishing_pid()
    _html_lst.append('Catch subprocess PID -> ' + str(_pid))
    _pub_file_result = _mod_utils.get_publish_result_file()
    publish_result = None
    if os.path.exists(_pub_file_result):
        publish_result = ProcessLogger()
        publish_result.set_log_file(_pub_file_result)
    if _pid:
        try:
            """
            записать в файл результата публикации - принудительная остановка публикации пользователем
            остановить все запущенные режимы
            записать что публикация закончена в файл прогресса
            """
            _flg = ExtendProcesses.stop(_pid)
            process_protocol = ProcessLogger()
            _admin_mgt_api = app_api.get_mod_api('admin_mgt')
            _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
            mod_data_path = app_api.get_mod_data_path(_mod_utils.get_mod_name())
            protocol_file = os.path.join(mod_data_path, 'publish.protocol')
            process_protocol.set_log_file(protocol_file)
            _portal_mode = None
            _mode_name = _mod_utils.get_portal_mode_name()
            #  теперь требуется завершить все режимы портала, связанные с публикацией
            if _portal_modes_util is not None:
                _pre_publish_mode = _portal_modes_util.get_current('publish_prepare')
            # режим подготовки к публикации {
            if _pre_publish_mode is not None:
                _html_lst.append('Try to disable "pre_publishing" mode')
                process_protocol.write(mod.name + '.views.__drop_publish: Enabled "pre_publishing" mode!')
                try:
                    _pre_publish_mode.disable()
                    process_protocol.write(mod.name + '.views.__drop_publish: "Pre_publishing" mode disabled!')
                    _html_lst.append('"Pre_publishing" mode is disabled')
                except Exception as ex:
                    _msg_ex = mod.name + '.views.__drop_publish.Exception: ' + str(ex)
                    process_protocol.write(_msg_ex)
                    if _portal_modes_util is not None:
                        _msg_ex = mod.name + '.views.__drop_publish.Exception: Disabling "pre_publishing" mode failed!'
                        process_protocol.write(_msg_ex)
                        _msg_ex = mod.name + '.views.__drop_publish.Exception: Try to disable "pre_publishing" mode with ModeUtils!'
                        process_protocol.write(_msg_ex)
                        _portal_modes_util.drop(_pre_publish_mode)
                    raise Exception(_msg_ex)
                pass
            # режим подготовки к публикации }
            if _portal_modes_util is not None:
                _portal_mode = _portal_modes_util.get_current(_mode_name)
            # режим публикации (работа с хранилищем) {
            if _portal_mode is not None:
                _html_lst.append('Try to disable "publishing" mode')
                process_protocol.write(mod.name + '.views.__drop_publish: Enabled "publishing" mode!')
                try:
                    _portal_mode.disable()
                    process_protocol.write(mod.name + '.views.__drop_publish: "Publishing" mode disabled!')
                    _html_lst.append('"Publishing" mode is disabled')
                except Exception as ex:
                    _msg_ex = mod.name + '.views.__drop_publish.Exception: ' + str(ex)
                    process_protocol.write(_msg_ex)
                    print(_msg_ex)
                    if _portal_modes_util is not None:
                        _msg_ex = mod.name + '.views.__drop_publish.Exception: Disabling "publishing" mode failed!'
                        process_protocol.write(_msg_ex)
                        _msg_ex = mod.name + '.views.__drop_publish.Exception: Try to disable "publishing" mode with ModeUtils!'
                        process_protocol.write(_msg_ex)
                        _portal_modes_util.drop(_portal_mode)
                    raise Exception(_msg_ex)
                pass
            # режим публикации (работа с хранилищем) }

            publish_result.write('Процесс публикации принудительно завершен администратором!')
            _html_lst.append('Add message to the current publish result file!')
            #  теперь надо сказать публикатору что процесс публикации завершен !!!!
            process_logger = DataPublishLogger()
            if process_logger:
                process_logger.set('process.Done', True)
                if process_protocol:
                    process_protocol.write('Write process.Done to tracker file: TRUE')
            _mod_utils.drop_publishing_pid_file()
            _html_lst.append('Delete pid file!')
        except Exception as ex:
            publish_result.write('Не удалось принудительно завершить процесс публикации администратором!')
            publish_result.write('Ошибка: ' + str(ex))
            _html_lst.append('Drop current publishing is failed!')
            if process_protocol:
                process_protocol.write('Drop current publishing is failed! Exception: ' + str(ex))
            pass
    _html = '<br />' . join(_html_lst)
    return _html


@mod.route('/tools/drop_section/<name>')
def __drop_section(name):
    """
    Функция реинициализирует раздел с указанным именем:
    просто удаляет все файлы и создает занового реестр
    :return:
    """
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path(_mod_utils.get_mod_name())
    _fm = FilesManagement(_w_pth)
    _sec = _fm.get_section_inf(name)
    if _sec is not None:
        _lst = _fm.get_section_files(name)
        if _lst:
            # удаляем все файлы без изменения реестра
            for _li in _lst:
                if os.path.exists(_li):
                    os.unlink(_li)
        # в любом случае удаляем реестр
        if _sec['use_register']:
            _sr = _fm.get_section_register(name)
            _sr.drop()
            _sr.init()
    return 'Success section ' + name + 'reinicialization!'


@mod.route('/tools/view_protocol', methods=['GET'])
def __view_protocol():
    """
    Функция возвращает html страницу просмотра последнего протокола публикации
    :return:
    """
    _mod_utils = ModUtils()
    _tpl_vars = {}
    _tpl_vars['title'] = ''
    _tpl_vars['page_title'] = ''
    _tpl_vars['inavi'] = []
    _cur_user = None
    if g.user:
        _cur_user = g.user
    _tpl_vars['inavi'] = _mod_utils.get_navi(_cur_user)
    _tpl_name = ''
    _tpl_name = os.path.join(_mod_utils.get_mod_name(), 'protocol.html')
    return app_api.render_page(_tpl_name, _tpl_vars)


@mod.route('/tools/view_protocol/tail', methods=['POST'], defaults={'num': 30})
@mod.route('/tools/view_protocol/tail/<num>', methods=['POST'])
def __view_protocol_tail(num):
    _log = ''
    _log_file = ''
    filename = 'publish.protocol'
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path(_mod_utils.get_mod_name())
    _log_file = os.path.join(_w_pth, filename)
    if 30 > int(num):
        num = 30
    if os.path.exists(_log_file):
        _cmd = 'tail -n %s %s' %(num, _log_file)
        _log = os.system(_cmd)
    return _log


@mod.route('/tools/export/protocol')
def __export_protocol():
    """
    Функция возвращает файл протокола последней публикации
    :return:
    """
    filename = 'publish.protocol'
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path(_mod_utils.get_mod_name())
    protocol_file = os.path.join(_w_pth, filename)
    if os.path.exists(protocol_file):
        download_file_name = filename
        mime = 'application/octet-stream'
        file_ext = 'txt'
        _mime = CodeHelper.get_mime4file_ext(file_ext)
        if '' != _mime:
            mime = _mime
        # print('Catch download file: ' + download_file)
        from flask import send_file
        return send_file(protocol_file, mimetype=mime,
                             as_attachment=True, attachment_filename=download_file_name)
    return app_api.render_page(os.path.join('errors', '404.html'),
                               message='Отсутствует файл-протокол публикации данных')


@mod.route('tools/publish_error/export')
def __export_publish_error():
    """
    Функция возвращает файл с ошибками прервавшими подпроцесс публикации
    :return:
    """
    filename = 'publish-subproc.errors'
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path(_mod_utils.get_mod_name())
    protocol_file = os.path.join(_w_pth, filename)
    if os.path.exists(protocol_file):
        download_file_name = filename
        mime = 'application/octet-stream'
        file_ext = 'txt'
        _mime = CodeHelper.get_mime4file_ext(file_ext)
        if '' != _mime:
            mime = _mime
        # print('Catch download file: ' + download_file)
        from flask import send_file
        return send_file(protocol_file, mimetype=mime,
                             as_attachment=True, attachment_filename=download_file_name)
    return app_api.render_page(os.path.join('errors', '404.html'),
                               message='Отсутствует файл с ошибками публикации!')


def __get_filtered_records(sec_name):
    _records = []
    sidx = 'Name'  # get index row - i.e. user click to sort
    sord = 'asc'  # get the direction
    filters = ''

    _result_format = 'json'

    _section_v = SectionView(sec_name)

    if 'GET' == request.method:
        sidx = request.args['sidx'] if 'sidx' in request.args else sidx
        sord = request.args['sord'] if 'sord' in request.args else sord
        filters = request.args['filters'] if 'filters' in request.args else filters
        _result_format = request.args['fmt'] if 'fmt' in request.args else _result_format

    if 'POST' == request.method:
        sidx = request.form['sidx'] if 'sidx' in request.form else sidx
        sord = request.form['sord'] if 'sord' in request.form else sord
        filters = request.form['filters'] if 'filters' in request.form else filters
    # =====
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path(_mod_utils.get_mod_name())
    _fm = FilesManagement(_w_pth)
    _sec = _fm.get_section_inf(sec_name)
    _records = []
    if _sec is not None:
        if _sec['use_register']:
            _sr = _fm.get_section_register(sec_name)

            USE_NAMED_GRAPHS = CodeHelper.conf_bool(_cfg['Main']['use_named_graphs'])

            columns_map = _section_v.get_columns_map()
            jq_grid = JQGridHelper()
            jq_grid.set_map(columns_map)

            _records = _fm.get_section_content(sec_name, filters, sort=columns_map[sidx], sord=sord)
    return _records


@mod.route('/tools/export/section/<name>')
def __export_section(name):
    """
    Функция создает файл с содержимым реестра в формате xml
    :return:
    """

    _result_format = 'json'
    if request.args:
        _result_format = request.args['fmt'] if 'fmt' in request.args else _result_format

    _mod_utils = ModUtils()
    _section_v = SectionView(name)
    _records = []
    _records = __get_filtered_records(name)

    _result = None
    if 'json' == _result_format:
        _result = json.dumps(_records)
    if 'xml' == _result_format:
        _xml = ''
        _xml = __records2xml(_records)
        _result = _xml
    #  теперь сохраним контент в виде файла
    _download_file = os.path.join(_mod_utils.get_mod_data_path(), name + '_exported_records.' + _result_format)
    with open(_download_file, 'w', encoding='utf-8') as _fp:
        _fp.write(_result)
    from flask import send_file
    return send_file(_download_file, mimetype=_result_format,
                     as_attachment=True, attachment_filename=os.path.basename(_download_file))


def __records2xml(records=None):
    _xml = ''
    _xml_recs = ''
    if records:
        _t = []
        for _r in records:
            _s = ''
            _s = _dictline2xml(_r)
            _t.append(_s)
        if _t:
            _tn = 'Row'
            _tag = _2xmltag(_tn)
            _xml_recs = str('</' + _tag + '><' + _tag + '>').join(_t)
            _xml_recs = '<' + _tag + '>' + _xml_recs + '</' + _tag + '>'
    _xml = _2xmldoc(_xml_recs)
    return _xml


def _2xmldoc(_content=''):
    _xml = ''
    _xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    _xml += '<Root>'
    _xml += _content
    _xml += '</Root>'
    return _xml


def _dictline2xml(_dictline={}):
    _xml = ''
    if _dictline:
        _t = []
        for k,v in _dictline.items():
            k = _2xmltag(k)
            _s = '<' + k + '>'
            _s += _2xmlval(v)
            _s += '</' + k + '>'
            _t.append(_s)
        if _t:
            _xml = ''.join(_t)
    return _xml


def _2xmlval(_val):
    new_val = ''
    new_val = str(_val)
    return new_val


def _2xmltag(_tn):
    _tag = str(_tn)
    return _tag


@mod.route('/tools/restore/<point>')
def __restore_full_backup(point):
    _html = ''
    return _html


@mod.route('/tools/filtered/remove/<name>', methods=['POST'])
def __filtered_remove(name):
    """
    Функция удаления данных из реестр, выбранных с помощью фильтра
    :return:
    """
    _answer = {'Msg': '', 'Data': None, 'State': 500}
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path(_mod_utils.get_mod_name())
    _fm = FilesManagement(_w_pth)
    _sec = _fm.get_section_inf(name)
    """
    При удалении записи в данных, требуется пометить на удаление результат (если есть)
    При удалении записи в резервных копиях - просто удаляем
    При удалении записи в картах - нужно проверить использована ли данная карта для данных, удаляем если неиспользовалась
    При удалении записи в медиа - надо использовать отличный метод
    """

    if 'media' == name:
        # получить апи управления файлами
        _files_api = app_api.get_mod_api('files_mgt')
        _files_utils = _files_api.get_util()()

        # будем получать отдельно медиа путь
        sidx = ''
        sord = ''
        filters = ''
        if 'GET' == request.method:
            sidx = request.args['sidx'] if 'sidx' in request.args else sidx
            sord = request.args['sord'] if 'sord' in request.args else sord
            filters = request.args['filters'] if 'filters' in request.args else filters

        if 'POST' == request.method:
            sidx = request.form['sidx'] if 'sidx' in request.form else sidx
            sord = request.form['sord'] if 'sord' in request.form else sord
            filters = request.form['filters'] if 'filters' in request.form else filters

        _media_src = _files_utils.get_dir_path(__get_media_root())
        # print(mod.name + '.views.__filtered_download_files: _media_src -> ' + _media_src)
        real_base_start = __get_media_root()
        media_path = ''
        media_path = request.args['base'] if 'base' in request.args else name
        media_path = request.form['base'] if 'base' in request.form else media_path
        if media_path.startswith('media'):
            media_path = media_path.replace('media', real_base_start).lstrip('/')
        items = []
        _content_lst = []
        if filters:
            """ сперва будем искать """
            _content_lst = _files_utils.search_items(media_path, filters)
        else:
            """ просто выбираем все """
            _content_lst = _files_utils.get_dir_source(media_path)
        if _content_lst:
            items = [_item.name.decode('utf-8', 'unicode_escape') for _item in _content_lst]
        result = _files_utils.remove_selected_items(items, media_path)
        if result and 0 < len(result['deleted']):
            _answer['State'] = 200
            _answer['Msg'] = '' if len(result['deleted']) == len(result['all']) else 'Не все данные были удалены!'
            _answer['Data'] = result # {'deleted': deleted, 'all': items}
    else:
        """
           При удалении записи в данных, требуется пометить на удаление результат (если есть)
           При удалении записи в резервных копиях - просто удаляем
           При удалении записи в картах - нужно проверить использована ли данная карта для данных,
            удаляем если неиспользовалась
           """
        _records = []
        # контекстно зависимая функция, использует flask.request для получения входных параметров
        _records = __get_filtered_records(name)
        if 'maps' == name:
            pass
            # убираем из отфильрованных карты которые указаны
            datas = _fm.get_section_content('data')
            usd_maps = set([di['map'] for di in datas if '' != di['result']])
            _records = [_m for _m in _records if _m['name'] not in usd_maps]
        _remove_results = {}
        if 'data' == name:
            # если включен режим подготовки публикации, то удалять данные нельзя
            _admin_mgt_api = app_api.get_mod_api('admin_mgt')
            _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
            _portal_mode = None
            if _portal_modes_util is not None:
                _portal_mode = _portal_modes_util.get_current('publish_prepare')
                if _portal_mode is not None:
                    pass
                    # возвращаем результат
                    _answer['State'] = 201
                    _answer['Msg'] = 'Запущен процесс подготовки к публикации. Удаление данных запрещено!'
                    return json.dumps(_answer)
            pass
            # создаем список результатов для пометки на удаление
            _d2 = {'deleted': True}
            for _r in _records:
                if _r['result']:
                    _remove_results[_r['result']] = _d2

        _sec_pth = _fm.get_section_path(name)
        _del_lst = [_r['name'] for _r in _records]
        # print('Delete list: ', _del_lst)
        _del_flg = _fm.remove_section_files(name, _del_lst)
        if _remove_results:
            _upd_flg2 = _fm.update_section_files('res', _remove_results)
            pass
            #  помечаем указанные результаты на удаление
        _answer['Msg']  = 'Can not delete filtered records, count: ' + str(len(_del_lst))
        if _del_flg:
            _answer['Msg']  = 'Delete records(count: ' + str(len(_del_lst)) + ') Complete!'
        if _del_flg:
            _html = 'Success'
            _answer['State'] = 200
            # _answer['Msg'] = 'Операция выполнена успешно!'
            _answer['Data'] = {}
    return json.dumps(_answer)


@mod.route('/tools/export/files/<name>', methods=['GET', 'POST'])
def __filtered_download_files(name):
    """
    Функция скачивает файлы из отфильтрованных записей
    :param name: имя секции записей для скачивания файлов
    :return:
    """

    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path(_mod_utils.get_mod_name())
    _fm = FilesManagement(_w_pth)
    _download_files = []
    # print(mod.name + '.views.__filtered_download_files: section name -> ' + name)
    zip_file_name = name + '_download_files_' + _mod_utils.formated_time_mark()
    zip_file_name += '.zip'
    # получить апи управления файлами
    _files_api = app_api.get_mod_api('files_mgt')
    _files_utils = _files_api.get_util()()
    _temp_pth = _files_utils.get_dir_path('temp')
    zip_file = os.path.join(_temp_pth, zip_file_name)
    if not os.path.exists(_temp_pth):
        os.mkdir(_temp_pth)
    if 'media' != name:
        _records = []
        _records = __get_filtered_records(name)
        if _records:
            _sec_pth = _fm.get_section_path(name)
            for _rec in _records:
                pass
                _file_path_to_arch = ''
                _file_path_to_arch = os.path.join(_sec_pth, _rec['name'])
                # print(mod.name + '.views.__filtered_download_files: ' + _file_path_to_arch)
                if os.path.exists(_file_path_to_arch):
                    _download_files.append(_file_path_to_arch)
        if _download_files:
            import zipfile
            if not os.path.exists(zip_file):
                with open(zip_file, 'a') as fm:
                    os.utime(zip_file, None)
            with zipfile.ZipFile(zip_file, 'w') as myzip:
                for ifile in _download_files:
                    add_file_name = os.path.basename(ifile)
                    myzip.write(ifile, arcname=add_file_name)
    else:
        """
        требуется определить текущую директорию
        затем скопировать ее во временную
        создать архив
        """
        sidx = ''
        sord = ''
        filters = ''
        if 'GET' == request.method:
            sidx = request.args['sidx'] if 'sidx' in request.args else sidx
            sord = request.args['sord'] if 'sord' in request.args else sord
            filters = request.args['filters'] if 'filters' in request.args else filters

        if 'POST' == request.method:
            sidx = request.form['sidx'] if 'sidx' in request.form else sidx
            sord = request.form['sord'] if 'sord' in request.form else sord
            filters = request.form['filters'] if 'filters' in request.form else filters

        _media_src = _files_utils.get_dir_path(__get_media_root())
        # print(mod.name + '.views.__filtered_download_files: _media_src -> ' + _media_src)
        real_base_start = __get_media_root()
        media_path = ''
        media_path = request.args['base'] if 'base' in request.args else name
        media_path = request.form['base'] if 'base' in request.form else media_path
        if media_path.startswith('media'):
            media_path = media_path.replace('media', real_base_start).lstrip('/')
        # print(mod.name + '.views.__filtered_download_files: media_path -> ' + media_path)

        if filters:
            """ сперва будем искать """
            file_list = _files_utils.search_items(media_path, filters)
        else:
            """ просто выбираем все """
            file_list = _files_utils.get_dir_source(media_path)
        # print(mod.name + '.views.__filtered_download_files: file_list -> ' + str(file_list))

        if file_list:
            if not os.path.exists(zip_file):
                with open(zip_file, 'a') as fm:
                    os.utime(zip_file, None)
            _zip_target = _files_utils.get_dir_path(media_path)
            _zip_src = os.path.join(_temp_pth, os.path.basename(_zip_target))
            if not os.path.exists(_zip_src):
                os.mkdir(_zip_src)
            # требуется делать через копирование иначе не работает фильтр внутри!!!!!
            # print(mod.name + '.views.__filtered_download_files: _zip_src -> ' + str(_zip_src))
            from shutil import make_archive, rmtree, copytree
            # когда все подготовили копируем отфильтрованные источники для архива
            for _ix in file_list:
                # print(mod.name + '.views.__filtered_download_files: str(_ix.name) -> ' + str(_ix.name))
                _t1 = os.path.join(_zip_target, str(_ix.name.decode('utf-8', 'unicode_escape')))
                # print(mod.name + '.views.__filtered_download_files: _t1 -> ' + _t1)
                _to1 = os.path.join(_zip_src, str(_ix.name.decode('utf-8', 'unicode_escape')))
                # print(mod.name + '.views.__filtered_download_files: _to1 -> ' + _to1)
                if os.path.isdir(_t1):
                    _cp_flg = copytree(_t1, _to1, dirs_exist_ok=True)
                    # print(mod.name + '.views.__filtered_download_files: _cp_flg (dir) -> ' + str(_cp_flg))
                if os.path.isfile(_t1):
                    _cp_flg = copyfile(_t1, _to1)
                    # print(mod.name + '.views.__filtered_download_files: _cp_flg (file) -> ' + str(_cp_flg))
            # интересное дело для данной функции в имени файла не надо указывать расширение
            # она сама назначает его
            _zip_flg = make_archive(zip_file.replace('.zip', ''), 'zip', _zip_src)
            # print(mod.name + '.views.__filtered_download_files: _zip_flg -> ' + str(_zip_flg))
            # print(mod.name + '.views.__filtered_download_files: os.path.basename(zip_file) -> ' + str(zip_file))
            if _zip_flg == zip_file:
                rmtree(_zip_src, ignore_errors=True)
                pass

    if os.path.exists(zip_file):
        from flask import send_file, after_this_request
        @after_this_request
        def __remove_sended_file(response):
            try:
                os.remove(zip_file)
            except Exception as ex:
                print('Не удалось сформировать архив со списком файла!', str(ex))
            return response
        return send_file(zip_file, mimetype='application/zip',
                         as_attachment=True, attachment_filename=zip_file_name)

    return app_api.render_page("/errors/404.html", message='Не удалось сформировать архив со списком файла!')


@mod.route('/tools/section/sync/<name>')
def __sync_section_register(name):
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path(_mod_utils.get_mod_name())
    _fm = FilesManagement(_w_pth)
    _sec = _fm.get_section_inf(name)
    _html = 'Error'
    _nL = "\n\r"
    _nL = '<br />'
    _fm.sync_section_content(name)
    _html = ''
    _html += 'Sync is with!' + _nL
    return _html


@mod.route('/tools', methods=['GET'], strict_slashes=False)
def __view_tools():
    """
    Функция возвращает html страницу просмотра последнего протокола публикации
    :return:
    """
    _mod_utils = ModUtils()
    _tpl_vars = {}
    _tpl_vars['title'] = 'Страница технической помощи управления данными'
    _tpl_vars['page_title'] = 'Страница технической помощи управления данными'
    _tpl_vars['inavi'] = []
    _tpl_vars['inavi'] = _mod_utils.get_tools_navi(g.user)
    _tpl_name = ''
    _tpl_name = os.path.join(_mod_utils.get_mod_name(), 'tools.html')
    return app_api.render_page(_tpl_name, **_tpl_vars)

# tools }


@mod.route('/sync/dataresults', methods=['GET'])
@_auth_decorator
def __sync_data_results():
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)
    USE_NAMED_GRAPHS = CodeHelper.conf_bool(_cfg['Main']['use_named_graphs'])
    _html = 'Error'
    _nL = "\n\r"
    _nL = '<br />'
    _fm.sync_section_content('res')
    _html = ''
    _html += 'Sync is with!' + _nL
    return _html


@mod.route('/tests/update', methods=['GET'])
@_auth_decorator
def __test_update_record():
    _mod_utils = ModUtils()
    _cfg = _mod_utils.get_config()
    _w_pth = app_api.get_mod_data_path('portaldata_mgt')
    _fm = FilesManagement(_w_pth)
    USE_NAMED_GRAPHS = CodeHelper.conf_bool(_cfg['Main']['use_named_graphs'])
    _html = 'Error'
    _nL = "\n\r"
    _nL = '<br />'
    # получим записи
    _recs = _fm.get_section_content('res')
    if _recs:
        _html = ''
        _html += 'Catch records: ' + str(len(_recs)) + _nL
        from random import randint
        _i = randint(0, len(_recs)-1)
        _html += 'views.__test_update_record -> selected item: ' + str(_i) + ' || ' + str(_recs[_i]) + _nL
        _mdate = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        _html += 'views.__test_update_record -> update mdate: ' + _mdate +  _nL
        _flg = False
        _flg = _fm.update_section_file('res', _recs[_i]['name'], {'mdate': _mdate})
        _html += 'views.__test_update_record -> update result: ' + str(_flg) +  _nL
    _html += 'Update done!' + _nL
    return _html


@mod.route('/secret/<base>', methods=['GET'])
@_auth_decorator
def app_config_state(base):
    from werkzeug.security import generate_password_hash
    _html = generate_password_hash(base)
    return _html

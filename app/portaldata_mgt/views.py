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
    # pid_file = PortalSettings.get_publishing_pid_file()
    # with open(pid_file, 'w') as file_p:
    #     file_p.write(str(data))

    answer['State'] = 200
    answer['Msg'] = 'Процесс запущен!'
    answer['Data'] = {'process': str(data)}

    return json.dumps(answer)


def __get_publish_error_file():
    check_errors = ''
    data_path = app_api.get_mod_data_path('portaldata_mgt')
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

            check_errors = ''
            check_errors = __get_publish_error_file()
            # надо проверить - если файл не пустой
            file_size = os.stat(check_errors).st_size
            if file_size > 1:
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
            rmtree(_upload_temp) # удаляем поскольку пуста
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
            rmtree(_upload_temp) # удаляем поскольку пуста
    return json.dumps(answer)


@mod.route('/loadFiles/<section>', methods=['POST'], strict_slashes=False)
@_auth_decorator
def __upload_files(section):
    """ загружаем файлы в определенную директорию """
    answer = {'Msg': '', 'Data': None, 'State': 404}
    answer['Msg'] = 'Нет файлов для сохранения.'
    if request.files and 'File[]' in request.files:
        # print('Catch files')
        file = None # type: werkzeug.datastructures.FileStorage

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

# -*- coding: utf-8 -*-

import sys

import os
from shutil import copyfile
from datetime import datetime

from app import app_api
from app.utilites.code_helper import CodeHelper
from app.portaldata_mgt.process_logger import ProcessLogger

from app.portaldata_mgt.mod_utils import ModUtils
_mod_utils = ModUtils()
process_protocol = None
publish_result = None
_mod_cfg = None
try:
    _mod_cfg = _mod_utils.get_config()
    process_protocol = ProcessLogger()
    publish_result = ProcessLogger()

    mod_data_path = app_api.get_mod_data_path('portaldata_mgt')
    protocol_file = os.path.join(mod_data_path, 'publish.protocol')
    result_file = _mod_utils.get_publish_result_file()
    process_protocol.set_log_file(protocol_file)
    publish_result.set_log_file(result_file)
    process_protocol.clear_log_file() # сбрасываем файл если он есть
    publish_result.clear_log_file() # сбрасываем файл если он есть
except Exception as ex:
    raise ex

process_protocol.write('Starting publishing process')

from app.portaldata_mgt.data_publisher import DataPublisher
from app.portaldata_mgt.data_backuper import DataBackuper
from app.portaldata_mgt.files_management import FilesManagement
from app.portaldata_mgt.data_publish_logger import DataPublishLogger

_fm = FilesManagement(mod_data_path)

USE_NAMED_GRAPHS = False
app_cfg = app_api.get_app_config()
try:
    USE_NAMED_GRAPHS = CodeHelper.conf_bool(app_cfg.get('data_storages.Main.use_named_graphs'))
except Exception as ex:
    print('data_publish_process.py: Error -> {}'.format(ex))
    process_protocol.write('Error on set constants USE_NAMED_GRAPHS: {}'.format(ex))

process_logger = DataPublishLogger()
process_protocol.write('Create publish process tracker')


class Counters:
    _d = {}

    @staticmethod
    def _enc(name):
        if name not in Counters._d:
            Counters._d[name] = 0
        Counters._d[name] += 1

    @staticmethod
    def get(name):
        Counters._enc(name)
        if name in Counters._d:
            return Counters._d[name]
        return 0


def trigger_upload_success(file_path):
    """"""
    process_protocol.write('Success file upload: {}'.format(file_path))
    count_to_upload = Counters.get('upload')
    process_logger.set('upload_files.done', count_to_upload)
    process_protocol.write('Write upload_files.done to tracker file: {}'.format(count_to_upload))


def trigger_upload_fail(error, file_path):
    """"""
    process_protocol.write('Fail file upload {} with error {}'.format(error))
    msg = 'Error: ' + error + '! on file: ' + file_path
    process_logger.set('errors', msg)
    process_protocol.write('Write errors to tracker file: {}'.format(msg))


def log_function_proxy(msg):
    process_protocol.write(msg)

# получаем паблишер
data_publisher = DataPublisher()
# настраиваем его
# устанавливаем файлы онтологий
data_publisher.use_named_graph = USE_NAMED_GRAPHS
process_protocol.write('Set flag USE_NAMED_GRAPHS - {}'.format(USE_NAMED_GRAPHS))

process_logger.set('process.Done', False)
process_protocol.write('Write FLAG "process.Done" to tracker file (initial)')

for_publish = [] # список для сохранения файлов результатов по файлам данных и онтологиям

# просмотрим есть ли у нас ре
old_results = {}
if _fm.get_section_path('res') is not None:
    _t1 = _fm.get_section_content('res')
    if _t1:
        for it in _t1:
            old_results[it['name']] = it

# подготовка файлов онтологий для публикации {
onto_list = []
process_protocol.write('Try add ontology files for publishing')
# получим онтологии
ontos_api = app_api.get_mod_api('onto_mgt')
# элемент списка файлов онтологий - список: 0 - полный путь к файлу, 1 - базовый URL онтологии (префикс)
# onto_list.append([os.path.join(PublishModConf.DATA_PATH, 'qudt_units.ttl'), ''])
# onto_list.append([os.path.join(PublishModConf.DATA_PATH, 'requirements_ontology.ttl'), ''])
# onto_utils = ontos_api.get_onto_utils() # метод удален без предупреждения
onto_list = ontos_api.get_ontos()
cnt_ontos = len(onto_list)
if onto_list:
    for onto_info in onto_list:
        for_publish.append(onto_info[0])
# подготовка файлов онтологий для публикации }

if 0 == len(onto_list):
    process_protocol.write('No ontology files!')
    publish_result.write('Отсутствуют файлы онтологий для загрузки!')
#     # Аварийно завершаем работу
#     if process_logger:
#         msg = 'Аварийное завершение процесса публикации данных: Отсутствуют файлы онтологий!'
#         process_logger.set('process.Done', True)
#         process_logger.set('errors', msg)
#         process_logger.set('process.crash_message', msg)
#         if process_protocol:
#             process_protocol.write('Write process.Done to tracker file: TRUE')
#     exit(0) # выходим для завершения

# =============================================== {

# подготовка файлов данных для публикации {
if _fm.get_section_path('res') is not None:
    process_protocol.write('Directory with data files (ttl) is exists!')
    drop_store = False

    files = _fm.get_section_content('res')
    # print('Data files', files)

    cnt_datas = len(files)
    # надо добавить файлы загружаемых онтологий
    cnt_datas += cnt_ontos
    process_logger.set('work_files.total', cnt_datas)
    process_protocol.write('Write work_files.total to tracker file: {}'.format(cnt_datas))
    # надо посчитать сколько файлов нужно для конвертирования
    cnt_flags = 0
    created = []
    process_protocol.write('Start loop over data files (description in register.json)')
    res_path = _fm.get_section_path('res')
    total_operate = 0
    for idata_file in files:
        process_protocol.write('Process on file - {}'.format(idata_file['name']))
        data_file = os.path.join(res_path, idata_file['name'])
        end_file_size = os.stat(data_file).st_size
        if 2 > end_file_size:
            process_protocol.write('Empty file - {}'.format(str(end_file_size)))
            publish_result.write('Файл 0-ой длины -> ' + idata_file['name'])
        for_publish.append(data_file)
        total_operate +=1
        process_logger.set('work_files.done', total_operate)
    process_protocol.write('Write work_files.done to tracker file: {}'.format(total_operate))

""" собственно начинаем публикацию """

process_logger.set('upload_files.total', len(for_publish))
process_protocol.write('Catch {} files for upload to triplestore' . format(len(for_publish)))

__has_publish_errors = False

# for_publish используме как маркер что мы обошли файлы данных
if for_publish:
    for it in for_publish:
        process_protocol.write(str(it))
        pf_name = os.path.basename(it)
        data_publisher.update_publish_list(it, False)
        process_protocol.write('Add {} to publish list'.format(pf_name))
    process_protocol.write('Add all files to publish list')

""" собственно начинаем публикацию """
data_publisher.set_success_trigger(trigger_upload_success)
process_protocol.write('Set trigger for success uploading!')
data_publisher.set_fail_trigger(trigger_upload_fail)
process_protocol.write('Set trigger for fail uploading!')
data_publisher.set_log_func(log_function_proxy)
process_protocol.write('Set function for logging (Publish tool)')
# сперва сделаем резервную копию текущего хранилища
# data_backuper = DataBackuper()
# data_backuper.use_named_graph = USE_NAMED_GRAPHS
# data_backuper.set_log_func(log_function_proxy)
# process_protocol.write('Set function for logging (Backup tool)')
# process_protocol.write('Try create backup file')
# backup_file = os.path.join(_fm.get_section_path('backups'), data_backuper.generate_filename())
# process_protocol.write('Backup data try save to: {}'.format(backup_file))
# flg_backup = data_backuper.create(backup_file)
# process_protocol.write('Create backup: {}'.format(flg_backup))
# if flg_backup:
#     # создали файл резервной копии - надо синхронизировать директорию
#     _fm.sync_section_content('backups')
#     # теперь укажем что даннаая резервная копия была сделана руками
#     call_args = {'comment': 'Cоздана автоматически перед публикацией данных'}
#     name = os.path.basename(backup_file)
#     name = os.path.basename(data_backuper.get_last_downloaded_file())
#     _fm.update_section_file('backups', name, call_args)
#     process_protocol.write('Sync backup files directory description')
# else:
#     """ надо ли прекращать если не смогли """
#     process_protocol.write('Creating backup FAIL!')

# запускаем непосредственно процесс публикации

# требуется установить режим портала ограничивающий
_admin_mgt_api = app_api.get_mod_api('admin_mgt')
_portal_modes_util = _admin_mgt_api.get_portal_mode_util()
_portal_mode = None
if _portal_modes_util is not None:
    _mode_name = ModUtils().get_portal_mode_name()
    _portal_mode = _portal_modes_util.set_portal_mode(_mode_name)
    _mod = os.path.basename(ModUtils().get_mod_path())
    _portal_mode.set_target(_mod + '.__publish_proc_info')
    _lst = []
    """
    portal.publish_proc_info, 'data_management.publish_process_step',
    'data_management.publish_process_done', 'data_management.publish_process_break'
    """
    _lst.append(_mod + '.static')
    _lst.append(_mod + '.publish_process_step')
    _lst.append(_mod + '.publish_process_done')
    _lst.append(_mod + '.publish_process_break')
    _lst.append(_mod + '.__export_protocol')
    _lst.append(_mod + '.__view_protocol')
    _lst.append(_mod + '.__drop_publish')
    _lst.append(_mod + '.__view_protocol_tail')
    _portal_mode.set_opened(_lst)
    _portal_mode.enable_redirect()
    _portal_mode.enable()
    process_protocol.write('Enable portal publish mode')

process_protocol.write('Start upload/update process')
pub_answer = data_publisher.publish()
__has_publish_errors = data_publisher.has_errors()
if __has_publish_errors:
    if data_publisher.has_upload_fails():
        process_protocol.write('Some file uploads is fail!')
    if data_publisher.has_trigger_fails():
        process_protocol.write('Some trigger execution failed!')
else:
    process_protocol.write('Upload/update process DONE!')

# теперь выключим режим блокировки
if _portal_mode is not None:
    try:
        _portal_mode.disable()
        process_protocol.write('Disable portal publish mode')
    except Exception as ex:
        if _portal_modes_util is not None:
            _portal_modes_util.drop(_portal_mode)
    pass

if process_logger:
    process_logger.set('process.Done', True)
    if process_protocol:
        process_protocol.write('Write process.Done to tracker file: TRUE')
if publish_result:
    if __has_publish_errors:
        publish_result.write('В процессе публикации произошли ошибки! Требуется ознакомиться с протоколом публикации.')
    else:
        publish_result.write('Процесс публикации успешно завершен!')
# завершение функции публикации

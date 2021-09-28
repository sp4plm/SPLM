# -*- coding: utf-8 -*-

import sys

import os
from shutil import copyfile
from datetime import datetime

from app import app_api
from app.utilites.code_helper import CodeHelper
from app.publish_mgt.module_conf import PublishModConf
from app.publish_mgt.process_logger import ProcessLogger

process_protocol = None
try:
    process_protocol = ProcessLogger()

    mod_data_path = PublishModConf.DATA_PATH
    protocol_file = os.path.join(mod_data_path, 'publish.protocol')
    process_protocol.set_log_file(protocol_file)
    process_protocol.clear_log_file() # сбрасываем файл если он есть
except Exception as ex:
    raise ex

process_protocol.write('Starting publishing process')

from app.publish_mgt.data_publisher import DataPublisher
from app.publish_mgt.data_backuper import DataBackuper
from app.publish_mgt.files_managment import FilesManagment
from app.publish_mgt.data_publish_logger import DataPublishLogger

USE_NAMED_GRAPHS = False
app_cfg = app_api.get_app_config()
try:
    USE_NAMED_GRAPHS = bool(int(app_cfg.get('main.DataStorage.use_named_graphs')))
except Exception as ex:
    print('data_publish_process.py: Error -> {}'.format(ex))
    process_protocol.write('Error on set constants USE_NAMED_GRAPHS: {}'.format(ex))

process_logger = DataPublishLogger()
process_protocol.write('Create publish process tracker')


class Counters:
    _d = {}

    @staticmethod
    def enc(name):
        if name not in Counters._d:
            Counters._d[name] = 0
        Counters._d[name] += 1

    @staticmethod
    def get(name):
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
res_meta = FilesManagment()
old_results = {}
if res_meta.set_current_dir('res'):
    _t1 = res_meta.get_dir_source('res')
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
onto_utils = ontos_api.get_onto_utils()
onto_list = onto_utils.get_ontos()
cnt_ontos = len(onto_list)
if onto_list:
    for onto_info in onto_list:
        for_publish.append(onto_info[0])
# подготовка файлов онтологий для публикации }

if 0 == len(onto_list):
    process_protocol.write('No ontology files!')
    # Аварийно завершаем работу
    if process_logger:
        msg = 'Аварийное завершение процесса публикации данных: Отсутствуют файлы онтологий!'
        process_logger.set('process.Done', True)
        process_logger.set('errors', msg)
        process_logger.set('process.crash_message', msg)
        if process_protocol:
            process_protocol.write('Write process.Done to tracker file: TRUE')
    exit(0) # выходим для завершения


# подготовка файлов данных для публикации {
meta = FilesManagment()
if meta.set_current_dir('data'):
    process_protocol.write('Directory with data files (ttl) is exists!')
    files = meta.get_dir_source('data')
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
    res_path = meta.get_dir_realpath('res')
    total_operate = 0
    for idata_file in files:
        process_protocol.write('Process on file - {}'.format(idata_file['name']))
        data_file = os.path.join(meta.get_dir_realpath('data'), idata_file['name'])
        for_publish.append(data_file)
        total_operate +=1
        process_logger.set('work_files.done', total_operate)
    process_protocol.write('Write work_files.done to tracker file: {}'.format(total_operate))

""" собственно начинаем публикацию """

# for_publish используме как маркер что мы обошли файлы данных
if for_publish:
    process_protocol.write('Catch {} files for upload to triplestore' . format(len(for_publish)))

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
    data_backuper = DataBackuper()
    data_backuper.use_named_graph = USE_NAMED_GRAPHS
    data_backuper.set_log_func(log_function_proxy)
    process_protocol.write('Set function for logging (Backup tool)')
    process_protocol.write('Try create backup file')
    backup_file = os.path.join(meta.get_dir_realpath('backups'), data_backuper.generate_filename())
    process_protocol.write('Backup data try save to: {}'.format(backup_file))
    flg_backup = data_backuper.create(backup_file)
    process_protocol.write('Create backup: {}'.format(flg_backup))
    if flg_backup:
        # создали файл резервной копии - надо синхронизировать директорию
        meta.set_current_dir('backups')
        meta.sync_description()
        # теперь укажем что даннаая резервная копия была сделана руками
        call_args = {'comment': 'Cоздана автоматически перед публикацией данных'}
        name = os.path.basename(backup_file)
        name = os.path.basename(data_backuper.get_last_downloaded_file())
        meta.set_file_description(name, call_args)
        process_protocol.write('Sync backup files directory description')
    else:
        """ надо ли прекращать если не смогли """
        process_protocol.write('Creating backup FAIL!')

    # запускаем непосредственно процесс публикации
    process_protocol.write('Start upload/update process')
    pub_answer = data_publisher.publish()
    process_protocol.write('Upload/update process DONE!')

if process_logger:
    process_logger.set('process.Done', True)
    if process_protocol:
        process_protocol.write('Write process.Done to tracker file: TRUE')
# завершение функции публикации

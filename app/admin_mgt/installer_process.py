# -*- coding: utf-8 -*-
# import sys
import os
import subprocess
import shutil
from app.admin_mgt.admin_conf import AdminConf
from app.admin_mgt.configurator import Configurator


_portal_configurator = Configurator()
_installer_source = os.path.join(os.path.dirname(__file__), AdminConf.INIT_DIR_NAME)
_installer_target = AdminConf.DATA_PATH # имя нужно получить из файла в defaults - рекурсия описания
_app_dir = os.path.dirname(os.path.dirname(__file__)) # application directory
_portal_configurator.set_app_dir(_app_dir)


def __2_log(msg, init=False):
    msg = str(msg) + "\n"
    __log = os.path.join(os.path.dirname(__file__), AdminConf.DATA_DIR_NAME, 'installer.log')
    flg = 'a'
    if init:
        flg = 'w'
    with open(__log, flg, encoding='utf-8') as fp:
        fp.write(msg)


def __cpr(_src, _tgt):
    # https://stackoverflow.com/questions/15034151/copy-directory-contents-into-a-directory-with-python
    # _t = subprocess.call(['cp', '-r', _installer_source + os.path.sep + '.', _installer_target])
    res = shutil.copytree(_src, _tgt, dirs_exist_ok=True)
    return res

# проверяем что нет маркера установки
if _portal_configurator.check_inst_marker():
    exit(0) # выходим, так как процесс инсталляции пройден
__2_log('Installer.start', True)

# копируем файлы по умолчанию по указанному пути
if not os.path.exists(_installer_target):
    os.mkdir(_installer_target)

__2_log('Installer.add destination directory ' + _installer_target)

# нужна ветка для обработки загруженного архива

__2_log('Installer.try copy to target from ' + _installer_source)

if os.path.exists(_installer_source):
    msg = ''
    _t = __cpr(_installer_source, _installer_target)
    __2_log('Installer. copy result ' + str(_t))

# запускаем процесс конфигурации базы данных
""" запускаем инициализацию """
config_flag = False
config_flag = _portal_configurator.configure_db(_app_dir)
__2_log('Installer. Configure database result %s' % str(config_flag))

# write
if config_flag:
    _portal_configurator.create_inst_marker()

__2_log('Installer. Installation result %s' % str(_portal_configurator.check_inst_marker()))

exit(0)

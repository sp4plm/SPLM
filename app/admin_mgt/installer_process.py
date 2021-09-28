# -*- coding: utf-8 -*-
# import sys
import os
import subprocess
from app.admin_mgt.admin_conf import AdminConf
from app.admin_mgt.configurator import Configurator


_portal_configurator = Configurator()
_installer_source = os.path.join(os.path.dirname(__file__), AdminConf.INIT_DIR_NAME)
_installer_target = AdminConf.DATA_PATH # имя нужно получить из файла в defaults - рекурсия описания
_app_dir = os.path.dirname(os.path.dirname(__file__)) # application directory
_portal_configurator.set_app_dir(_app_dir)

# проверяем что нет маркера установки
if _portal_configurator.check_inst_marker():
    exit(0) # выходим, так как процесс инсталляции пройден

# копируем файлы по умолчанию по указанному пути
if not os.path.exists(_installer_target):
    os.mkdir(_installer_target)

# нужна ветка для обработки загруженного архива

if os.path.exists(_installer_source):
    msg = ''
    # https://stackoverflow.com/questions/15034151/copy-directory-contents-into-a-directory-with-python
    _t = subprocess.call(['cp', '-r', _installer_source + os.path.sep + '.', _installer_target])

# запускаем процесс конфигурации базы данных
""" запускаем инициализацию """
config_flag = False
config_flag = _portal_configurator.configure_db(_app_dir)

# write
if config_flag:
    _portal_configurator.create_inst_marker()

exit(0)

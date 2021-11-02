# -*- coding: utf-8 -*-
import sys
import os
import subprocess
from datetime import datetime


class Configurator:
    _class_file = __file__
    _debug_name = 'PortalConfigurator'
    _alembic_dir_name = 'migrations'
    _scripts_dir_name = 'versions'
    _install_marker = 'splm_installation'

    def __init__(self):
        self._app_dir = ''
        self._db_configure_steps = []

    def configure_db(self, app_root):
        """"""
        if not os.path.exists(app_root) or not os.path.isdir(app_root):
            return False
        # проверка что DB неинициализирована - flask db init
        app_root_dir = app_root
        if '' == self._app_dir:
            self.set_app_dir(app_root_dir)
        app_parent = os.path.dirname(app_root_dir)
        migrate_dir = os.path.join(app_parent, self._alembic_dir_name)
        versions_dir = os.path.join(migrate_dir, self._scripts_dir_name)
        errors = None
        output = None
        is_init = False

        if app_parent not in sys.path:
            sys.path.insert(0, app_parent)
        cwd = os.getcwd()
        if os.getcwd() != app_parent:
            os.chdir(app_parent)

        if os.path.exists(migrate_dir) and os.path.isdir(migrate_dir) \
                and os.path.exists(versions_dir) and os.path.isdir(versions_dir):
            """ будем считать что директория инициализирована"""
            is_init = True
        else:
            cmd = 'flask db init'
            """ запускаем инициализацию """
            cmd_args = cmd.split(' ')
            run_cmd = subprocess.Popen(cmd_args)
            output, errors = run_cmd.communicate()
            is_init = True
            # print('run "' + cmd + '" output:', output)
            # print('run "' + cmd + '" errors:', errors)
            if errors:
                is_init = False
                return errors
        if is_init:
            scripts = [it.name for it in os.scandir(versions_dir)]
            # создаем комментарий о дате реконфигурации
            cmt = 'DB autoreconfiguration ' + datetime.now().strftime("%Y%m%d_%H-%M-%S")
            # создаем скрипт реконфигурации
            cmd = 'flask db migrate -m'
            cmd_args = cmd.split(' ')
            cmd_args.append('"' + cmt + '"')
            run_cmd = subprocess.Popen(cmd_args)
            output, errors = run_cmd.communicate()
            scripts1 = [it.name for it in os.scandir(versions_dir)]
            if errors:
                return errors
            # выполняем реконфигурацию
            cmd = 'flask db upgrade'
            if 0 < len(scripts1) - len(scripts):
                cmd_args = cmd.split(' ')
                run_cmd = subprocess.Popen(cmd_args)
                output, errors = run_cmd.communicate()
                if errors:
                    return errors
                self._db_configure_steps.insert(0, 'DB upgrade done!')
            self._db_configure_steps.insert(0, 'Create migration scripts!')
            self._db_configure_steps.insert(0, 'DB initialization done!')
        os.chdir(cwd)
        return True

    def remove_migrations_dir(self):
        flg = False
        app_parent = os.path.dirname(self._app_dir)
        migrate_dir = os.path.join(app_parent, self._alembic_dir_name)
        if os.path.exists(migrate_dir) and os.path.isdir(migrate_dir):
            from shutil import rmtree
            rmtree(migrate_dir, ignore_errors=True)
            flg = not os.path.exists(migrate_dir)
        return flg

    def create_inst_marker(self):
        _marker = self.get_inst_marker()
        with open(_marker, 'w', encoding='utf-8') as fp:
            _now = datetime.now()
            _tm = str(_now.timestamp()).replace('.', '')
            fp.write(str(_tm))

    def remove_inst_marker(self):
        _marker = self.get_inst_marker()
        if os.path.exists(_marker) and os.path.isfile(_marker):
            os.remove(_marker)
        return not os.path.exists(_marker)

    def check_inst_marker(self):
        _marker = self.get_inst_marker()
        return os.path.exists(_marker) and os.path.isfile(_marker)

    def get_inst_marker(self):
        _marker = os.path.join(os.path.dirname(self._app_dir), self.get_installation_marker_name())
        return _marker

    def set_app_dir(self, work_dir):
        if os.path.exists(work_dir) and os.path.isdir(work_dir):
            self._app_dir = work_dir

    def get_installation_marker_name(self):
        return self._install_marker

    def get_db_configure_steps(self):
        return self._db_configure_steps

# -*- coding: utf-8 -*-
import sys
import os
import subprocess
from .code_helper import CodeHelper


class ExtendProcesses:
    _class_file = __file__

    @staticmethod
    def get_exec_path():
        return os.path.dirname(os.path.dirname(ExtendProcesses._class_file))

    @staticmethod
    def run(script, script_args=[], errors=''):
        """ """
        if not CodeHelper.check_file(script):
            raise FileExistsError('Try execute undefined script: {}'. format(script))
        cmd_args = []
        cmd_args.append(sys.executable)
        cmd_args.append(script)
        if script_args:
            for ix in script_args:
                cmd_args.append(ix)
        stdin_point = subprocess.PIPE
        stdout_point = subprocess.PIPE
        stderr_point = open(errors, 'w', encoding='utf8') if '' != errors and CodeHelper.check_file(errors) else subprocess.PIPE
        script_call = subprocess.Popen(cmd_args, stdin=stdin_point,
                                            stdout=stdout_point, stderr=stderr_point,
                                            cwd=ExtendProcesses.get_exec_path(),
                                            env={**os.environ, 'PYTHONPATH': os.pathsep.join(sys.path)},
                                            encoding='utf8')
        return script_call

    @staticmethod
    def update_sys_path():
        sys.path.insert(0, ExtendProcesses.get_exec_path())

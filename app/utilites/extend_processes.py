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
        stderr_point = subprocess.PIPE
        if '' != errors and CodeHelper.check_file(errors):
            stderr_point = open(errors, 'w', encoding='utf8')
        __call_args = {}
        __call_args['stdin'] = stdin_point
        __call_args['stdout'] = stdout_point
        __call_args['stderr'] = stderr_point
        __call_args['cwd'] = ExtendProcesses.get_exec_path()
        __call_args['env'] = {**os.environ, 'PYTHONPATH': os.pathsep.join(sys.path)}
        if not sys.platform.startswith('win'):
            __call_args['encoding'] = 'utf8' # Exception on windows 7 with code/decode in subprocess
        script_call = subprocess.Popen(cmd_args, **__call_args)
        return script_call

    @staticmethod
    def update_sys_path():
        sys.path.insert(0, ExtendProcesses.get_exec_path())

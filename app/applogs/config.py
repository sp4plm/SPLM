# -*- coding: utf-8 -*-
import os


class Config:
    _class_file = __file__
    _debug_name = 'AppLogsConfig'
    _def_rotate_size = 1024 * 1024 * 10  # 10 megabites
    error_file = 'flask-error.log'
    info_file = 'flask-info.log'

    def __init__(self, logs_path=''):
        self._app = None
        self._app_log_path = logs_path
        self._rotate_size = self._def_rotate_size
        self._rotate_size = 1024 * 1024 * 2  # 2 megabites
        # self._rotate_size = 1024  # test

    def init_app(self, flask_app):
        if flask_app is not None:
            self._app = flask_app

    def get_logger(self, name):
        pass

    def configure(self):
        """
        Метод настраивает логирование приложения flask в определенные файлы
        :return:
        """
        import logging
        from logging.config import dictConfig
        if not os.path.exists(self._app_log_path):
            raise Exception('Undefine path for log files!')
        dictConfig(self.get_app_logger_conf())

    def get_log_loggers(self):
        _d = {}
        _d['flask.app'] = {
            'handlers': ['infolog', 'errorlog'],
            'level': 'INFO',
            'propagate': True
        }
        _d['app'] = _d['flask.app']
        return _d

    def get_log_handlers(self):
        _d = {}
        """
        logging создает столько файлов сколько создано обработчиков
        """
        _d['infolog'] = {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(self._app_log_path, self.info_file),
            'mode': 'a',
            'maxBytes': self._rotate_size,  # 2MB
            'backupCount': 5,
        }
        _d['errorlog'] = {
            'level': 'ERROR',
            'formatter': 'advanced',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(self._app_log_path, self.error_file),
            'mode': 'a',
            'maxBytes': self._rotate_size,  # 2MB
            'backupCount': 5,
        }
        """
        # from flaskbb code 
        _d['console'] = {
            'level': 'NOTSET',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        }
        # from https://flask.palletsprojects.com/en/latest/logging/
        _d['wsgi'] = {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
        """
        return _d

    def get_log_formatters(self):
        _d = {}
        _d['default'] = {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        }
        _d['advanced'] = {
            'format': '[%(asctime)s] %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        }
        return _d

    def get_app_logger_conf(self):
        _dict = {}
        _dict['version'] = 1
        # add formatters
        _dict['formatters'] = self.get_log_formatters()
        # add handlers
        _dict['handlers'] = self.get_log_handlers()
        # add loggers
        """
        # add root logger | from https://flask.palletsprojects.com/en/latest/logging/
        _dict['root'] =  {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
        """
        _dict['loggers'] = self.get_log_loggers()
        return _dict

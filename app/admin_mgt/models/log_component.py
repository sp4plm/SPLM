import logging
from os import path as opath, utime

class LogComponent:
    @staticmethod
    def get_app_logger(name: str = '', logger_file=''):
        log_name = 'models'
        if '' != name:
            log_name += '.' + name
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)
        if not opath.exists(logger_file):
            with open(logger_file, 'a') as fm:
                utime(logger_file, None)
        file_handler = logging.FileHandler(logger_file, 'w', 'utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        return logger
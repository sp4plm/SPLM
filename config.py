# -*- coding: utf-8 -*-

import os
from datetime import timedelta
from werkzeug.security import generate_password_hash


#class Config(object):

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
APP_DATA_PATH = os.path.join(APP_ROOT, 'app', 'data')
APP_CONFIG_PATH = os.path.join(APP_ROOT, 'app', 'cfg')

DEBUG = True

ADMINS = frozenset(['youremail@yourdomain.com'])
# имена переменных окружения нужно читать из файла
PORTAL_MAN_USER = os.environ.get('SPLMPY_PORTAL_USER') or \
                          'manager'
_t = os.environ.get('SPLMPY_PORTAL_SECRET') or 'testadmin'
PORTAL_MAN_SECRET = generate_password_hash(_t)
SECRET_KEY = 'This string will be replaced with a proper key in production.'

SQLALCHEMY_DATABASE_URI = os.environ.get('SPLMPY_DATABASE_URL') or \
                          'sqlite:///' + os.path.join(APP_CONFIG_PATH, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(APP_CONFIG_PATH, 'migrations')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
SESSION_REFRESH_EACH_REQUEST = True

THREADS_PER_PAGE = 8

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "somethingimpossibletoguess"

RECAPTCHA_USE_SSL = False
RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'
RECAPTCHA_OPTIONS = {'theme': 'white'}

APP_URL_PREFIX = '/'  # префикс для URL при использовании при одном домене

CONFIGURATOR_WAY='admin_mgt.portal_installer'
CONFIGURATOR_MARK_NAME = os.path.join(APP_CONFIG_PATH, 'splm_installation')

APP_NAME_THEMES_IDENTIFIER = "splm"
THEME_PATHS = os.path.join(APP_CONFIG_PATH, 'themes')  # or themes_mgt use mod name for themes ??????
DEFAULT_THEME = "light"

#SCHEDULER
SCHEDULER_TIMEZONE = "Europe/Moscow"

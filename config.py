# -*- coding: utf-8 -*-

import os
from datetime import timedelta
from werkzeug.security import generate_password_hash


#class Config(object):

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
APP_DATA_PATH = os.path.join(APP_ROOT, 'app', 'data')

DEBUG = True

ADMINS = frozenset(['youremail@yourdomain.com'])
# имена переменных окружения нужно читать из файла
PORTAL_MAN_USER = os.environ.get('SPLMPY_PORTAL_USER') or \
                          'manager'
PORTAL_MAN_SECRET = os.environ.get('SPLMPY_PORTAL_SECRET') or \
                          generate_password_hash('testadmin')
SECRET_KEY = 'This string will be replaced with a proper key in production.'

SQLALCHEMY_DATABASE_URI = os.environ.get('SPLMPY_DATABASE_URL') or \
                          'sqlite:///' + os.path.join(APP_DATA_PATH, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(APP_DATA_PATH, 'migrations')
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

CONFIGURATOR_WAY='admin_mgt.portal_installer'
CONFIGURATOR_MARK_NAME = os.path.join(os.path.dirname(__file__), 'splm_installation')

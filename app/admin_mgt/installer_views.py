# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса портала по URL - /portal
"""
import subprocess

from flask import Blueprint, request, flash, g, session, redirect, url_for

from ..utilites.extend_processes import ExtendProcesses

from .admin_utils import os # import embeded pythons
from .admin_utils import app_api # import application globals
from .admin_utils import AdminConf, AdminUtils # import current module libs
from .configurator import Configurator

from .decorators import requires_auth

mod = Blueprint('portal_installer', __name__, url_prefix=AdminConf.MOD_WEB_ROOT + '/installer',
                static_folder=AdminConf.get_web_static_path(),
                template_folder=AdminConf.get_web_tpl_path())


@mod.route('/run', methods=['POST'])
def run_installer():
    """
    Функция
    :return:
    """
    html = 'Первичное конфигурирование не требуется!'
    _portal_configurator = Configurator()
    _portal_configurator.set_app_dir(app_api.get_app_root_dir())
    if not _portal_configurator.check_inst_marker():
        html = ''
        root_path = os.path.dirname(__file__)
        script = os.path.join(root_path, 'installer_process.py')
        data = None
        data = ExtendProcesses.run(script, [])
        output, errors = data.communicate()
        # print('OUTPUT: =========>', output)
        # print('ERRORS: =========>', errors)
        # html += '<h2>Process:</h1>'
        # html += '<br />'
        # html += str(data)
        # html += '<hr />'
        # html += '<h3>OUTPUT:</h2>'
        # html += '<br />'
        # html += str(output)
        # html += '<hr />'
        # html += '<h3>ERRORS:</h2>'
        # html += '<br />'
        # html += str(errors)
        # html += '<hr />'
        html += '<p>'
        html += 'Первичное конфигурирование успешно произведено!'
        html += '</p>'
    return html


@mod.route('/uninstall', methods=['POST'])
def run_uninstall():
    """
    Функция производит удаление файла базы данных, директории migrations и маркера установки
    :return:
    """
    html = 'Попытка деинсталяции завершилась с ошибками!'
    _portal_configurator = Configurator()
    _portal_configurator.set_app_dir(app_api.get_app_root_dir())
    if _portal_configurator.check_inst_marker():
        # удаляем маркер установки - чтобы закрыть портал для доступа всем
        flg_mark = _portal_configurator.remove_inst_marker()
        # удаляем директорию migrations
        flg_db_cfg = _portal_configurator.remove_migrations_dir()
        # удаляем файл базы данных
        from app import app
        db_path = app.config['SQLALCHEMY_DATABASE_URI']
        db_path = db_path.replace('sqlite:///', '')
        if os.path.exists(db_path):
            os.unlink(db_path)
            flg_db = not os.path.exists(db_path)
        if flg_db and flg_mark and flg_db_cfg:
            html = 'Деинсталляция успешно произведена!'
    return html


@mod.route('/backup', methods=['POST'])
def run_backup():
    """
    Функция создает резервную копию файла базы данных, директории migrations и директории cfg административного модуля
    :return:
    """
    html = ''
    _portal_configurator = Configurator()
    _portal_configurator.set_app_dir(app_api.get_app_root_dir())
    if _portal_configurator.check_inst_marker():
        html = 'Резервная копия успешно создана'
    return html


@mod.route('', methods=['GET'])
def installer():
    """
    Отображение страницы инсталлятора
    :return:
    """
    tmpl_vars = {}
    tmpl_vars['title'] = 'Установщик портала'
    tmpl_vars['page_title'] = 'Первичная установка портала'
    tmpl_vars['page_side_title'] = 'Действия'

    _portal_configurator = Configurator()
    _portal_configurator.set_app_dir(app_api.get_app_root_dir())
    tmpl_vars['already_c0nfigured'] = _portal_configurator.check_inst_marker()

    _tpl_name = os.path.join(AdminConf.MOD_NAME, 'portal', 'installer.html')
    return app_api.render_page(_tpl_name, **tmpl_vars)

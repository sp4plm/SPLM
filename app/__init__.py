import os

from flask import Flask, session, g, redirect, url_for, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from .applogs import LogsConf
from app.module_mgt.manager import Manager

from flask_themes2 import Themes

from flask_apscheduler import APScheduler

__package_path = os.path.dirname(__file__)  # app directory (app package directory)
__app_work_path = os.path.dirname(__package_path)  # parent directory of app (application directory - all prog code)
__app_instance_path = os.path.join(__app_work_path, 'instance')

# must be configured before create instance Flask app
# https://flask.palletsprojects.com/en/latest/logging/
from config import APP_LOG_PATH as LOG_PATH
LogsConf(LOG_PATH).configure()

app = Flask(__name__, root_path=__package_path)
app.config.from_object('config')

# создание основных директорий для работы приложения
# директория для пользовательских данных
__dir_key = 'APP_DATA_PATH'
if not os.path.exists(app.config[__dir_key]):
    try: os.mkdir(app.config[__dir_key], )
    except: pass
# директория хранения логов
__dir_key = 'APP_LOG_PATH'  # перенесено в config для настройки через logging
__dir_name = app.config[__dir_key]  # перенесено в config для настройки через logging
if not os.path.exists(__dir_name):
    try: os.mkdir(__dir_name)
    except: pass
# директория для фалов изменяемых при работе портала
__dir_key = 'APP_CONFIG_PATH'
if not os.path.exists(app.config[__dir_key]):
    try: os.mkdir(app.config[__dir_key])
    except: pass
# директория хранения тем приложения
__dir_key = 'THEME_PATHS'
if not os.path.exists(app.config[__dir_key]):
    try: os.mkdir(app.config[__dir_key])
    except: pass

# try set url prefix
# app.config['APP_URL_PREFIX'] - for multiproject
__dir_key = 'APP_CONFIG_PATH'
__prefix_file = os.path.join(app.config[__dir_key], 'prefix.url')
if os.path.exists(__prefix_file):
    _test_prefix = ''
    with open(__prefix_file, 'r', encoding="utf-8") as _fp:
        _test_prefix = _fp.read().strip("\n\r")
    if _test_prefix:
        _test_prefix = '/' + _test_prefix.lstrip('/').rstrip('/')
        # print('app.__init__->generate APP_URL_PREFIX: _test_prefix', _test_prefix)
        app.config['APP_URL_PREFIX'] = _test_prefix
        # далее требуется развести авторизацию приложений под одним доменом, но в разных директориях
        app.config['REMEMBER_COOKIE_PATH'] = _test_prefix.rstrip('/')  # '/app_1'
        app.config['SESSION_COOKIE_NAME'] = app.config['SESSION_COOKIE_NAME'] + _test_prefix.replace('/', '#')
        # дополнительно надо менять app.config['SECRET_KEY'] and app.config['WTF_CSRF_SECRET_KEY']
        app.config['SECRET_KEY'] = app.config['SECRET_KEY'] + _test_prefix.replace('/', '!&@')
        app.config['WTF_CSRF_SECRET_KEY'] = app.config['WTF_CSRF_SECRET_KEY'] + _test_prefix.replace('/', '#%$')
    pass

# управление модулями
mod_manager = Manager(app)
# собираем информацию о модулях
mod_manager.compile_modules_info()

# теперь требуется скопировать тему поумолчанию из модуля управления темами
mod_name = 'themes_mgt'
_src_pth = os.path.join(os.path.dirname(__file__), mod_name, 'themes_list')
_trgt_pth = os.path.join(app.config['THEME_PATHS'])
if os.path.exists(_trgt_pth):
    if not os.path.exists(_src_pth):
        print('Application.Start: no default theme -> %s' % _src_pth)
    else:
        from shutil import copytree as _cd
        _lst = os.scandir(_src_pth)
        for _d in _lst:
            _sd = os.path.join(_src_pth, _d.name)
            _td = os.path.join(_trgt_pth, _d.name)
            if os.path.exists(_sd) and not os.path.exists(_td):
                res = _cd(_sd, _td, dirs_exist_ok=True)

# инициализации и загрузка тем
Themes(app, app_identifier=app.config['APP_NAME_THEMES_IDENTIFIER'])

from app import app_api
from app.utilites.code_helper import CodeHelper
from app.utilites.portal_navi import PortalNavi


db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
# flask_login messages
login_manager.login_message = u'Авторизуйтесь пожалуйста для доступа.' # LOGIN_MESSAGE
login_manager.needs_refresh_message = u'Авторизуйтесь пожалуйста для доступа.' # REFRESH_MESSAGE

# требуется обдумать и реализовать переход после авторизации на стартовую страницу портала - из настроек
login_manager.login_view = 'portal.login'  # данный параметр требуется устанавливать через настройки

from app.admin_mgt.models.user import User
login_manager.anonymous_user = User

app.add_template_global(app_api.get_app_root_tpl, name='app_root_tpl') # функция в шаблоне - получение главного шаблона портала
app.add_template_global(app_api.is_app_module_enabled, name='check_module')
app.add_template_global(PortalNavi.get_mod_tpl_path, name='mod_tpl_path')
app.add_template_global(PortalNavi.get_main_navi, name='main_navi')
app.add_template_global(PortalNavi.get_top_navi, name='top_navi')
app.add_template_global(PortalNavi.get_user_custom_navi, name='ucustom_navi')
# app.add_template_global(PortalSettings.get_copyright, name='copyright')
app.add_template_global(app_api.get_portal_labels('siteCopyright'), name='copyright')
app.add_template_global(app_api.get_portal_labels, name='portal_labels')
# app.add_template_global(PortalSettings.get_jquery_info, name='portal_jquery')
# app.add_template_global(PortalSettings.get_js_libs_info, name='portal_js_libs')
app.add_template_global(app_api.get_portal_version(), name='portal_ver')
app.add_template_global(app_api.get_portal_locale(), name='page_lang')

# logger view
from app.applogs.views import mod as web_logs
# app.register_blueprint(web_logs,
#                        url_prefix=app.config['APP_URL_PREFIX'].rstrip('/') + '/' + web_logs.url_prefix.lstrip('/'))
mod_manager.register_module_http_handler(web_logs, 'web_logs')

# обработка запроса корня портала
from app.views import mod as app_views
# app.register_blueprint(app_views)
mod_manager.register_module_http_handler(app_views, 'app_views')

# регистрируем модули приложения
from app.admin_mgt.models.links import Link
from app.admin_mgt.models.embedded_user import EmbeddedUser
# модуль редактора
from app.kv_editor.views import mod as kve_mod
# app.register_blueprint(kve_mod)
mod_manager.register_module_http_handler(kve_mod, 'kv_editor')

from app.admin_mgt.views import mod as adminModule
from app.admin_mgt.views import portal_mod
from app.admin_mgt.views import installer_mod
from app.admin_mgt.views import management_mod
from app.admin_mgt.views import configurator_mod
# app.register_blueprint(adminModule)
mod_manager.register_module_http_handler(adminModule, 'admin_mgt')
# app.register_blueprint(portal_mod)
mod_manager.register_module_http_handler(portal_mod, 'admin_mgt')
# app.register_blueprint(installer_mod)
mod_manager.register_module_http_handler(installer_mod, 'admin_mgt')
# app.register_blueprint(management_mod)
mod_manager.register_module_http_handler(management_mod, 'admin_mgt')
# app.register_blueprint(configurator_mod)
mod_manager.register_module_http_handler(configurator_mod, 'admin_mgt')

from app.files_mgt.views import mod as files_mgt_web
# app.register_blueprint(files_mgt_web)
mod_manager.register_module_http_handler(files_mgt_web, 'files_mgt')

from app.module_mgt.views import mod as module_mgt_web
# app.register_blueprint(module_mgt_web)
mod_manager.register_module_http_handler(module_mgt_web, 'module_mgt')

from app.themes_mgt.views import mod as themes_mgt_web
# app.register_blueprint(themes_mgt_web)
mod_manager.register_module_http_handler(themes_mgt_web, 'themes_mgt')

if app_api.is_app_module_enabled('ts_mgt'):
    from app.ts_mgt.views import mod as tsModule
    app.register_blueprint(tsModule)

# settings editor for printer pdf
if app_api.is_app_module_enabled('printer'):
    from app.printer.views import mod as print_pdf
    app.register_blueprint(print_pdf)

if app_api.is_app_module_enabled('user_mgt'):
    from app.user_mgt.models.users import User
    from app.user_mgt.models.roles import Role
    from app.user_mgt.views import mod as userModule
    # app.register_blueprint(userModule)
    mod_manager.register_module_http_handler(userModule, 'user_mgt')
else:
    pass
    """ Установить настройку что открытый портал по умолчанию !!!! """

from app.query_mgt.views import mod as query_mgtModule
app.register_blueprint(query_mgtModule)

from app.wiki.views import mod as wikiModule
# app.register_blueprint(wikiModule)
mod_manager.register_module_http_handler(wikiModule, 'wiki')

from app.onto_mgt.views import mod as ontoModule
app.register_blueprint(ontoModule)

from app.portaldata_mgt.views import mod as publisherModule
app.register_blueprint(publisherModule)

from app.search_mgt.views import mod as searchModule
app.register_blueprint(searchModule)

# динамическая загрузка сторонних модулей
mod_manager.load_modules_http_handlers()


@app.errorhandler(404)
def not_found(error):
    # требуется проверить - может быть портал только развернут, следовательно надо получить адрес административного
    # интерфейса и перенаправить
    # all_urls = [str(_u) for _u in app.url_map.iter_rules()]
    # if '/' not in all_urls:
    _marker = app.config['CONFIGURATOR_MARK_NAME']
    _url_prefix = app.config['APP_URL_PREFIX']
    if not os.path.exists(_marker):
        return redirect(url_for('portal.welcome'))
    app.logger.info('Undefined request path -> ' + str(request.path))
    return app_api.render_page('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    # db.session.rollback()
    app.logger.exception('Exception occurred -> ' + str(error))
    return app_api.render_page('errors/500.html'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    # db.session.rollback()
    """"""
    """
    Отлавливаем в логирование неотлавливаемые ошибки
    """
    app.logger.exception('Exception occurred -> ' + str(e))
    return app_api.render_page('errors/500.html'), 500


@app.before_request
def before_request():
    # надо выполнять простую проверку на наличие файла - что портал установлен и инициализирован
    # если файла нет перенаправлять на специальный урл инсталлятор портала? который закрыт паролем к административного
    # интерфейса
    _test_url = url_for('portal.welcome')
    _marker = app.config['CONFIGURATOR_MARK_NAME']
    _url_prefix = app.config['APP_URL_PREFIX']
    if not os.path.exists(_marker):
        opened_urls = []
        _url = url_for('portal.welcome')
        opened_urls.append(_url)
        install_url = url_for('portal_installer.installer')
        opened_urls.append(install_url)

        if request.path not in opened_urls and \
                -1 == request.path.find('/static/') and \
                -1 == request.path.find('/_themes/') and \
                not request.path.startswith(install_url):
            return redirect(_url)

    # надо отсеч статические файлы
    if 0 < request.path.find('/static/') or 0 < request.path.find('/_themes/'):
        return

    g.user = None
    session.permanent = True
    # print('app.__init__.before_request->session:', session.__dict__)
    # print('app.__init__.before_request->current_user:', current_user)
    # print('app.__init__.before_request->request.path:', request.path)
    # print('app.__init__.before_request->session.get(\'csrf_token\'):', session.get('csrf_token'))
    g.user = User()  # устанавление пользователя - гостя
    if current_user.is_authenticated:
        if '_user_id' in session:
            uid = int(session['_user_id'])
            if 0 < uid:
                g.user = User.query.get(session['_user_id'])
            else:
                # для администратора портала
                g.user = EmbeddedUser()

        _admin_mgt_api = app_api.get_mod_api('admin_mgt')
        _portal_modes_util = _admin_mgt_api.get_portal_mode_util()
        _portal_mode = None
        if _portal_modes_util is not None:
            _portal_mode = _portal_modes_util.get_current()
        if _portal_mode is not None and _portal_mode.use_redirecting():
            pass
            # проверяем наличие файла процесса публикации и перенаправляем пользователя на страницу
            # про процесс публикации данных
            # чтобы не было зацикливания - надо проверить а не находимся ли мы уже тут
            # publish_proc_met = 'portal.publish_proc_info' # Наверно надо вынести в настройки - main.ini
            _redirect_target = _portal_mode.get_target()
            opens_endpoints = []
            # opens_endpoints = [publish_proc_met, 'data_management.publish_process_step',
            #                    'data_management.publish_process_done', 'data_management.publish_process_break']
            opens_endpoints = _portal_mode.get_opened()
            opens_endpoints.append('static') # для правиgльной работы css и js на определенных режимах
            # нужно добавить перенаправление темы
            opens_endpoints.append('_themes.static') # для правиgльной работы css и js на определенных режимах
            if request.endpoint not in opens_endpoints:
                """ перенаправляем на страницу информации о процессе обновления данных """
                publish_proc_page = url_for(_redirect_target)
                return redirect(publish_proc_page)


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# импорт здесь во избежании зацикленности
from app.admin_mgt.jobs import Jobs
# получаем все существующие задания
j = Jobs("schedule").get_job_data()
# назначаем в scheduler ранее активные задания
[Jobs.update_job(item, j[item], scheduler=scheduler) for item in j]

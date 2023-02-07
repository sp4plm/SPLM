import os

from flask import Flask, session, g, redirect, url_for, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.module_mgt.manager import Manager

from flask_themes2 import Themes

from flask_apscheduler import APScheduler



app = Flask(__name__, root_path=os.path.dirname(__file__))
app.config.from_object('config')

# создание основных директорий для работы приложения
# директория для пользовательских данных
__dir_key = 'APP_DATA_PATH'
if not os.path.exists(app.config[__dir_key]):
    os.mkdir(app.config[__dir_key])
# директория хранения логов
__dir_name = os.path.join(app.config[__dir_key], 'logs')
if not os.path.exists(__dir_name):
    os.mkdir(__dir_name)
# директория для фалов изменяемых при работе портала
__dir_key = 'APP_CONFIG_PATH'
if not os.path.exists(app.config[__dir_key]):
    os.mkdir(app.config[__dir_key])
# директория хранения тем приложения
__dir_key = 'THEME_PATHS'
if not os.path.exists(app.config[__dir_key]):
    os.mkdir(app.config[__dir_key])

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

from app.utilites.extend_processes import ExtendProcesses


db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
# flask_login messages
login_manager.login_message = u'Авторизуйтесь пожалуйста для доступа.' # LOGIN_MESSAGE
login_manager.needs_refresh_message = u'Авторизуйтесь пожалуйста для доступа.' # REFRESH_MESSAGE

# требуется обдумать и реализовать переход после авторизации на стартовую страницу портала - из настроек
login_manager.login_view = 'portal.login'  # данный параметр требуется устанавливать через настройки

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

# обработка запроса корня портала
from app.views import mod as app_views
app.register_blueprint(app_views)

# регистрируем модули приложения
from app.admin_mgt.models.links import Link
from app.admin_mgt.models.embedded_user import EmbeddedUser
# модуль редактора
from app.kv_editor.views import mod as kve_mod
app.register_blueprint(kve_mod)

from app.admin_mgt.views import mod as adminModule, portal_mod, installer_mod, management_mod, configurator_mod
app.register_blueprint(adminModule)
app.register_blueprint(portal_mod)
app.register_blueprint(installer_mod)
app.register_blueprint(management_mod)
app.register_blueprint(configurator_mod)

from app.files_mgt.views import mod as files_mgt_web
app.register_blueprint(files_mgt_web)

from app.module_mgt.views import mod as module_mgt_web
app.register_blueprint(module_mgt_web)

from app.themes_mgt.views import mod as themes_mgt_web
app.register_blueprint(themes_mgt_web)

if app_api.is_app_module_enabled('user_mgt'):
    from app.user_mgt.models.users import User
    from app.user_mgt.models.roles import Role
    from app.user_mgt.views import mod as userModule
    app.register_blueprint(userModule)

from app.query_mgt.views import mod as query_mgtModule
app.register_blueprint(query_mgtModule)

from app.wiki.views import mod as wikiModule
app.register_blueprint(wikiModule)

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
    all_urls = [str(_u) for _u in app.url_map.iter_rules()]
    if '/' not in all_urls:
        return redirect(url_for('portal.welcome'))
    return app_api.render_page('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    # db.session.rollback()
    return app_api.render_page('errors/500.html'), 500


@app.before_request
def before_request():
    # надо выполнять простую проверку на наличие файла - что портал установлен и инициализирован
    # если файла нет перенаправлять на специальный урл инсталлятор портала? который закрыт паролем к административного
    # интерфейса
    _marker = app.config['CONFIGURATOR_MARK_NAME']
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
    g.user = None
    session.permanent = True
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



def job_by_script(action):
    log = os.path.join(app.config['APP_DATA_PATH'], "logs", "job_by_script.log")
    with open(log, "w", encoding="utf-8") as f:
        f.write("")

    script = os.path.join(app.config['APP_ROOT'], "app", action)
    data = ExtendProcesses.run(script, [], errors = log)


scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

from app.admin_mgt.jobs import Jobs
# получаем все существующие задания
j = Jobs("schedule").get_job_data()

# назначаем в scheduler ранее активные задания
for item in j:
    if 'active' in j[item] and j[item]['active'] == "1":
        if 'period' in j[item] and 'action' in j[item] and 'name' in j[item]:
            # вычисляем период 
            minute, hour, day, month, day_of_week = j[item]['period'].split(' ')
            # запускаем активные задания с id <name>
            scheduler.add_job(id = j[item]['name'], func=job_by_script, trigger="cron", day_of_week=day_of_week, month=month, day=day, hour=hour, minute=minute, second="0", args=[j[item]['action']])

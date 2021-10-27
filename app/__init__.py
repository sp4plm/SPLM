import os
import sys
# print(sys.modules.get(__name__))
# kk = sys.modules.get(__name__)
# if hasattr(kk, "__file__"):
#     print(os.path.dirname(os.path.abspath(kk.__file__)))

from flask import Flask, session, render_template, g, redirect, url_for, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.module_mgt.manager import Manager

app = Flask(__name__, root_path=os.path.dirname(__file__))
app.config.from_object('config')

# управление модулями
mod_manager = Manager(app)

from app import app_api
from app.app_api import CodeHelper
from app.app_api import PortalNavi

# собираем информацию о модулях
mod_manager.compile_modules_info()

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
app.add_template_global(PortalNavi.get_main_navi, name='main_navi')
app.add_template_global(PortalNavi.get_top_navi, name='top_navi')
app.add_template_global(PortalNavi.get_user_custom_navi, name='ucustom_navi')
# app.add_template_global(PortalSettings.get_copyright, name='copyright')
app.add_template_global(app_api.get_portal_labels, name='portal_labels')
# app.add_template_global(PortalSettings.get_jquery_info, name='portal_jquery')
# app.add_template_global(PortalSettings.get_js_libs_info, name='portal_js_libs')

# обработка запроса корня портала
from app.views import mod as app_views
app.register_blueprint(app_views)

# регистрируем модули приложения
from app.admin_mgt.models.links import Link
from app.admin_mgt.models.embedded_user import EmbeddedUser

from app.admin_mgt.views import mod as adminModule, portal_mod, installer_mod, management_mod, configurator_mod
app.register_blueprint(adminModule)
app.register_blueprint(portal_mod)
app.register_blueprint(installer_mod)
app.register_blueprint(management_mod)
app.register_blueprint(configurator_mod)

from app.files_mgt.views import mod as files_mgt_web
app.register_blueprint(files_mgt_web)

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

from app.publish_mgt.views import mod as publisherModule
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
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    # db.session.rollback()
    return render_template('errors/500.html'), 500


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
        # проверяем наличие файла процесса публикации и перенаправляем пользователя на страницу
        # про процесс публикации данных
        # чтобы не было зацикливания - надо проверить а не находимся ли мы уже тут
        # publish_proc_met = 'portal.publish_proc_info' # Наверно надо вынести в настройки - main.ini
        # opens_endpoints = [publish_proc_met, 'data_management.publish_process_step',
        #                    'data_management.publish_process_done', 'data_management.publish_process_break']
        # opens_endpoints.append('static') # для правильной работы css и js на определенных режимах
        # if request.endpoint not in opens_endpoints and PortalSettings.check_publish_pid_exists():
        #     """ перенаправляем на страницу информации о процессе обновления данных """
        #     publish_proc_page = url_for(publish_proc_met)
        #     return redirect(publish_proc_page)

# -*- coding: utf-8 -*-

"""
Для удобства импорта API в любую точку приложения целиком или по частям
импорт нужных функциональностей производим в функциях
"""

# import os.path
# import re

# if 'app' not in globals():
#     from app import app

# вспомогательная утиллита для работы с файлами и не только
# from app.utilites.code_helper import CodeHelper
# from app.utilites.some_config import SomeConfig
# from app.utilites.portal_navi import PortalNavi
# from app.query_mgt.query import Query
# from app.module_mgt.manager import Manager

# from rdflib import Namespace

# from flask_themes2 import render_theme_template, get_theme, static_file_url


def get_config_util():
    """
    Функция возвращает класс для унифицированной работы с файлами конфигов (ini)
    :return: класс SomeConfig
    """
    from app.utilites.some_config import SomeConfig
    return SomeConfig


def get_app_config():
    """
    Функция возвращает инструмент для получения данных о настройках приложения.
    :return: экземляр класса SomeConfig
    """
    admin_api = get_mod_api('admin_mgt')
    cfg = get_config_util()(admin_api.get_config_path())
    return cfg


def get_app_url_prefix():
    """
    Функция возвращает установленный URL префикс для всех запросов приложения
    :return: URL префикс
    :rtype str:
    """
    from app import app
    _prefix = app.config['APP_URL_PREFIX']
    if '/' == _prefix:
        _prefix = ''
    return _prefix


def get_mod_manager():
    from app import app
    from app.module_mgt.manager import Manager
    mod_manager = Manager(app)
    return mod_manager


def get_mod_decscription(mod_name):
    """
    Функция возвращает описание, хранящееся в dublin.ttl, модуля с именем mod_name (имя директории)
    :param mod_name: string: Имя модуля (имя директории) для получения описания - dublin.ttl
    :return: None или rdflib.Graph() Если модуля нет то None, если модуль есть то rdflib.Graph()
    rdflib.Graph() - может оказаться пустым, если модуль есть а dublin.ttl отсутствует
    """
    mod_manager = get_mod_manager()
    mod_descr = mod_manager.get_mod_decscription(mod_name)
    return mod_descr


def get_mod_api(modname):
    """
    Функция форвращает экземпляр класса ModApi модуля modname описанного в файле mod_api
     расположеного в корне модуля modname
    :param modname: string: имя модуля (имя директории)
    :return: ModApi: None или экземпляр класса ModApi
    """
    mod_manager = get_mod_manager()
    obj_comp = None
    try:
        obj_comp = mod_manager.get_mod_api(modname)
    except Exception as ex:
        raise ex
    return obj_comp # type: ModApi


def is_app_module_enabled(mod_name):
    """
    Функция проверяет подключен ли модуль mod_name к порталу
    :param mod_name: string: имя модуля (имя директории)
    :return:
    """
    mod_manager = get_mod_manager()
    return mod_manager.module_exists(mod_name)


def get_app_root_tpl():
    """
    Функция возвращает имя основного HTML шаблона портала
    :return: имя HTML шаблона
    """
    from flask_themes2 import static_file_url
    return static_file_url(get_current_theme(), "layout.html").strip("/")


def get_portal_locale():
    _lang_code = 'ru'
    return _lang_code


def get_max_filesize_upload():
    """
    Функция возвращает  максимальный размер файла в
    :return: 1024 * 1024 + 50
    """
    app_config = get_app_config()
    return 1024 * 1024 + 50


def get_allowed_file_exts():
    """
    Функция возвращает допустимых расширений файлов
    :return: ('jpg', 'jpeg', 'xml', 'png', 'gif', 'docx', 'doc', 'pdf', 'ttl', 'xls', 'xlsx')
    """
    app_config = get_app_config()
    return ('jpg', 'jpeg', 'xml', 'png', 'gif', 'docx', 'doc', 'pdf', 'ttl', 'xls', 'xlsx', 'xlsm')


def get_app_root_dir():
    """
    Функция возвращает путь к директории приложения
    :return: полный путь
    """
    import os.path
    return os.path.dirname(__file__)


def get_mod_path(mod_name):
    """
    Функция возвращает полный путь к директории модуля
    :param mod_name: имя модуля портала
    :return: полный путь
    """
    import os.path
    pth = ''
    pth += os.path.join(get_app_root_dir(), mod_name)
    return pth


def get_app_data_path():
    """
    Функция возвращает полный путь к директории данных приложения
    :return: полный путь
    """
    from app import app
    pth = app.config['APP_DATA_PATH']
    return pth


def get_app_cfg_path():
    """
    Функция возвращает полный путь к директории настроечных файлов
    :return: полный путь
    """
    from app import app
    pth = app.config['APP_CONFIG_PATH']
    return pth


def get_mod_data_path(mod_name):
    """
    Функция возвращает полный путь к директории указанного модуля mod_name
    :param mod_name: имя модуля
    :return: полный путь
    """
    import os.path
    from app.utilites.code_helper import CodeHelper
    mod_data_path = ''
    mod_data_path = os.path.join(get_app_data_path(), mod_name)
    if not CodeHelper.check_dir(mod_data_path):
        print('app_api.get_mod_data_path(): ', 'The module "{}" data directory does not exists -> '.format(mod_name), mod_data_path)
    return mod_data_path


def get_save_meta_path(mod_name, _create=False):
    """
    Функция возвращает полный путь для сохранения измененных файлов (конфигурационных или шаблонов запросов) модуля
    mod_name
    :param mod_name: имя модуля
    :param _create: флаг указывающий, что требуется создать даную директорию если таковой еще нет
    :return: полный путь
    """
    import os.path
    _meta_pth = os.path.join(get_app_cfg_path(), mod_name)
    if _create and not os.path.exists(_meta_pth):
        try: os.mkdir(_meta_pth)
        except: pass
    return _meta_pth


def get_meta_path(mod_name, relative):
    """
    Функция возвращает полный путь до указанного файла relative относительно модуля  mod_name
    :param mod_name: имя модуля для искомого файла
    :param relative: имя файла отностительно директории модуля
    :return: полный путь
    """
    import os.path
    _search_pth = os.path.join(get_mod_path(mod_name), relative)
    # работаем только с файлами
    if not os.path.exists(_search_pth) or not os.path.isfile(_search_pth):
        # если такого файла нет то мы и не могли его редактировать
        raise FileNotFoundError(_search_pth)

    # теперь проверим вдруг администратор портала редактировал исходный файл
    # значит он должен сохраниться в другом месте
    _edit_pth = get_save_meta_path(mod_name)
    if os.path.exists(_edit_pth) and os.path.isdir(_edit_pth):
        _edit_pth = os.path.join(_edit_pth, relative)
        if os.path.exists(_edit_pth):
            _search_pth = _edit_pth
    return _search_pth


def get_meta_path_by_path(_pth):
    return ''


def get_logs_path():
    """
    Функция возвращает полный путь к директории логов приложения
    :return: полный путь
    """
    import os.path
    pth = ''
    _data_pth = get_app_data_path()
    pth += os.path.join(_data_pth, 'logs')
    return pth


def tsc_query(_q, _params = {}):
    '''
    Метод принимает на основной параметр _q, который является, либо кодом запроса
    в формате <module>.<file>.<template>, либо текстовым SPARQL запросом. В случае кода запроса есть дополнительный параметр param,
    переменные для подстановки в запрос.
    Если select запрос - метод вернет объект типа Python.List
    Если construct запрос - метод вернет объект типа Rdflib.Graph
    В случае, если в результате выполнения запроса обнаружена ошибка метод вернет строку с пояснением:
    - нет подключения к триплстору: Request error: StoreDriverBlazegraph._post_req say: Cant not send post request!
    - ошибка в sparqt файле: Request error: the JSON object must be str, bytes or bytearray, not bool

    :param _q: <module>.<file>.<template>
    :param _params: dict - {VARNAME : VALUE}
    :return: list or string or rdflib.Graph
    '''
    import re
    from app.query_mgt.query import Query
    result = ""
    query_instance = Query()
    if re.findall(r'^\w+\.\w+\.\w+$', _q):
        result = query_instance.queryByCode(_q, _params)
    else:
        result = query_instance.query(_q)
    return result


def compile_query(_q, _params={}):
    '''
    :param _q: <module>.<file>.<template>
    :param _params: dict - {VARNAME : VALUE}
    :return: query_TXT
    '''
    from app.query_mgt.query import Query
    return Query().compileQuery(_q, _params)


def compile_query_result(result):
    '''
    :param result: sparql query
    :return: compiled sparql query
    '''
    from app.query_mgt.query import Query
    return Query().compileQueryResult(result)


def get_module_sparqt_dir(module):
    '''
    :param module: module name
    :return: path to sparqt dir in module
    '''
    import os.path
    from rdflib import Namespace
    g = get_mod_decscription(module)
    OSPLM = Namespace(get_portal_onto_uri() + "#")
    path_sparqt = ""
    for path in g.objects(predicate=OSPLM.hasPathForSPARQLquery):
        path_sparqt = path
        break

    return os.path.join(get_mod_path(module), path_sparqt)


def get_portal_onto_uri():
    """
    Функция фозвращает базовый урл для онтологии описывающий портал (не данные портала)
    :return: URI онтологии портала
    """
    base_uri = 'http://splm.portal.web/osplm' # URL базовой онтологии портала
    return base_uri


def cook_graph_name(base):
    """
    Функция возвращает URI для графа base
    :param base: имя графа
    :return: полное имя графа
    """
    base_uri = get_portal_onto_uri() # URL базовой онтологии портала
    uri = base_uri + '/graph'
    _name = uri + '#' + base
    return _name


def get_auth_decorator():
    """
    Функция возвращает функцию декоратор для проверки авторизации пользователя перед выполнением
    функции, обрабатывающей запрос
    :return: функция-декоратор
    """
    from app.admin_mgt.decorators import requires_auth
    return requires_auth


def check_in_registred_urls(check):
    """
    Функция отвечает на вопрос - существует ли обработчик для url, указанного параметром check
    :param check: string - url наличие обработчика которого требуется проверить
    :return: True - если обработчик есть, иначе False
    """
    from app import app
    all_urls = [str(_u) for _u in app.url_map.iter_rules()]
    return check in all_urls


def get_portal_labels(label_code):
    """
    Функция возвращает надписи для портала по коду
    :param label_code: код надписи
    :return: надпись или пустая строка
    """
    _cfg = get_app_config()
    name = ''
    try:
        name = _cfg.get('prj_labels.Info.' + label_code)
        # print(name)
    except Exception as ex:
        print('Не удалось получить название для кода {}!' . format(label_code))
    return name


def get_described_roles():
    lst = []
    mod_manager = get_mod_manager()
    lst = mod_manager.get_described_roles()
    return lst


def get_current_theme():
    """
    Функция выбирает текущую тему
    return Theme
    """
    from app import app
    from flask_themes2 import get_theme
    current_theme = get_app_config().get('main.Interface.Theme')
    if isinstance(current_theme, str):
        ident = current_theme
    else:
        ident = app.config.get('DEFAULT_THEME')
    return ident


def render_page(tmpl_name, **tmpl_vars):
    """
    Функция выполняющая рендер страницы с учетом тематизации
    return html
    """
    from flask_themes2 import render_theme_template, get_theme
    tmpl_name = correct_template_path(tmpl_name)
    _url_prefix = get_app_url_prefix()
    tmpl_vars['_APP_URL_PREFIX_'] = _url_prefix
    tmpl_vars['site_home_link'] = _url_prefix.rstrip('/') + '/' if _url_prefix else '/'
    return render_theme_template(get_theme(get_current_theme()), tmpl_name, **tmpl_vars)



def canExportReqs():
    """
    Функция проверяет возможность экспорта в xlsx для jqgrid
    return <int>
    """
    from flask import g
    if g.user and g.user.has_role(get_app_config().get('users.Roles.exportCReqsRole')):
        return 1
    return 0


def get_useDBGMode():
    """
    Функция получает значение для debug mode для jqgrid
    return <int>
    """
    from flask import g, session
    app_cfg = get_app_config()
    debug_key = app_cfg.get('main.Info.debugModeSesKey')

    if g.user:
        if g.user.has_role(app_cfg.get('users.Roles.debugRole')):
            return session.get(debug_key) if debug_key in session else 0

    return 0


def get_portal_version():
    _v = ''
    admin_api = get_mod_api('admin_mgt')
    _v = admin_api.get_portal_version()
    return _v

def correct_template_path(_tmpl):
    """
    Функция предназначена для коректировки пути шаблонов
    :param str _tmpl: относительный путь к html шаблону
    :return: скорректированный путь
    :rtype str:
    """
    from sys import platform
    from os import path
    if "win32" == platform:
        # так как
        # from flak_themes2/__init__.py return render_template("_themes/%s/%s" % (theme, template_name), **context)
        # преобразуем путь к соответствующему шаблону
        _tmpl = _tmpl.replace(path.sep, path.altsep)
    return _tmpl


def get_event_manager():
    """
    Функция возвращает экзмпляр класса EventManager, который существует в единственном экземпляре
    :return: instance EventManager
    """
    from app.utilites.event_manager import EventManager
    return EventManager()


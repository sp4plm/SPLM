# -*- coding: utf-8 -*-
import os.path
import re

if 'app' not in globals():
    from app import app

# вспомогательная утиллита для работы с файлами и не только
from app.utilites.code_helper import CodeHelper
from app.utilites.some_config import SomeConfig
from app.utilites.portal_navi import PortalNavi
from app.query_mgt.query import Query
from app.module_mgt.manager import Manager

from rdflib import Namespace


def get_config_util():
    """
    Функция возвращает класс для унифицированной работы с файлами конфигов (ini)
    :return: класс SomeConfig
    """
    return SomeConfig


def get_app_config():
    """
    Функция возвращает инструмент для получения данных о настройках приложения.
    :return: экземляр класса SomeConfig
    """
    admin_api = get_mod_api('admin_mgt')
    cfg = get_config_util()(admin_api.get_config_path())
    return cfg


def get_mod_manager():
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
    app_config = get_app_config()
    return 'base_bootstrap.html'


def get_app_root_dir():
    """
    Функция возвращает путь к директории приложения
    :return: полный путь
    """
    return os.path.dirname(__file__)


def get_mod_path(mod_name):
    """
    Функция возвращает полный путь к директории модуля
    :param mod_name: имя модуля портала
    :return: полный путь
    """
    pth = ''
    pth += os.path.join(get_app_root_dir(), mod_name)
    return pth


def tsc_query(_q, _params = {}):
    '''
    Метод принимает на основной параметр _q, который является, либо кодом запроса
    в формате <module>.<file>.<template>, либо текстовым SPARQL запросом. В случае кода запроса есть дополнительный параметр param,
    переменные для подстановки в запрос.
    :param _q: <module>.<file>.<template>
    :param _params: dict - {VARNAME : VALUE}
    :return: result
    '''
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
    return Query().compileQuery(_q, _params)


def compile_query_result(result):
    '''
    :param result: sparql query
    :return: compiled sparql query
    '''
    return Query().compileQueryResult(result)




def get_module_sparqt_dir(module):
    '''
    :param module: module name
    :return: path to sparqt dir in module
    '''
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

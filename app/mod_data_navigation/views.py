# -*- coding: utf-8 -*-

import os
from flask import Blueprint, request, redirect, url_for
from rdflib import Graph
from app.app_api import tsc_query
from app import app_api
from .shacl import Shacl

onto_mod_api = app_api.get_mod_api('onto_mgt')
qry_mod_api = app_api.get_mod_api('query_mgt')

url_prefix='/datanav'
MOD_NAME = 'data_navigation'
mod = Blueprint(MOD_NAME, __name__, url_prefix='/',
                static_folder=os.path.join(os.path.dirname(__file__),'static'),
                static_url_path='datanav',
                template_folder=os.path.join(os.path.dirname(__file__),'templates'))

_auth_decorator = app_api.get_auth_decorator()

qry_mod_api.create_sparqt_manager(url_prefix + '/sparqt', mod)

def getParent(cur_class, argms, list_of_templates):

    if any(argms['prefix'] in sl for sl in onto_mod_api.get_prefixes()):

        class_name = onto_mod_api.get_parent(argms['prefix'],cur_class)

        if class_name != '' and class_name not in list_of_templates:
            new_class = getParent(class_name, argms, list_of_templates)
        else:
            new_class = class_name
    else:
        new_class = ''

    return new_class

@mod.route(url_prefix)
@_auth_decorator
def startPage():

    heading = 'Стартовая страница'
    message1 = 'Стандартная навигация'
    message2 = 'Альтернативная навигация по дереву онтологии с кореневого класса "Thing"'

    page_stat = {'pizza':['<http://www.co-ode.org/ontologies/pizza/pizza.owl#Pizza>',
                          '<img class="img-responsive" src="/static/files/images/Pizza.png" alt="Pizza">',
                          '<a href="datanav/Pizza?prefix=pizza">Пицца</a>'],
                 'topping':['<http://www.co-ode.org/ontologies/pizza/pizza.owl#PizzaTopping>',
                            '<img class="img-responsive" src="/static/files/images/PizzaTopping.png" alt="PizzaTopping">',
                            '<a href="datanav/PizzaTopping?prefix=pizza">Топпиг</a>'],
                 'base':['<http://www.co-ode.org/ontologies/pizza/pizza.owl#PizzaBase>',
                         '<img class="img-responsive" src="/static/files/images/PizzaBase.png" alt="PizzaBase">',
                         '<a href="datanav/PizzaBase?prefix=pizza">Основа для пицца</a>']}

    stat = {}
    for key, val in page_stat.items():
        q_inst = tsc_query('mod_data_navigation.index.count_instances',{'URI':val[0]})
        q_cls = tsc_query('mod_data_navigation.index.count_subclasses',{'URI':val[0]})
        if q_inst and q_cls:
            stat.update({key:{'inst':q_inst[0]['inst_qnt'], 'cls':q_cls[0]['cls_qnt'], 'img':val[1], 'href':val[2]}})
        else:
            stat.update({key: {'inst':q_inst, 'cls':q_cls}})

    return app_api.render_page(mod.name + "/index.html", heading=heading, stat=stat, message1=message1, message2=message2)

@mod.route(url_prefix + '/<class_object>')
@_auth_decorator
def uri_class(class_object):
    # cls = ''
    # new_class = ''
    list_of_templates = ['Thing']

    # Берем необходимые аргументы из http запроса
    argms = request.args.to_dict()
    argms['class'] = class_object

    # Если префикс онтологии не указан, то назначаем префикс по умолчанию "onto"
    if not 'prefix' in argms.keys():
        argms['prefix'] = 'onto'

    # Собираем все классы Питона, которые созданы для отображения классов онтологии из соответствующей папки
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__),'classes',argms['prefix'])):
        for _file in files:
            k = _file.rindex(".")
            if _file[k:] == ".py":
                list_of_templates.append(_file[:k])

    # Если у текущего класса онтологии нет шаблона, то ищем ближайший по иерархии родительский класс онтологии
    # у которого есть шаблон и переопределяем текущий класс на найденного родителя
    if class_object not in list_of_templates:
        class_with_tmpl = getParent(class_object, argms, list_of_templates)
    else:
        class_with_tmpl = class_object

    """ 
    Обрабатываем классы 
    согласно указанному префиксу
    """
    if argms['prefix'] == 'onto':  # ---------------------- ONTO ------------------------
        if class_with_tmpl == 'Document':
            from .classes.onto.Document import Document
            cls = Document(argms)
        # Добавляем сюда все варианты пренастроенных шаблонов коассов для префикса ONTO
        # elif _____:

        # Назначаем шаблон самого верхнего класса, который всегда должен быть
        elif class_with_tmpl == 'Thing':
            # Если есть прямое обращение к классу Thing с неправильным префиксом, то выдаем сообщение об ошибке
            if class_object == 'Thing':
                from .classes.onto.Blank import Blank
                cls = Blank(class_with_tmpl, 'NO class "%s" for the prefix "ONTO"' % argms['class'])
            else:
                from .classes.owl.Thing import Thing
                cls = Thing(argms)
        else:
            from .classes.onto.Blank import Blank
            cls = Blank(class_with_tmpl, 'NO class "%s" for the prefix "%s"' % (argms['class'], argms['prefix']))

    elif argms['prefix'] == 'pizza': # ---------------------- PIZZA ------------------------
        if class_with_tmpl == 'Pizza':
            from .classes.pizza.Pizza import Pizza
            cls = Pizza(argms)
        elif class_with_tmpl == 'PizzaTopping':
            from .classes.pizza.PizzaTopping import PizzaTopping
            cls = PizzaTopping(argms)
        elif class_with_tmpl == 'PizzaBase':
            from .classes.pizza.PizzaBase import PizzaBase
            cls = PizzaBase(argms)
        # Добавляем сюда все варианты пренастроенных шаблонов коассов для префикса ONTO
        # elif _____:

        elif class_with_tmpl == 'Thing':
            if class_object == 'Thing':
                from .classes.onto.Blank import Blank
                cls = Blank(class_with_tmpl, 'Нет класса "%s" в онтологии с префиксом "%s"' % (argms['class'], argms['prefix']))
            else:
                from .classes.owl.Thing import Thing
                cls = Thing(argms)
        else:
            from .classes.onto.Blank import Blank
            cls = Blank(class_with_tmpl, 'Нет класса "%s" в онтологии с префиксом "%s"' % (argms['class'], argms['prefix']))

    elif argms['prefix'] == 'owl': # ---------------------- OWL ------------------------
        if class_with_tmpl == 'Thing':
            from .classes.owl.Thing import Thing
            cls = Thing(argms)
        else:
            from .classes.onto.Blank import Blank
            cls = Blank(class_with_tmpl, 'Нет класса "%s" в онтологии с префиксом "OWL"' % argms['class'] )

    else: # ---------------------- ????????? ------------------------
        from .classes.onto.Blank import Blank
        cls = Blank(class_with_tmpl, 'Незарегистрированный префикс "%s"' % argms['prefix'] )

    return cls.getTemplate()



@mod.route(url_prefix + '/getver/<class_object>')
@_auth_decorator
def get_verif_result(class_object):
    html='<h4 style="color:#c22719">Результаты проверки выполнения требований:</h4>'

    # Берем необходимые аргументы из http запроса
    argms = request.args.to_dict()
    argms['class'] = class_object

    from .classes.pizza.Pizza import get_reqs_verification, FILE_REQS
    df, len_new_triples = get_reqs_verification(argms['prefix'],argms['class'], FILE_REQS)
    html += df.to_html(index=False)
    return html

@mod.route(url_prefix + '/rules/<class_object>')
@_auth_decorator
def get_rules_result(class_object):

    html='<h4 style="color:#c22719">Результаты выполнения правил:</h4>'

    # Берем необходимые аргументы из http запроса
    argms = request.args.to_dict()
    argms['class'] = class_object

    from .classes.pizza.Pizza import get_reqs_verification, FILE_RULES
    df, len_new_triples = get_reqs_verification(argms['prefix'],argms['class'], FILE_RULES)
    html += "<span>В результате выполнения правил добавлено %s записей в базу данных.</span>" % len_new_triples
    return html


@mod.route( url_prefix + '/shacl' )
@_auth_decorator
def shacl():
    '''
    Функция возвращает список файлов SHACL для последующего редактирования
    '''
    return app_api.render_page( '/data_navigation/files.html', files=Shacl().get_list_shacl() )


@mod.route( url_prefix + '/shacl/file/<file>', methods=["GET", "POST"] )
@mod.route( url_prefix + '/shacl/file/', methods=["GET", "POST"] )
@_auth_decorator
def shacl_file(file=''):
    if 'save' in request.form:
        if os.path.exists( Shacl().get_full_file_path( file ) ):
            try:
                g = Graph()
                result = g.parse( data=request.form['data'], format="turtle" )
                # согласно новой концепции сохранять редактируемый файл требуется в директорию общего конфига
                Shacl().edit_file( file, request.form['data'] )
            except Exception as e:
                print( e )
                pass

        else:
            pass
        return redirect( url_for( 'data_navigation.shacl', file=file ) )

    elif 'delete' in request.form:
        Shacl().delete_file( file )
        return redirect( url_for( 'data_navigation.shacl', file=file ) )

    else:
        data = Shacl().get_file( file )
        _can_remove = False
        _can_remove = Shacl().can_remove( file )
        return app_api.render_page( '/data_navigation/edit.html', file=file, data=data, can_delete=_can_remove )

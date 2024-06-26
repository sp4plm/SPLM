# -*- coding: utf-8 -*-
'''
Created on 4 sept. 2021 г.
@author: oleg st
'''

import pandas as pd
import numpy as np
import re, copy, os
from urllib.parse import quote
from hashlib import sha1
from rdflib import URIRef, Graph
from rdflib.plugins.sparql.results.jsonresults import JSONResult
from pyshacl import validate

from app.app_api import tsc_query
from app import app_api
from app.utilites.data_upload_manager import DataUploadManager

onto_mod_api = app_api.get_mod_api('onto_mgt')
from app.utilites.axiom_reader import getClassAxioms

MOD_PATH = app_api.get_mod_path( "mod_data_navigation" )

# with open(os.path.join( MOD_PATH, FILE ), 'r', encoding='utf-8') as f:
FILE_REQS = 'shacl/shacl_reqs.ttl'
FILE_RULES = 'shacl/shacl_rules.ttl'

def make_breadcrumbs(prefix, pref_unquote, cls):

    bc = []
    while cls != 'Food':
        if cls == '' or cls == 'Thing': # в онтологии могут быть несколько родительских классов и возможно не выполнение первого условия
            break

        query_paretn_lbl = tsc_query('mod_data_navigation.Pizza.class_lbl',
                                    {'URI': pref_unquote + cls })

        if not isinstance(query_paretn_lbl, str):
            df_prnt = pd.DataFrame(query_paretn_lbl)

            if len(df_prnt):
                cls_lbl = df_prnt.cls_lbl[0]
            else:
                cls_lbl = cls

            bc.insert(0, {'href': cls + '?' + 'prefix=' + prefix, 'label' : cls_lbl})
            cls = onto_mod_api.get_parent(prefix, cls)
        else:
            bc.insert(0,query_paretn_lbl)

    return bc

class Pizza:
    def __init__(self, argm):

        self.argm = argm
        self.parent = onto_mod_api.get_parent(argm['prefix'], argm['class'])

        self.pref_unquote = ''
        prefixes = onto_mod_api.get_prefixes()
        for p in prefixes:
            if p[0] == argm['prefix']:
                self.pref_unquote = p[1]

        query = tsc_query('mod_data_navigation.Pizza.one_instances',
                          {'URI': self.pref_unquote + self.argm['class']})

        if isinstance(query, str) or len(query) == 0:
            self.pref_4_data = ''
        else:
            self.pref_4_data = query[0]['inst'].split("#")[0] + "#"

    def __make_href__(self, cls='', prf='', uri='', lbl=''):
        if uri =='':
            uri_str = '<a href="{}?prefix={}">{}</a>'.format(cls,prf,lbl)
        else:
            uri_str = '<a href="{}?prefix={}&uri={}">{}</a>'.format(cls,prf,quote(uri),lbl)

        return uri_str

    def __get_axioms__(self):
        text = ""
        replaces = {"onto:hasPart": "состоит из: ",
                    "owl:someValuesFrom": " хотя бы 1 экземпляра класса ", "rdf:type - owl:Restriction":"",
                    "onto:": "", 'OWL:intersectionOf:':'пересечение множеств ', "owl:onProperty -":"",
                    "rdfs:subClassOf:":"", "OWL:subClassOf: ":"", "rdf:type - owl:Class":"",
                    "owl:unionOf":"объединяет: "}

        G = onto_mod_api.get_graph(self.argm['prefix'])
        AXIOMS = getClassAxioms(URIRef(self.pref_unquote + self.argm['class']), G, self.pref_unquote)

        if 'subClass' in AXIOMS.keys():
            text = "<p>Это объект класса {}</p>".format(self.parent)

            a = AXIOMS['subClass'].values()
            if a:
                a_str = ' '.join(a)
                a_str = a_str.replace("\n", "<br>").replace("(","").replace(")","")
                a_str = re.sub("|".join(replaces.keys()), lambda match: replaces[match.string[match.start():match.end()]], a_str)
                text += "<p>для которого выполняются все следующие условия:</p>" + a_str


        if 'equivalentClass' in AXIOMS.keys():
            ec = AXIOMS['equivalentClass'].values()
            if ec:
                ec_str = ' '.join(ec)
                ec_str = ec_str.replace("\n\n", "<br>")
                ec_str = re.sub("|".join(replaces.keys()), lambda match: replaces[match.string[match.start():match.end()]], ec_str)
                text += "<p>для которого выполняются все следующие условия:</p>" + ec_str

        text = text.replace("<br><br>", "<br>").replace("<br><br>", "<br>")
        return text


    def getTemplate(self):
        '''
        Возвращает шаблон HTML страницы, сформированный в соответствии с полученными в URL аргументами
        '''

        subclasses = ''
        instances = ''
        page_path = make_breadcrumbs(self.argm['prefix'], self.pref_unquote, self.argm['class'])
        d = {}

        query_class_lbl = tsc_query('mod_data_navigation.Pizza.class_lbl',
                     {'URI': self.pref_unquote + self.argm['class']})

        if not isinstance(query_class_lbl, str):
            df_cls = pd.DataFrame(query_class_lbl)
        else:
            df_cls =pd.DataFrame()

        if len(df_cls):
            class_lbl = df_cls.cls_lbl[0]
        else:
            class_lbl = self.argm['class']

        # Если есть аргумент URI, то значит показываем страничку "Экземпляра класса"
        if 'uri' in self.argm.keys():
            query_inst = tsc_query('mod_data_navigation.Pizza.instance',
                                   {'PREF': self.pref_unquote, 'URI': self.argm['uri']})

            if not isinstance(query_inst, str):
                df = pd.DataFrame(query_inst)
            else:
                df = pd.DataFrame()

            # INSERT PICTURE ----------------------------------------------------
            myHash = sha1(self.argm['uri'].encode('utf-8')).hexdigest()
            gravatar_url = "http://www.gravatar.com/avatar/{}?d=identicon&s=300".format(myHash)
            Avatar = '<img class="img-responsive" style="margin: 0 auto;" src=\"' + gravatar_url + '\" width=\"400\" height=\"400\" alt=\"pizza\">'

            if not df.empty:
                for ind, row in df.iterrows():
                    if not row.inst_lbl in d:
                        d.update({row.inst_lbl:{} })
                        d[row.inst_lbl].update({'Topping':{} })
                    if row.att_cls_lbl == 'Topping':
                        row_topp = row.att_val.split('&&')
                        d[row.inst_lbl]['Topping'].update({row_topp[2]: self.__make_href__(cls=row_topp[0].split('#')[1],
                                                                                    prf='pizza', uri=row_topp[1],
                                                                                     lbl=row_topp[2])})
                    elif row.att_cls_lbl == 'Base':
                        row_base = row.att_val.split('&&')
                        d[row.inst_lbl].update({row.att_cls_lbl: self.__make_href__(cls=row_base[0].split('#')[1],
                                                                                    prf='pizza', uri=row_base[1],
                                                                                    lbl=row_base[2])})
                    else:
                        d[row.inst_lbl].update({row.att_cls_lbl : row.att_val})


                d[row.inst_lbl].update({'Avatar':Avatar})

                templ = app_api.render_page("data_navigation/Pizza_inst.html", title="Пицца",
                                class_name=self.__make_href__(cls=self.argm['class'], prf=self.argm['prefix'], uri='',lbl=class_lbl),
                                instance=d,
                                argm=self.argm.items(),
                                page_path=page_path)

            else:
                templ = app_api.render_page("data_navigation/Pizza_inst.html", title="Пицца",
                                class_name=self.__make_href__(cls=self.argm['class'], prf=self.argm['prefix'], uri='', lbl=class_lbl),
                                instance={"No data":{"Comment":"about this instance.","Topping": {"None":"None"},"Avatar":""}},
                                argm=self.argm.items(),
                                page_path=page_path)

        # В остальных случаях показываем страничку со "Списком экземпляров класса и его подклассами"
        else:
            # ------------- subclasses --------------------------
            query_subclass = tsc_query('mod_data_navigation.Pizza.list_of_subclasses',
                                       {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})

            if not isinstance(query_subclass, str):
                df = pd.DataFrame(query_subclass)
            else:
                df = pd.DataFrame()

            if not df.empty:
                df.cls = '<a href="' + df.cls.str.replace(self.pref_unquote,'', regex=True) + \
                         '?prefix=' + self.argm['prefix'] + '">' + df.cls_lbl + '</a>'
                df.drop('cls_lbl', axis=1, inplace=True)
                df.columns = ['Наименование','Доступно для заказа']

                subclasses = df.to_html(escape=False, index=False)

            # ------------- list of instances --------------------------
            query_list_inst = tsc_query('mod_data_navigation.Pizza.list_of_instances',
                                        {'URI': "<" + self.pref_unquote + self.argm['class'] + ">"})

            if not isinstance(query_list_inst, str):
                df2 = pd.DataFrame(query_list_inst)
            else:
                df2 = pd.DataFrame()

            if not df2.empty:
                # Если у экземпляра нет лейбла, то вместо него вставляем часть URI
                df2.inst_lbl.replace('', np.nan, inplace=True)
                df2.inst_lbl.fillna(value=df2.inst.str.replace(self.pref_unquote, '', regex=True), inplace=True)

                df2.insert(loc=2, column='Avatar', value="")
                for ind, row in df2.iterrows():
                    myHash = sha1(row.inst.encode('utf-8')).hexdigest()
                    gravatar_url = "http://www.gravatar.com/avatar/{}?d=identicon&s=50".format(myHash)
                    df2.iloc[ind]['Avatar'] = '<img class="img-responsive" src=\"' + gravatar_url + '\" width=\"40\" height=\"40\" alt=\"pizza\">'

                df2.inst = '<a href="' + self.argm['class']  + '?prefix=' + self.argm['prefix'] + '&uri=' + \
                           df2.inst.str.replace(self.pref_4_data, quote(self.pref_4_data), regex=True) + '">' + df2.inst_lbl + '</a>'
                df2.drop('inst_lbl', axis=1, inplace=True)
                df2.columns = ['Наименование', 'Картинка']

                instances = df2.to_html(escape=False, index=False)

            # Проверяем наличие требований к классу
            req = get_requirements_and_rules(self.pref_unquote, self.argm['class'], FILE_REQS)
            if not req.empty:
                requirements = req.to_html(index=False)
            else:
                requirements = ""

            # Проверяем наличие правил логических выводов
            rule = get_requirements_and_rules(self.pref_unquote, self.argm['class'], FILE_RULES)
            if not req.empty:
                rules = rule.to_html(index=False)
            else:
                rules = ""

            definition = self.__get_axioms__()

            page_path = make_breadcrumbs(self.argm['prefix'], self.pref_unquote, self.argm['class'])

            templ = app_api.render_page("data_navigation/Pizza.html", title="Пицца", class_name=class_lbl,
                        sidebar1 = '<a href="{}?prefix={}&uri={}">{}</a>'.format('American',self.argm['prefix'],quote('http://www.co-ode.org/ontologies/pizza/pizza.owl#NamedIndividual_1'),'Американо'),
                        sidebar2 = '<a href="{}?prefix={}&uri={}">{}</a>'.format('FruttiDiMare',self.argm['prefix'],quote('http://www.co-ode.org/ontologies/pizza/pizza.owl#FruttiDiMare_1'),'Frutti DiMare'),
                        sidebar3 = '<a href="{}?prefix={}&uri={}">{}</a>'.format('Soho',self.argm['prefix'],quote('http://www.co-ode.org/ontologies/pizza/pizza.owl#NamedIndividual_9'),'Пицца Сохо 3'),
                        sidebar4 = '<a href="{}?prefix={}&uri={}">{}</a>'.format('Mushroom',self.argm['prefix'],quote('http://www.co-ode.org/ontologies/pizza/pizza.owl#NamedIndividual_3'),'Грибная пицца 1'),
                        definition = definition,
                        requirements = requirements,
                        rules = rules,
                        subclasses=subclasses,
                        instances=instances,
                        page_path=page_path)

        return templ


def get_requirements_and_rules(pref, cls, choiced_file):
    # choice can be 'req' or 'rule'

    reqs = pd.DataFrame()

    with open( os.path.join( MOD_PATH, choiced_file ), 'r', encoding='utf-8' ) as f:
        G = Graph()
        G.parse( f )
        query_str = """prefix sh: <http://www.w3.org/ns/shacl#>
                       prefix pz: <%s> 
                    select distinct ?code ?text {
                    ?sh a sh:NodeShape .
                    ?sh sh:targetClass <%s> .
                    ?sh sh:property|sh:rule ?pr .
                    ?pr sh:name ?code .
                    ?pr sh:description ?text .} order by ?code
                    """ % (pref, pref + cls)

        reqs = pd.DataFrame(G.query(query_str))

    if not reqs.empty:
        reqs.columns = ['Код', 'Текст требования']
    else:
        reqs = pd.DataFrame()

    return reqs


def get_reqs_verification(prefix, ontoclass, choiced_file):
    print(ontoclass)
    pref_unquote = ''
    prefixes = onto_mod_api.get_prefixes()
    for p in prefixes:
        if p[0] == prefix:
            pref_unquote = p[1]


    # Выбираем из всех данных только те, которые имеют отношение к текущему классу
    data = tsc_query('mod_data_navigation.Pizza.get_subgraph',
                      {'URI': pref_unquote + ontoclass})

    with open( os.path.join( MOD_PATH, choiced_file ), 'r', encoding='utf-8' ) as file:
        shacl = Graph()
        shacl.parse( file )

    if isinstance(data, Graph) and len(data) > 0:

        data_graph = copy.deepcopy( data )
        G = onto_mod_api.get_graph(prefix)

        r = validate(data,
                     shacl_graph=shacl,
                     ont_graph=G,
                     inference='none',
                     abort_on_first=False,
                     allow_warnings=False,
                     meta_shacl=False,
                     advanced=True,
                     js=False,
                     inplace=True,
                     debug=True)

        conforms, results_graph, results_text = r

        if not conforms:
            qry_validat = """prefix sh: <http://www.w3.org/ns/shacl#>
                                SELECT ?code ?text ?conf ?message ?inst ?val {{ 
                                    ?rslt a sh:ValidationResult .
                                    ?rslt sh:resultSeverity ?cmf .
                                    BIND(STRAFTER(STR(?cmf),'#') as ?conf) .
                                    ?rslt sh:focusNode ?inst .
                                    ?rslt sh:resultMessage ?message .                                    
                                    ?rslt sh:sourceShape ?shape .
                                    ?shape sh:name ?code .
                                    ?shape sh:description ?text . 
                                Optional { ?rslt sh:value ?val . }
                                            } union {
                                    ?rslt a sh:ValidationResult .
                                    ?rslt sh:resultSeverity ?cmf .
                                   BIND(STRAFTER(STR(?cmf),'#') as ?conf) .
                                   ?rslt sh:focusNode ?inst .
                                   Optional {?rslt sh:resultMessage ?message .}
                                   ?rslt sh:sourceConstraint ?shape .
                                   ?shape sh:name ?code .
                                   ?shape sh:description ?text . 
                                 Optional { ?rslt sh:value ?val . }
                                       }} order by ?code"""

            val = pd.DataFrame(results_graph.query(qry_validat))

            if len( val.columns ) == 6:
                val.columns = ['Код', 'Текст требования', 'Выполнено', 'Обоснование', 'Объект', 'Значение']
                val['Объект'] = val['Объект'].str.replace(pref_unquote, '', regex=True)
                val['Выполнено'] = val['Выполнено'].str.replace('false', 'Нет')
        else:
            val = pd.DataFrame([['Нарушений требований не выявлено, либо требования для данного класса отсутствуют']], columns=['Результат'])

        new_triples = data - data_graph - G          # Вычисляет только добавленные в SHACL триплеты

        if len(new_triples) > 0:
            new_triples_f = os.path.join( MOD_PATH, 'new_triples.ttl')
            new_triples.serialize( new_triples_f, format='turtle' )
            data_uploader = DataUploadManager()

            cfg = app_api.get_app_config()
            if '1' == cfg.get('data_storages.Main.use_named_graphs') or \
                1 == cfg.get('data_storages.Main.use_named_graphs'):
                data_uploader.use_named_graph = True

            flag = data_uploader.upload_file(new_triples_f)

            if not flag:
                print('Can not upload new triplets')

            os.unlink(new_triples_f)  # delete files with SHACL resoning

    else:
        val = pd.DataFrame([['Не получен ответ от базы данных, обратитесь к администратору портала.']],
                           columns=['Ошибка'])

    return val, len(new_triples)
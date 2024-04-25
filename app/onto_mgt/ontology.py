# -*- coding: utf-8 -*-
import json
import os
import re
from rdflib import Graph, RDF, OWL, RDFS

from app.app_api import compile_query_result
from app.onto_mgt.files_managment import FilesManagment


class Ontology():
    _class_file = __file__
    _debug_name = 'Ontology'

    MOD_DATA_PATH = os.path.dirname(os.path.abspath(__file__))

    onto_file = ""
    dir_name = "ontos"

    ONTOS_PREFIXES = []

    ONTO_FILES_NSS = []
    NS_PREF_MAP = {}

    def __init__(self, onto_file = None):
        self.prefixes = {}
        self.onto_file = onto_file

    def getClassName(self, ontology_class):
        """ Возвращает имя класса без URI : ontology_class """
        try:
            ontology, ontology_class = ontology_class.split("#")
        except Exception as e:
            pass
            _ris = ontology_class.find('/')
            if -1 < _ris:
                _ris = ontology_class.rfind('/')  # уточняем последний справа
                ontology = ontology_class[:_ris]
                ontology_class = ontology_class[_ris+1:]

        return ontology_class

    def getBaseUri(self, file_name):
        """ Возвращает baseUri по файлу : fullname """
        _baseURI = ""
        mfile = open(file_name, "r", encoding="utf-8")
        for line in mfile.readlines():
            baseURI = re.findall(r'^\s*#\s*baseURI:\s*(.*)\s*$', line.strip())
            if baseURI:
                _baseURI = baseURI[0]
                if not _baseURI.endswith("#"):
                    _baseURI += "#"

        mfile.close()

        return _baseURI

    def getFileOntoByPrefix(self, prefix):
        """ Возвращает файл по префиксу : fullname """
        uri = ""
        prefs = self.getPrefixes()
        for pref in prefs:
            if pref[0] == prefix:
                uri = pref[1]

        ontos = self.getOntos()
        for onto in ontos:
            if onto[1] == uri:
                return onto[0]

        return ""

    def getOntoPrefix(self, onto_file):
        """ Возвращает префикс по файлу : prefix """
        baseURI = self.getBaseUri(onto_file)

        prefixes = {}
        mfile = open(onto_file, "r", encoding="utf-8")
        for line in mfile.readlines():
            prefix = re.findall(r'^\s*@prefix\s+(\w+):\s*<(.*)>\s*\.\s*$', line.strip())
            if prefix:
                prefixes[prefix[0][1]] = prefix[0][0]

        mfile.close()

        if baseURI in prefixes:
            return prefixes[baseURI]

        return ""

    def getPrefixes(self):
        """ Возвращает список префиксов всех онтологий [[prefix, baseUri], ...]"""
        self.ONTOS_PREFIXES = []
        ontos = self.getOntos()

        for onto in ontos:
            self.ONTOS_PREFIXES.append([self.getOntoPrefix(onto[0]), onto[1]])

        return self.ONTOS_PREFIXES

    def getAllPrefixes(self, onto = ""):
        """ Возвращает словарь префиксов онтологий {prefix : uri} """
        prefixes = {}
        if onto:
            onto_file = self.getFileOntoByPrefix(onto)
            mfile = open(onto_file, "r", encoding="utf-8")
            for line in mfile.readlines():
                prefix = re.findall(r'^\s*@prefix\s+(\w+):\s*<(.*)>\s*\.\s*$', line.strip())
                if prefix:
                    prefixes[prefix[0][0]] = prefix[0][1]

            mfile.close()

        else:
            prefs = self.getPrefixes()
            for pref in prefs:
                result = self.getAllPrefixes(pref[0])
                prefixes = {**prefixes, **result}

        return prefixes

    def can_upload_onto_file(self, some_file, ext_result=False):
        """
        Метод определяет можно ли загрузить новый файл some_file с онтологией.
        :param str some_file: путь к файлу с онтологией
        :param boolean ext_result: изменяет возвращаемый результат. Если равен True, то к выводу будет добавлен
        префикс который уже зарегистрирован с другим сохращением. Данные аргумент влияет на формат вывода при найденной
        коллизии.
        :return: результат проверки True - если в файле нет противоречия в префиксах, иначе False. Если передан параметр
        ext_result и равен True, то изменяется формат возвращаемого значения:
        (False, {'exist': _long_exs, 'checked': _long_new, 'short': _short}), где второй аргумент - словарь, содержащий
        URI префикса уже зарегистрированного (ключ - exist), URI префикса из загружаемого файла
         (ключ - checked) и короткое название префикса (ключ - short)
        :rtype boolean|tuple:
        """
        _flg = True  # по-умолчанию любой файл можно загрузить
        _exists_prefs = self.get_all_prefixes()
        _ext_result = None
        if _exists_prefs:
            # _prefs_d = self._list_prefs_2_dict(_exists_prefs)
            _file_prefs = self.get_prefixes_from_file(some_file)
            _short_old = [_i[0] for _i in _exists_prefs]
            _short_new = [_i[0] for _i in _file_prefs]
            # делаем ручное пересечение для исключения относительного префикса тк короткая форма - пустая строка
            _intersect = [_k for _k in _short_new if _k and _k in _short_old]
            if _intersect:
                """
                Теперь надо стравнить а у пересечений одинаковый полный URI
                Если полный URI разный, то выдаем ошибку что для одинакового короткого префикса указаны разный полные
                URI пространст имен
                """
                for _ins in _intersect:
                    _pref_idx = _short_old.index(_ins)
                    _exist_pref = _exists_prefs[_pref_idx]
                    _pref_idx = _short_new.index(_ins)
                    _load_pref = _file_prefs[_pref_idx]
                    if _exist_pref[1] != _load_pref[1]:
                        _flg = False
                        if ext_result:
                            _ext_result = (_flg, {'exist': _exist_pref[1], 'checked': _load_pref[1], 'short': _ins})
                        break  # выходим на первой ошибке

        return _flg if _ext_result is None else _ext_result

    def get_all_prefixes(self):
        """
        Метод возвращает все имеющиеся префиксы всех загруженных онтологий
        :return: спискок префиксов всех онтологий
        :rtype list:
        """
        _lst = []
        if not Ontology.ONTO_FILES_NSS:
            _d = {}
            df = FilesManagment()
            file_list = df.get_dir_source("ontos")
            for _fi in file_list:
                _t_lst = self.get_prefixes_from_file(_fi['fullname'])
                if _t_lst:
                    _t_d = self._list_prefs_2_dict(_t_lst)
                    for _lp in _t_d:
                        if _lp not in _d:
                            _d[_lp] = _t_d[_lp]
            if _d:
                _lst = list(_d.values())  # изменяем тип dict_values на list
                Ontology.ONTO_FILES_NSS = _lst
                Ontology.NS_PREF_MAP = _d
                # print('Ontology.NS_PREF_MAP -> ', Ontology.NS_PREF_MAP)
        else:
            _lst = Ontology.ONTO_FILES_NSS
            # print('reload?')
        return _lst

    @staticmethod
    def ns2pref(node_uri):
        """
        Метод заменяет пространство имен в node_uri до # или / на соответствующий префикс
        :param str node_uri: полный URI узла - хэшед(#) или слешед(/) URI
        :return: сокращенный вид URI узла, как пример - owl:Thing
        :rtype str:
        """
        _res = ''
        _sh = node_uri.find('#')
        _t = node_uri.split('/')
        _ns = ''
        _id = ''
        if -1 < _sh:
            _t1 = _t[-1].split('#')
            _t[-1] = _t1[0] + '#'
            _id = _t1[1]
        else:
            if not _t[-1]:
                _t.pop()
            _id = _t.pop()
        _ns = '/'.join(_t)
        if not Ontology.NS_PREF_MAP:
            _ns = ''
            _ns = _t[-2]
        else:
            _k = Ontology.NS_PREF_MAP.get(_ns, [])
            if not _k and not _ns.endswith('#'):
                """ значит какого пространства имен нет если не заканчивается на # то добавляем / и повторяем поиск """
                _ns += '/'
                _k = Ontology.NS_PREF_MAP.get(_ns, [])
            if not _k and _ns.endswith('#'):
                _k = ['', _ns]
            if not _k:
                _k = ['', '']
            _ns = _k[0]
        _res = _ns + ':' + _id
        return _res

    def _list_prefs_2_dict(self, _list_prefs):
        """
        Специализированный метод, который приводит список кортежей (префиксов) _list_prefs к словарю
        :param _list_prefs: список кортежей, где каждый кортеж состоит из двух элементов
        :return: словарь вида {long_name: (short_name, long_name)}
        :rtype dict:
        """
        _d = {}
        if _list_prefs:
            for _pref in _list_prefs:
                _d[str(_pref[1])] = _pref
        # RETURN dict{long_name: tuple(short_name, long_name)}
        return _d

    def get_prefixes_from_file(self, file_name):
        """
        Метод возвращает все префиксы указанные в файле file_name
        :param str file_name: путь к файлу
        :return: список префиксов из файла, где элемент списка tuple(short_name, long_name)
        :rtype list:
        """
        _lst = []
        if os.path.exists(file_name) and os.path.isfile(file_name):
            _g = Graph()
            file_format = 'ttl'  # возможно потребуется динамически менять
            file_format = None
            _g = _g.parse(file_name, format=file_format)
            _lst = self._get_prefixes_from_rdflib_graph(_g)
        return _lst

    def _get_prefixes_from_rdflib_graph(self, _g):
        _lst = []
        if _g and isinstance(_g, Graph):
            for _ns in _g.namespaces():
                _t = (str(_ns[0]), str(_ns[1]))
                _lst.append(_t)
        return _lst

    def _create_graph_by_file(self, file_name):
        _g = Graph()
        _file = None
        _file_api = FilesManagment()
        _file =  os.path.join(_file_api.get_dir_realpath(self.dir_name), file_name)
        if os.path.exists(_file) and os.path.isfile(_file):
            file_format = 'ttl'  # возможно потребуется динамически менять
            file_format = None
            _g = _g.parse(_file, format=file_format)
        return _g

    def normalize_classes_tree(self, _g):
        """
        Метод привотид структуру классов в графе к нормали. Нормалью будем считать, что все классы по наследованию
         связаны отношением rdfs:subClassOf, но owl:Thing никогда не выступает в таких отношениях в качестве субъекта,
         только объекта. Таким образом owl:Thing является корневым классом.
        :param rdflib.Graph _g:
        :return:
        :rtype rdflib.Graph:
        """
        _res = None
        _normal_root = OWL.Thing  # 'http://www.w3.org/2002/07/owl#Thing'
        _normal_leaf = OWL.Nothing  # 'http://www.w3.org/2002/07/owl#Nothing'
        # получаем корни графов
        _roots = self.get_graph_root_nodes(_g)
        _res = _g
        if 1 == len(_roots) and _normal_root == _roots[0]:
            pass  # так и должно быть - обратное условие огромное получается
        else:
            for _r in _roots:
                if _r != _normal_root:
                    _spo = (_r, RDFS.subClassOf, _normal_leaf)
                    _res.add(_spo)
            _spo = (_normal_leaf, RDFS.subClassOf, _normal_root)
            _res.add(_spo)
        return _res

    def get_ontodata_by_file(self, onto_file_name):
        """
        Метод возвращает структурированные (структура задается в данном методе) онтологии из файла onto_file_name
        :param str onto_file_name: имя файла с онтологией
        :return: вовзращает структурированные данные онтологии из файла
        :rtype dict:
        """
        data = {}
        data['Классы онтологии'] = {}
        data['Предикаты онтологии'] = {}

        _g = self._create_graph_by_file(onto_file_name)
        if _g:

            _def_root_class_node = 'owl:Thing'
            # надо проверить является ли _def_root_class_node корнем в онтологии
            if not self.node_is_graph_root(_g, _def_root_class_node):
                _def_root_class_node = self.get_graph_root_nodes(_g)[0]

            if not _def_root_class_node.startswith('<') and \
                not _def_root_class_node.endswith('>') and \
                _def_root_class_node.startswith('http'):
                _def_root_class_node = '<' + _def_root_class_node + '>'


            query_cls_string = """select ?term ?term_lbl ?term_cls ?term_comm ?term_dfnt {
                                                ?term rdfs:subClassOf* %s .
                                                ?term a ?term_cls .
                                                Optional {?term rdfs:label ?term_lbl . }
                                                Optional { ?term rdfs:comment ?term_comm . }
                                                }
                                           """ % (_def_root_class_node)

            data_cls = {}
            for row in _g.query(query_cls_string):
                data_cls[self.getClassName(str(row[0]))] = [["URI", str(row[0])], ["Наименование", str(row[1])],
                                                 ["Класс", str(row[2])], ["Комментарий", str(row[3])]]

            query_prd_string = """select ?term ?term_lbl ?term_cls ?term_dom ?term_rng ?term_comm
                                                {?term a owl:ObjectProperty .
                                                ?term a ?term_cls .
                                                Optional { ?term rdfs:label ?term_lbl . }
                                                Optional { ?term rdfs:domain ?term_dom . } 
                                                Optional { ?term rdfs:range ?term_rng . } 
                                                Optional { ?term rdfs:comment ?term_comm . }
                                                }
                                           """
            data_prd = {}
            for row in _g.query(query_prd_string):
                data_prd[self.getClassName(str(row[0]))] = [["URI", str(row[0])], ["Наименование", str(row[1])],
                                                 ["Класс", str(row[2])], ["Domain", str(row[3])],
                                                 ["Range", str(row[4])],
                                                 ["Комментарий", str(row[5])]]

            data['Классы онтологии'] = data_cls
            data['Предикаты онтологии'] = data_prd
        return data

    def prefixes_to_str(self, _prefs):
        _str = ''
        if _prefs:
            _lst = []
            for _i in _prefs:
                _s = _i[0] + ': ' + _i[1]
                _lst.append(_s)
            if _lst:
                _str = "\n".join(_lst)
        return _str

    def getClasses(self, onto):
        """ Возвращает словарь классов онтологии {uri : label} """
        classes = {}
        self.onto_file = self.getFileOntoByPrefix(onto)

        if self.onto_file:
            g = Graph()
            if os.path.exists(self.onto_file):
                g.parse(self.onto_file, format=None)

            for class_name in g.subjects(RDF.type, OWL.Class):
                for class_label in g.objects(class_name, RDFS.label):
                    classes[str(class_name)] = str(class_label)

        return classes

    def getOntos(self):
        """ Возвращает список списков [fullname, baseURI] """
        ontos = []

        df = FilesManagment()
        file_list = df.get_dir_source("ontos")
        for file in file_list:
            ontos.append([file["fullname"], self.getBaseUri(file["fullname"])])
        return ontos

    def getParent(self, onto, class_name):
        """ Возвращает родителя класса parent """
        parent = ""

        onto_file = self.getFileOntoByPrefix(onto)
        graph = Graph()
        if os.path.exists(onto_file):
            graph = graph.parse(onto_file, format=None)


        QUERY = "SELECT ?parent WHERE { %s:%s rdfs:subClassOf ?parent . filter (isIRI(?parent)) }" % (onto, class_name)
        parent_result = []
        try:
            parent_result = compile_query_result( json.loads( graph.query(QUERY).serialize(format="json").decode("utf-8") )  )
        except:
            pass

        if parent_result:
            parent = self.getClassName(parent_result[0]["parent"])

        return parent

    def get_graph_root_nodes(self, _graph):
        _roots = []
        from networkx import DiGraph
        if isinstance(_graph, DiGraph):
            for n in _graph:
                _predecessors = []
                try:
                    _ti = _graph.predecessors(n)
                    for _i in _ti:
                        _predecessors.append(_i)
                except Exception as ex:
                    pass
                if not _predecessors:
                    _roots.append(n)
                else:
                    pass
                    # print('__get_graph_root_nodes -> _predecessors', _predecessors)
        if isinstance(_graph, Graph):
            _q = """
                SELECT DISTINCT ?s WHERE {
                  ?sc rdfs:subClassOf ?s .
                  FILTER NOT EXISTS { ?s rdfs:subClassOf ?o . }
                  FILTER isIRI(?s)
                }
            """
            try:
                _qr = _graph.query(_q)
                for _ri in _qr:
                    _roots.append(_ri[0])
            except Exception as ex:
                pass
        return _roots

    def node_is_graph_root(self, _graph, _node):
        _flg = False
        if _node.startswith('<') and \
                _node.endswith('>'):
            _node = _node[1:-1]
        if not _node.startswith('http') and -1 < _node.find(':'):
            # получили краткую форму
            _prefs = self._get_prefixes_from_rdflib_graph(_graph)
            for _ns in _prefs:
                if _node.startswith(_ns[0]):
                    _t = _node.split(':')
                    _node = _ns[1] + _t[1]
                    break

        _roots = self.get_graph_root_nodes(_graph)
        if _roots:
           _flg = _node in _roots
        return _flg

    def getGraph(self, onto):
        """ Возвращает объект rdflib.graph онтологии по префиксу """
        onto_file = self.getFileOntoByPrefix(onto)
        graph = Graph()
        if os.path.exists(onto_file):
            graph = graph.parse(onto_file, format=None)

        return graph

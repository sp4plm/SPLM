# -*- coding: utf-8 -*-
import json
import os
from time import time, strftime, localtime

from app.utilites.code_helper import CodeHelper
from .data_manager import DataManager


class DataPublisher(DataManager):
    _class_file = __file__
    _debug_name = 'DataPublisher'

    def __init__(self):
        super().__init__()
        self._use_named_graph = False
        self._timer_file = ''
        self._success_trigger = None
        self._fail_trigger = None
        self._log_func = None
        self._on_ts = {}
        self._on_files = {}

    def set_success_trigger(self, trigger):
        """"""
        if callable(trigger):
            self._success_trigger = trigger

    def set_fail_trigger(self, trigger):
        """"""
        if callable(trigger):
            self._fail_trigger = trigger

    def set_log_func(self, trigger):
        """"""
        if callable(trigger):
            self._log_func = trigger

    def to_log(self, msg):
        if callable(self._log_func):
            self._log_func(self._debug_name + ': {}' . format(msg))
        #print(msg)

    def update_publish_list(self, file_path, is_deleted=False):
        flg = False
        if os.path.exists(file_path):
            file_key = ''
            file_key = CodeHelper.str_to_hash(file_path)
            if file_key not in self._on_files:
                self._on_files[file_key] = {'name': file_path, 'deleted': is_deleted}
                flg = True
        return flg

    def publish(self):
        """ publish file process """
        answer = {'total': 0, 'success': 0, 'fails': [], 'errors': []}
        if not self._on_files:
            self.to_log('No data for publishing')

        # делаем две ветки с именными графами и без
        if self._use_named_graph:
            """"""
            answer = self._publish_with_named_graphs()
        else:
            """"""
            answer = self._publish_simple()
        self.to_log('End loop over catched files')
        # теперь надо вызвать хранимые процедуры для обработки новой информации
        self.to_log('Try execute triggers after uploading files')
        self.post_publish_trigger()
        self.to_log('Execute triggers after uploading files is DONE')
        # теперь изменим время публикации данных
        self.to_log('Try set new publish time')
        self._set_last_publish_time()
        self.to_log('Set new publish time Done')
        return answer

    def _publish_with_named_graphs(self):
        self.to_log('Start upload files to TS with named graphs')
        """"""
        answer = {'total': 0, 'success': 0, 'fails': [], 'errors': []}
        # получим все именный графы с порталаъ
        self._on_ts = self.get_graph_list()
        # определим список именных графов с TS которые требуется удалить
        graphs_2_delete = self._get_namedgraphs_to_delete(self._on_ts)
        if graphs_2_delete:
            self.to_log('Catch graphs to remove from TS')
            for graph in graphs_2_delete:
                self.to_log('Try remove graph {}' .format(graph))
                try:
                    """"""
                    result = self._clear_graph(graph)
                    self.to_log('Remove graph is done. Result: {}' .format(result))
                except Exception as ex:
                    """"""
                    self.to_log('Exception on remove graph request. Error: {}' .format(ex))
                    self.to_log(str(ex.args))
                    self.to_log('graph name -> "{}"' . format(graph))
        # теперь собственно произведем загрузку файлов
        # надо определить какие файлы надо грузить
        self._clear_existed_graphs_from_files()
        stat = self._publish_files()
        for k in stat:
            answer[k] = stat[k]
        return answer

    def _clear_existed_graphs_from_files(self):
        self.to_log('Try remove from files item that allready exists on TS')
        if self._on_files and self._on_ts:
            new_files = {}
            self.to_log('Exists file list and graph list')
            for file_key in self._on_files:
                file_path = self._on_files[file_key]['name']
                file_name = file_path.split('/')[-1]
                self.to_log('Operate with file: {}'.format(file_name))
                graph_name = self.cook_graph_name(file_name)
                self.to_log('Cooked graph name: {}'.format(graph_name))
                # надо убрать угловые скобки с начала и с конца  < >
                graph_name = graph_name.lstrip('<').rstrip('>')
                if graph_name not in self._on_ts or self._on_files[file_key]['deleted']:
                    self.to_log('Find not existed data or data for remove from TS. Removed flag: {}' . format(self._on_files[file_key]['deleted']))
                    new_files[file_key] = self._on_files[file_key]
            self._on_files = new_files

    def _publish_simple(self):
        self.to_log('Start simple upload files to TS(without named graphs)')
        """"""
        answer = {'total': 0, 'success': 0, 'fails': [], 'errors': []}
        # сперва надо очистить хранилище
        self.to_log('Try clear storage')
        self._clear_storage()
        self.to_log('Clear storage done!')
        self.to_log('Catch files to operate')
        answer['total'] = len(self._on_files)
        self.to_log('Start loop over catched files')
        stat = self._publish_files()
        for k in stat:
            answer[k] = stat[k]
        return answer

    def _publish_files(self):
        stat = {'success': 0, 'fails': 0, 'errors': []}
        if self._on_files:
            for file_key in self._on_files:
                file_path = self._on_files[file_key]['name']
                try:
                    flg = self._publish_file(self._on_files[file_key])
                    if flg:
                        stat['success'] += 1
                    else:
                        stat['fails'].append(file_path)
                except Exception as ex:
                    """ """
                    stat['errors'].append(file_path)
        return stat

    def _publish_file(self, file_info):
        flg = False
        file_path = file_info['name']
        file_name = file_path.split('/')[-1]
        try:
            self.to_log('Try operate with file: ' + file_path)
            if self._use_named_graph and file_info['deleted']:
                """"""
                self.to_log('Result file marked as DELETED')
                graph_name = self.cook_graph_name(file_name)
                result = self._clear_graph(graph_name)
                # print('remove graf result', graph_name, ':', result)
                self.to_log('remove graf result' + graph_name + ':' + str(result))
                if result:
                    """ теперь удалим сам файл """
                    os.unlink(file_path)
                    old = self._meta.get_current_dir()
                    self._meta.set_current_dir('res')
                    self._meta.sync_description()
                    self._meta.set_current_dir(old)
                    flg = True
                    # print('remove graf result', graph_name, ':', result)
                    self.to_log('remove result file' + file_info['name'] + ' for ' + graph_name)
            else:
                self.to_log('Try upload file ' + file_info['name'])
                flg = self._publish_file_to_storage(file_path)
                self.to_log('Upload file result - {}'.format(flg))

            if flg:
                if callable(self._success_trigger):
                    self._success_trigger(file_path)
            else:
                if callable(self._fail_trigger):
                    self._fail_trigger('File not uploaded!', file_path)
        except Exception as ex:
            """ """
            flg = False
            if callable(self._fail_trigger):
                self._fail_trigger('Except: ' + ex, file_path)
            self.to_log('Operate with file {} FAIL with Exception:- {}!'.format(file_path, ex))
        return flg

    def post_publish_trigger(self):
        if not self._on_files:
            self.to_log('DataPublisher.post_publish_trigger: No data for operation in TS - no needs for triggers')
            return
        """ """
        if self._use_named_graph:
            # удаляем флаг последней версии у требований
            self.to_log('Try execute "Rem Req last version" trigger')
            flg = self._rem_req_last_version()
            self.to_log('Execute "Rem Req last version" trigger DONE. Result: ' + str(flg))
            # удаляем флаг последней версии у документов
            self.to_log('Try execute "Rem Doc last version" trigger')
            flg = self._set_doc_last_version()
            self.to_log('Execute "Rem Doc last version" trigger DONE. Result: ' + str(flg))
        # устанавливаем флаг последней версии требований ТЗ
        self.to_log('Try execute "Set TZ Req last version" trigger')
        flg = self._set_tz_req_last_version()
        self.to_log('Execute "Set TZ Req last version" trigger DONE. Result: ' + str(flg))
        # устанавливаем флаг последней версии требований НТД
        self.to_log('Try execute "Set NTD Req last version" trigger')
        flg = self._set_ntd_req_last_version()
        self.to_log('Execute "Set NTD Req last version" trigger DONE. Result: ' + str(flg))
        # устанавливаем последнюю версию документов
        self.to_log('Try execute "Set Doc last version" trigger')
        flg = self._set_doc_last_version()
        self.to_log('Execute "Set Doc last version" trigger DONE. Result: ' + str(flg))
        # устанавливаем флаг Доп к ТЗ на экземплярах класса ТЗ
        self.to_log('Try execute "Set Extend TZ last version" trigger')
        flg = self._set_extending_tzdoc()
        self.to_log('Execute "Set Extend TZ last version" trigger DONE. Result: ' + str(flg))
        # теперь надо вызвать специфичные действия для хранилища
        if self._app_data_manager is not None:
            try:
                self.to_log('Try execute spesial triggers for tiplestore')
                self._app_data_manager.call_after_modify_storage_triggers()
                self.to_log('Execute spesial triggers for tiplestore DONE')
            except Exception as ex:
                self.to_log('Execute spesial triggers for tiplestore FAIL with Exception: ' + str(ex))
                raise ex

    def _get_namedgraphs_to_delete(self, graphs):
        self.to_log('DataPublisher._get_namedgraphs_to_delete.arg - {}'. format(str(graphs)))
        to_delete = []
        if self._on_files:
            _exists = []
            for file_key in self._on_files:
                self.to_log('DataPublisher._get_namedgraphs_to_delete.file_info - {}'. format(str(self._on_files[file_key])))
                file_path = self._on_files[file_key]['name']
                graph_name = self.cook_graph_name(file_path.split('/')[-1])
                # надо убрать угловые скобки с начала и с конца  < >
                graph_name = graph_name.lstrip('<').rstrip('>')
                self.to_log('DataPublisher._get_namedgraphs_to_delete.graph_name - {}'. format(str(graph_name)))
                if graph_name in graphs:
                    _exists.append(graph_name)
            self.to_log('DataPublisher._get_namedgraphs_to_delete.graphs_exists - {}'. format(str(_exists)))
            to_delete = list(set(graphs) - set(_exists))
            # так как мы очищаем имя графа для сравнения то надо обратно вернуть
            to_delete = ['<' + graph_name + '>' for graph_name in to_delete ]
        self.to_log('DataPublisher._get_namedgraphs_to_delete.to_delete - {}'.format(str(to_delete)))
        return to_delete


    def get_last_publish_time(self, tmpl='%Y-%m-%d %H:%M:%S'):
        """ """
        _file = self._get_timer_file()
        time_from_file = 0
        with open(_file, 'r') as file_p:
            str_time = file_p.read()
            if str_time:
                time_from_file = float(str_time)
        _time = localtime(time_from_file)
        _time = strftime(tmpl, _time)
        return _time

    def _set_last_publish_time(self, _time=0):
        """ """
        _file = self._get_timer_file()
        if 0 == _time:
            _time = time()
        with open(_file, 'w') as file_p:
            file_p.write(str(_time))

    def set_backup_time_to_publish(self, _time):
        """ """
        self._set_last_publish_time(_time)

    def _get_timer_file(self):
        if '' == self._timer_file:
            self._timer_file = os.path.join(self.DATA_PATH, 'last_publish') # data_storages.Manage.publishTimeFile
        if not os.path.exists(self._timer_file):
            with open(self._timer_file, 'w') as file_p:
                file_p.write('')
        return self._timer_file

    def _publish_file_to_storage(self, file_path):
        """ """
        flg = False
        if '' != file_path:
            flg = self._upload_file2(file_path)
        return flg

    def _clear_graph(self, graph_name):
        """ clear named graph """
        return self._app_data_manager.clear_named_graph_data(graph_name)

    def _clear_storage(self):
        """ """
        return self._app_data_manager.clear_storage()

    def get_graph_list(self):
        """ """
        query = '''SELECT ?g WHERE { GRAPH ?g {} }'''
        result = self._exec_query(query)
        result_rows = []
        if result:
            result = json.loads(result)
            rows = []
            cols = []
            if 'head' in result:
                if 'vars' in result['head']:
                    cols = result['head']['vars']
            if 'results' in result:
                if 'bindings' in result['results']:
                    rows = result['results']['bindings']
            if cols and rows:
                for row in rows:
                    new_row = {}
                    for col in cols:
                        new_row[col] = row[col]['value']
                    result_rows.append(new_row)
            if result_rows:
                # оставляет имя файла
                # result_rows = [r[k].split('#')[1] for r in result_rows for k in r]
                # оставляет URI графа
                result_rows = [r[k] for r in result_rows for k in r]
        return result_rows

    def _rem_req_last_version(self):
        """ """
        query = '''prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                prefix onto: <http://proryv2020.ru/req_onto#>
                prefix xs: <http://www.w3.org/2001/XMLSchema#>

                delete { ?itemver ?p ?o . }
                where {?itemver onto:latestVersion ?o .
                       ?itemver ?p ?o .
                       ?itemver a onto:TextItemVersion .
                }'''
        return self._exec_query(query)

    def _rem_doc_last_version(self):
        """ """
        query = '''prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                prefix onto: <http://proryv2020.ru/req_onto#>
                prefix xs: <http://www.w3.org/2001/XMLSchema#>

                delete { ?docver ?p ?o }
                where {?docver onto:latestVersion ?o .
                       ?docver ?p ?o .
                       ?typ rdfs:subClassOf onto:Document .
                        ?doc a ?typ .
                        ?doc onto:hasVersion ?docver.
                }
                '''
        return self._exec_query(query)

    def _set_req_last_version(self):
        """ """
        query = '''prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix onto: <http://proryv2020.ru/req_onto#>
        prefix xs: <http://www.w3.org/2001/XMLSchema#>
        
        INSERT {?itemver onto:latestVersion xs:true .}
         WHERE {
         ?item onto:hasVersion ?itemver .
         ?itemver onto:value ?version .
         {
         select distinct ?item (max(?ver) as ?version) 
         where {
         ?typ rdfs:subClassOf onto:TextItem .
         ?item a ?typ .
         ?item onto:hasVersion ?itemver.
         ?itemver onto:value ?ver .
         } group by ?item 
         }
        }'''
        return self._exec_query(query)

    def _set_tz_req_last_version(self):
        """ """
        query = '''prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix onto: <http://proryv2020.ru/req_onto#>
        prefix xs: <http://www.w3.org/2001/XMLSchema#>
        
        INSERT {?itemver onto:latestVersion xs:true .}
        WHERE {
            ?item onto:hasVersion ?itemver .
            ?itemver onto:value ?version .
            {
                select distinct ?item (max(?ver) as ?version)
                where {
                ?typ rdfs:subClassOf onto:TextItem .
                ?item a ?typ .
                  FILTER NOT EXISTS {
                    ?item onto:hasAttribute ?att .
				            ?att a onto:Status .
            				?att onto:hasAttributeValue/rdfs:label ?val . filter (?val = "Удалено")
                          }
                ?item onto:isCreatedIn ?doc .
                ?doc a onto:TZ .
                ?item onto:hasVersion ?itemver.
                ?itemver onto:value ?ver .
                } group by ?item
            }
        }'''
        return self._exec_query(query)

    def _set_ntd_req_last_version(self):
        """ """
        query = '''prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix onto: <http://proryv2020.ru/req_onto#>
        prefix xs: <http://www.w3.org/2001/XMLSchema#>
        
        INSERT {?itemver onto:latestVersion xs:true .}
        WHERE {
            ?item onto:hasVersion ?itemver .
            ?itemver onto:value ?version .
            {
                select distinct ?item (max(?ver) as ?version)
                where {
                    ?typ rdfs:subClassOf onto:TextItem .
                    ?item a ?typ .
                    ?item onto:isCreatedIn ?doc .
                    ?doc a onto:RegulatoryDocument .
                    ?doc onto:hasAttribute ?att .
                    ?att a onto:Status .
                    ?att onto:hasAttributeValue/rdfs:label "Действует" .
                    ?item onto:hasVersion ?itemver.
                    ?itemver onto:value ?ver .
                } group by ?item
            }
        }'''
        return self._exec_query(query)

    def _set_doc_last_version(self):
        """ """
        query = '''prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        prefix onto: <http://proryv2020.ru/req_onto#>
        prefix xs: <http://www.w3.org/2001/XMLSchema#>
        
        INSERT {?docver onto:latestVersion xs:true . 
         xs:true rdfs:label "Правда" .}
         WHERE {
         ?doc onto:hasVersion ?docver .
         ?docver rdfs:label ?version .
         {
         select distinct ?doc (max(?ver) as ?version) 
         where {
         ?doc onto:hasVersion ?docver .
         ?docver rdfs:label ?ver .
         ?docver a onto:DocumentVersion .
         } group by ?doc 
         }
        }'''
        return self._exec_query(query)

    def _set_extending_tzdoc(self):
        """ """
        query = '''PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX onto: <http://proryv2020.ru/req_onto#>
                    Insert {?tz onto:hasSupplementaryAgreement ?dop . }
                    WHERE {
                    ?dop a onto:TZ .
                      ?dop rdfs:label ?dop_lbl . filter(!STRENDS(?dop_lbl, "0" ))
                      ?dop onto:hasAttribute ?att .
                      ?att a onto:DocumentationPlanHierarchy .
                      BIND (concat(substr(?dop_lbl, 1, strlen(?dop_lbl)-1 ), "0") as ?main )
                      ?tz rdfs:label ?main .
                    }'''
        return self._exec_query(query)

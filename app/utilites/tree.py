# -*- coding: utf-8 -*-
import os
import json
import networkx as nx
from flask import url_for, request, g
from flask_login import current_user

from app.app_api import tsc_query
from app.utilites.portal_navi import PortalNavi

import re
from app import app_api
from urllib.parse import unquote
LABELS = {}
HREFS = {}
SORTED = {}

QUERY_CODE = "mod_splm_nav.Topic.themes"

PARENTS_FOR_QUERY = []
ENUMERATION = []


def get_data():
    data_navi = []
    if g.user:
        data_navi = PortalNavi.get_navi_map(g.user)

    data = []
    for item in data_navi:
        data.append(data_navi[item])


    # получение кодов на Порядок и Прорыв
    # получим именно /verification/documents, потому что последний в route
    PARENTS_FOR_QUERY_URLS = [url_for("splm_nav.tracing"), url_for("splm_nav.reportdocs"), url_for("splm_nav.verification")]
    ENUMERATION_URLS = [url_for("reports.analytics")]
    for item in data:
        if item['href'] in PARENTS_FOR_QUERY_URLS:
            if item['code'] not in PARENTS_FOR_QUERY:
                PARENTS_FOR_QUERY.append(item['code'])
            continue
        if item['href'] in ENUMERATION_URLS:
            if item['code'] not in ENUMERATION:
                ENUMERATION.append(item['code'])
            continue

    return data


def get_element_by_id(elem_id):
    for element in get_data():
        if element["id"] == elem_id:
            return element
    return {}


def get_parent_id(elem_id):
    for element in get_data():
        if element["id"] == elem_id:
            if element["parid"] == 0:
                return element["id"]
            else:
                return get_parent_id(element["parid"])

def get_id_by_href(href):
    for element in get_data():
        if element['href'] == href:
            return element["id"]
    return 0


# result = [parent, child]
def get_structure(parent_id):
    for element in get_data():
        LABELS[element['id']] = element['label']
        HREFS[element['id']] = element['href']
        SORTED[element['id']] = element['srtid']

    if parent_id in get_parents_for_query_ids():
        return get_query(parent_id)

    children = get_children(parent_id, get_data(), [])
    for query_id in children:
        if query_id[1] in get_parents_for_query_ids():
            children += get_query(query_id[1])
            continue

    return children


def get_children(parent_id, data, result):
    for element in data:
        if element['parid'] == parent_id:
            result.append([parent_id, element['id']])
            get_children(element['id'], data, result)

    return result


def get_attrs(tree, parent_id, parent_order = ""):
    current_order = 1

    srtid = {leaf['id'] : int(SORTED[leaf['id']]) for leaf in tree}
    srtid = {key : srtid[key] for key in sorted(srtid, key=srtid.get)}
    sorted_tree = []
    for key in srtid:
        for leaf in tree:
            if key == leaf['id']:
                sorted_tree.append(leaf)


    for leaf in sorted_tree:
        #########
        # добавляем префикс из GET параметра
        prefs = ""
        _get = request.args
        if _get:
            if 'prefix' in _get:
                prefs = "?prefix=" + _get['prefix']
        #########

        leaf['order'] = (parent_order + str(current_order) if parent_order else str(current_order)) + "."
        if parent_id in get_enumeration_ids():
            label = leaf['order'] + " " + LABELS[leaf['id']]
        else:
            label = LABELS[leaf['id']]

        href = HREFS[leaf['id']] + prefs
        leaf['name'] = '<a href="' + href + '">' + label + '</a>'
        if 'children' in leaf:
            leaf['children'] = get_attrs(leaf['children'], parent_id, leaf['order'])

        current_order += 1

    return sorted_tree


def create_tree(structure, node):
    G = nx.DiGraph()
    G.add_edges_from(structure)

    tree = nx.tree_data(G, node, {'children': 'children' , 'id': 'id'})

    return get_attrs(tree['children'], tree['id'])


def get_tree(href):
    parent_id = get_parent_id(get_id_by_href(href))
    try:
        parent_id = int(parent_id)
        return json.dumps(create_tree(get_structure(parent_id), parent_id), ensure_ascii=False)
    except Exception as e:
        return {}


def get_sidebar_navi(href):
    #  Вывод бокового меню без учета смежных с корнем (href) узлов

    id = get_id_by_href( href )
    item = get_element_by_id(id)

    # для структуры в виде дерева
    if PortalNavi.get_portal_navi(item['code'], g.user):
        return json.dumps(create_tree(get_structure(item['id']), item['id']), ensure_ascii=False)

    # для плоского списка
    else:
        lst = []
        for el in PortalNavi.get_brothers(item, g.user):
            _name = '<a href="' + el['href'] + '">' + el['label'] + '</a>'
            lst.append( {'id':el['id'], 'order':el['srtid'], 'name':_name} )
        return json.dumps(lst)


def create_tree_description(tree):
    html = ""
    for leaf in tree:
        html += '<h3 class="content-header">{name}</h3><div class="well">{desc}</div>'.format(name = leaf['name'], desc = "")
        if 'children' in leaf:
            html += '<div class="create_tree_description">' + create_tree_description(leaf['children']) + '</div>'

    return html


def create_bread_crumbs(href):
    bread_crumbs = []

    element = get_element_by_id(get_id_by_href(href))
    if element:
        bread_crumbs.append({"href" : element['href'], "label" : element['label'], "id" : element['id']})

        while element['parid'] != 0:
            element = get_element_by_id(element['parid'])
            bread_crumbs.insert(0, {"href" : element['href'], "label" : element['label'], "id" : element['id']})

    return bread_crumbs


def js_code_tree(tree):
    if tree:
        js = '''<script type="text/javascript">
        $(function() {$('#tree3').tree({
        autoEscape: false,
        autoOpen: true, 
        drapAndDrop:false,
        selectable:false,
        data: %s
        });
        });
        </script>''' % (tree)
    else:
        js = ''

    return js


def get_order(tree, elem_id):
    for leaf in tree:
        if leaf['id'] == elem_id:
            return leaf['order']

        if 'children' in leaf:
            get_order_children = get_order(leaf['children'], elem_id)
            if get_order_children:
                return get_order_children
        

def get_enumeration_ids():
    ENUMERATION_IDS = []
    for element in get_data():
        if element['code'] in ENUMERATION:
            ENUMERATION_IDS.append(element['id'])
    return ENUMERATION_IDS


def get_parents_for_query_ids():
    PARENTS_FOR_QUERY_IDS = []
    for element in get_data():
        if element['code'] in PARENTS_FOR_QUERY:
            PARENTS_FOR_QUERY_IDS.append(element['id'])
    return PARENTS_FOR_QUERY_IDS


def get_info_by_href(href):
    elem_id = get_id_by_href(href)
    parent_id = get_parent_id(elem_id)

    order = get_order(create_tree(get_structure(parent_id), parent_id), elem_id) if parent_id in get_enumeration_ids() else None

    for element in get_data():
        if element['id'] == elem_id:
            return element['label'], order

    return "", ""


def get_tree_path(elem_id, tree):
    for leaf in tree:
        if leaf['id'] == elem_id:
            return leaf['name']
        if 'children' in leaf:
            result = get_tree_path(elem_id, leaf['children'])
            if result:
                return leaf['name'] + '&nbsp;/&nbsp;' + result

    return ''


def build_theme_path(href, r_full_path):
    # выполняем unquote и экранируем символы
    if r_full_path.endswith("?"):
        r_full_path = r_full_path[:-1]
    r_full_path = unquote(r_full_path).replace("?", "\?")

    _tree = js_code_tree(get_tree(href))

    parent_id = get_parent_id(get_id_by_href(href))
    ELEM_ID = None
    for item in HREFS:
        if re.findall(rf'^{r_full_path}$', HREFS[item]):
            ELEM_ID = item

    return '<h3 class="content-header">{path}</h3>'.format(path = get_tree_path(ELEM_ID, create_tree(get_structure(parent_id), parent_id)))


def get_query(parent_id):
    try:
        # определяем дефолтный префикс
        if 'prefix' in request.args:
            pref = request.args['prefix']
        else:
            pref = "onto"

        # находим онтологию по префиксу
        prefixes =  app_api.get_mod_api('onto_mgt').get_prefixes()
        for p in prefixes:
            if p[0] == pref:
                ontology = p[1]

        themes = tsc_query(QUERY_CODE, {"PREF" : ontology})

        param_key = "TZTheme"
        
        result = []
        id_dict = {}
        PARENT_ID_HREF = HREFS[parent_id]
        
        sorted_id = 1

        ID = parent_id * 100
        LABELS[ID] = ""

        # Получаем корень
        for item in range(0, len(themes)):
            if not themes[item]['lev_2']:
                LABELS[ID] = themes[item]['topic']
                themes.pop(item)
                break

        HREFS[ID] = PARENT_ID_HREF + "?" + param_key + "=" + LABELS[ID]
        SORTED[ID] = sorted_id

        result.append([parent_id, ID])
        parent_id = ID

        for item in range(0, len(themes)):
            th_global_lbl = themes[item]['lev_2'] if themes[item]['lev_2'] else themes[item]['topic']
            if th_global_lbl not in list(id_dict.keys()):
                ID += 1
                id_dict[th_global_lbl] = ID
                
                result.append([parent_id, ID])
                LABELS[ID] = th_global_lbl
                # HREFS[ID] = PARENT_ID_HREF + "?obj=" + str(ID)
                HREFS[ID] = PARENT_ID_HREF + "?" + param_key + "=" + themes[item]['topic']
                SORTED[ID] = sorted_id


        for item in range(0, len(themes)):
            ID += 1
            if themes[item]['lev_3']:
                result.append([id_dict[themes[item]['lev_2']], ID])
                LABELS[ID] = themes[item]['lev_3']
                # HREFS[ID] = PARENT_ID_HREF + "?obj=" + str(ID)
                HREFS[ID] = PARENT_ID_HREF + "?" + param_key + "=" + themes[item]['topic']
                SORTED[ID] = sorted_id


        return result
    except Exception as e:
        print(e)
        return []

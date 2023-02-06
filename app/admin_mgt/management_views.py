# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса портала по URL - /portal
"""
import string
import json
import random

from crontab import CronSlices, CronTab

import sys

from flask import Blueprint, request, flash, g, session, redirect, url_for, current_app

from .admin_utils import os # import embeded pythons
from .admin_utils import app_api, CodeHelper # import application globals
from .admin_utils import AdminConf, AdminUtils # import current module libs
from .admin_navigation import AdminNavigation
from .configurator_utils import ConfiguratorUtils

from .decorators import requires_auth

from app import app
from .jobs import Jobs

from ..utilites.extend_processes import ExtendProcesses
from datetime import datetime




WEB_MOD_NAME = 'portal_management'
mod = Blueprint(WEB_MOD_NAME, __name__, url_prefix=AdminConf.MOD_WEB_ROOT+'/management',
                static_folder=AdminConf.get_web_static_path(),
                template_folder=AdminConf.get_web_tpl_path())


# { Navigation set_authorisation_method


@mod.route('/navigation', methods=['GET'], strict_slashes=False)
@requires_auth
def admin_navigation():
    """"""
    sect_code = 'PortalSettings'
    subitem_code = 'PortalManagementNavigation'
    tmpl_vars = {}
    # tmpl_vars['project_name'] = 'Semantic PLM'
    tmpl_vars['title'] = 'Административный интерфейс'
    tmpl_vars['page_title'] = 'Настройки навигации: '
    tmpl_vars['page_side_title'] = 'Содержание раздела'

    admin_navi = AdminNavigation()
    _t = sect_code
    tmpl_vars['current_section'] = admin_navi.get_section_by_code(sect_code)
    tmpl_vars['page_title'] = tmpl_vars['current_section']['label']
    tmpl_vars['navi'] = admin_navi.get_sections_navi(tmpl_vars['current_section']['code'])
    current_subitem = None
    if tmpl_vars['navi']:
        for it in tmpl_vars['navi']:
            if it['code'] == subitem_code:
                current_subitem = it
                break
    if current_subitem is not None:
        tmpl_vars['page_title'] += ':' + current_subitem['label']
        tmpl_vars['current_subitem'] = current_subitem
    tmpl_vars['save_action'] = url_for(WEB_MOD_NAME + '.navigation_save_block')
    tmpl_vars['navi_blocks'] = admin_navi.get_navi_blocks()
    # нужно получить блоки по умолчанию
    def_config = AdminUtils.get_default_config()
    def_blocks = []
    def_blocks = (def_config.get('navi.Codes')).values()
    tmpl_vars['def_blocks'] = list(def_blocks)
    # требуется каждому блоку добавить путь - в дереве каких отношений участвует
    # есть ли у него родители
    _tpl_name = os.path.join(AdminConf.MOD_NAME, 'admin_navigation.html')
    return app_api.render_page(_tpl_name, **tmpl_vars)


@mod.route('/navigation/<block>', defaults={'item': ''}, methods=['GET'], strict_slashes=False)
@mod.route('/navigation/<block>/<item>', methods=['GET'], strict_slashes=False)
@requires_auth
def edit_navigation(block, item):
    tmpl_vars = {}
    # tmpl_vars['project_name'] = 'Semantic PLM'
    tmpl_vars['title'] = 'Административный интерфейс'
    tmpl_vars['page_title'] = 'Настройки навигации: '
    tmpl_vars['page_side_title'] = 'Содержание раздела'
    tmpl_vars['navi_block'] = {}

    app_cfg = app_api.get_app_config()
    admin_navi = AdminNavigation()

    # нужно получить блоки по умолчанию
    def_config = AdminUtils.get_default_config()
    def_blocks = []
    def_blocks = list((def_config.get('navi.Codes')).values())

    has_block = False
    curr_blk = None
    curr_point = None
    blocks_lst = admin_navi.get_navi_blocks()
    for blk in blocks_lst:
        if blk['code'] == block:
            curr_blk = blk
            has_block = True
            break

    is_def_block = False
    is_def_block = block in def_blocks
    tmpl_vars['is_locked'] = []
    defaults_path = AdminConf.get_mod_path(AdminConf.INIT_DIR_NAME)
    defaults_path = os.path.join(defaults_path, AdminConf.NAVI_DIR_NAME)
    def_navi = AdminNavigation()
    def_navi.set_work_dir(defaults_path)
    if has_block:
        tmpl_vars['navi_block'] = curr_blk
        tmpl_vars['page_title'] += curr_blk['label']
        if is_def_block:
            def_links = def_navi.get_file_source(block)
            tmpl_vars['is_locked'] = [i['code'] for i in def_links]
        # теперь будем искать файл имя которого равно коду блока
        items_lst = admin_navi.get_sections_navi(curr_blk['code'])
        tmpl_vars['block_items'] = items_lst
        if items_lst:
            # print(items_lst)
            for it in items_lst:
                if item == it['code']:
                    curr_point = it
                    break

    tpl_name = 'navigation.html'
    if item:
        is_def_block_point = False
        tpl_name = 'navigation_item.html'
        tmpl_vars['save_action'] = url_for(WEB_MOD_NAME + '.navigation_save_item')
        tmpl_vars['user_roles'] = []
        if app_api.is_app_module_enabled('user_mgt'):
            users_api = app_api.get_mod_api('user_mgt')
            tmpl_vars['user_roles'] = users_api.get_roles()
        tmpl_vars['link_selector'] = os.path.join(AdminConf.MOD_NAME, 'link_selector.html')
        tmpl_vars['link_selector'] = app_api.correct_template_path(tmpl_vars['link_selector'])
        tmpl_vars['parent_navi_code'] = block
        tmpl_vars['current_navi_code'] = item
        tmpl_vars['_base_tpl'] = os.path.join(AdminConf.MOD_NAME, '')
        tmpl_vars['_base_tpl'] = app_api.correct_template_path(tmpl_vars['_base_tpl'])

    if curr_point:
        curr_point['roles_'] = []
        if 'roles' in curr_point:
            curr_point['roles_'] = curr_point['roles'].split(',')

    tmpl_vars['back_url'] = url_for(WEB_MOD_NAME + '.edit_navigation', block=block)
    tmpl_vars['curr_blk'] = curr_blk
    tmpl_vars['curr_point'] = {} if curr_point is None else curr_point
    tpl_name = os.path.join(AdminConf.MOD_NAME, tpl_name.lstrip(os.path.sep))
    return app_api.render_page(tpl_name, **tmpl_vars)


def _sort_items(lst, ord='asc', attr='label'):
    sort_result = []
    sort_result = lst
    revers = True if 'asc' != ord else False
    sort_result = sorted(sort_result, key=lambda x: x[attr], reverse=revers)
    return sort_result


@mod.route('/navigation/item/links', methods=['POST'])
@requires_auth
def navigation_item_links():
    """
    Возвращаем список моудлей (приложение также объявляем модулем) .
    Каждый модуль описывается наименованием, кодом и списком доступных ссылок.
    Каждая ссылка представлена отображаемым текстом и адресом для перехода.
    :return:
    """
    answer = {'msg': '', 'data': None, 'state': 404}

    _module = {'name': '', 'label': '', 'links': []}
    _link = {'label': '', 'href': '', 'roles': []}

    modules = []

    # получаем список модулей
    mod_manager = app_api.get_mod_manager()
    mods_lst = mod_manager.get_available_modules()
    if mods_lst:
        for modx in mods_lst:
            _mod = {'name': '', 'label': '', 'links': []}
            _mod['name'] = modx
            _mod['label'] = modx
            _mod['links'] = mod_manager.get_mod_open_urls(modx)
            modules.append(_mod)
        answer['state'] = 200

    answer['data'] = modules

    return json.dumps(answer)

@mod.route('/navigation/item/sort', methods=['POST'])
@requires_auth
def navigation_sort_item():
    """"""
    answer = {'msg': '', 'data': None, 'state': 404}
    app_cfg = app_api.get_app_config()
    admin_navi = AdminNavigation()
    block = ''
    item = ''
    direct = 0
    # определяем код блока и код пункта
    field = 'block'
    if request.form[field]:
        block = request.form[field]

    field = 'item'
    if request.form[field]:
        item = request.form[field]

    field = 'dir'
    if request.form[field]:
        direct = 0 + int(request.form[field])

    # проверим на существование блока с кодом block - если нет то ошибка -
    answer['state'] = 300
    answer['msg'] = 'Навигационный блок с кодом {} отсутствует!' . format(block)
    has_block = False
    blocks_lst = admin_navi.get_navi_blocks()
    for blk in blocks_lst:
        if blk['code'] == block:
            has_block = True
            break

    # блок с куказанным кодом существует
    has_item = False
    if has_block:
        answer['state'] = 300
        answer['msg'] = 'Пункт навигации с кодом {} отсутствует!' . format(item)
        # обрабатываем файл блока
        items_lst = admin_navi.get_sections_navi(block)
        if items_lst:
            _t = []
            new_srtid = 0
            ki = 0
            for it in items_lst:
                if it['code'] == item:
                    has_item = True
                    break
                    """"""
            # определяем будущий srtid
            # direct - -1 - уменьшаем srtid - перемещаем пункт в начало списка
            # direct - 1 - увеличиваем srtid - перемещаем пункт в конец списка

            new_srtid = it['srtid'] + direct
            # теперь найдем с таким же показанием другой пункт меню
            same_sort = _get_by_srtid(items_lst, new_srtid)
            for it in items_lst:
                if it['code'] == item:
                    it['srtid'] = new_srtid
                if same_sort is not None and it['code'] == same_sort['code']:
                    it['srtid'] = same_sort['srtid'] - direct
                _t.append(it)
            items_lst = _t

            admin_navi.save_file(block, items_lst)

    if has_item:
        answer['state'] = 200
        answer['msg'] = ''
        answer['data'] = item
    return json.dumps(answer)


def _get_by_srtid(lst, val):
    for it in lst:
        if val == it['srtid']:
            return it
    return None


@mod.route('/navigation/item/delete', methods=['POST'])
@requires_auth
def navigation_remove_item():
    """"""
    answer = {'msg': '', 'data': None, 'state': 404}
    app_cfg = app_api.get_app_config()
    admin_navi = AdminNavigation()
    block = ''
    item = ''
    # определяем код блока и код пункта
    field = 'block'
    if request.form[field]:
        block = request.form[field]

    field = 'item'
    if request.form[field]:
        item = request.form[field]

    # проверим на существование блока с кодом block - если нет то ошибка -
    file_name = 'navi_blocks.json'
    file_path = os.path.join(AdminConf.get_mod_path('data'), 'navi', file_name)
    content = CodeHelper.read_file(file_path)
    answer['state'] = 300
    answer['msg'] = 'Навигационный блок с кодом {} отсутствует!' . format(block)
    has_block = False
    blocks_lst = admin_navi.get_navi_blocks()
    if blocks_lst:
        for blk in blocks_lst:
            if blk['code'] == block:
                has_block = True
                break

    # блок с куказанным кодом существует
    has_item = False
    if has_block:
        answer['state'] = 300
        answer['msg'] = 'Пункт навигации с кодом {} отсутствует!' . format(item)
        items_lst = admin_navi.get_sections_navi(block)
        has_childs = admin_navi.is_empty(item)
        if not has_childs:
            if items_lst:
                _t = []
                for it in items_lst:
                    if it['code'] == item:
                        has_item = True
                        continue
                    _t.append(it)
                items_lst = _t
            admin_navi.save_file(block, items_lst)
        else:
            has_item = False # hook
            answer['state'] = 300
            answer['msg'] = 'Пункт навигации с кодом {} имеет дочернии ссылки!'.format(item)

    if has_item:
        answer['state'] = 200
        answer['msg'] = ''
        answer['data'] = item
    return json.dumps(answer)


@mod.route('/navigation/item/save', methods=['POST'])
@requires_auth
def navigation_save_item():
    """"""
    answer = {'msg': '', 'data': None, 'state': 404}
    app_cfg = app_api.get_app_config()
    admin_navi = AdminNavigation()
    block_data = {}
    block_data = admin_navi.get_link_tpl()
    block = ''
    cur_item_code = ''

    next_page = ''
    field = 'next_page'
    if request.form[field]:
        next_page = request.form[field]
        next_page = next_page if -1 < next_page.find('/') else url_for(next_page)

    # определяем код блока и код пункта
    field = 'NaviCode'
    if request.form[field]:
        block = request.form[field]

    field = 'NaviItem'
    cur_item_code = 'new' if '' == request.form[field] else request.form[field]

    # проверим на существование блока с кодом block - если нет то ошибка -
    has_block = False
    blocks_lst = admin_navi.get_navi_blocks()
    if blocks_lst:
        for blk in blocks_lst:
            if blk['code'] == block:
                has_block = True
                break

    # блок с куказанным кодом существует
    if has_block:
        items_lst = admin_navi.get_sections_navi(block)
        # теперь приступаем к обработке присланных данных
        field = 'NaviItemName'
        if request.form[field]:
            block_data['label'] = request.form[field]
        field = 'NaviItemCode'
        if request.form[field]:
            block_data['code'] = str(request.form[field]).strip()
        field = 'NaviItemLink'
        if request.form[field]:
            block_data['href'] = str(request.form[field]).strip()
        field = 'NaviItemRoles'
        if request.form[field]:
            block_data['roles'] = request.form[field]
        field = 'NaviItemDisDropdown'
        block_data['DisDropdown'] = 0
        # print('request.form', request.form)
        # так как данный элемент управления  checkbox то надо проверять наличие ключа
        if field in request.form:
            block_data['DisDropdown'] = 1

        if '' == block_data['code']:
            msg = 'Не указан код пункта навигации!'
            if '' != next_page:
                flash(msg)
                next_page = url_for(WEB_MOD_NAME + '.edit_navigation', block=block, item=cur_item_code)
                return redirect(next_page)
            else:
                answer['state'] = 400
                answer['msg'] = msg
                return json.dumps(answer)

        has_item = False
        for it in items_lst:
            if it['code'] == cur_item_code:
                has_item = True
                break
        if not has_item:
            answer['state'] = 200
            answer['msg'] = ''
            answer['data'] = block_data
            block_data['srtid'] = len(items_lst) + 1
            block_data['id'] = len(items_lst) + 1
            items_lst.append(block_data)
        else:
            answer['state'] = 200
            answer['msg'] = ''
            _t = []
            for it in items_lst:
                if it['code'] == cur_item_code:
                    it['label'] = block_data['label']
                    it['code'] = block_data['code']
                    it['href'] = block_data['href']
                    it['roles'] = block_data['roles']
                    it['DisDropdown'] = block_data['DisDropdown']
                    block_data = it
                    # print('it', it)
                _t.append(it)
            if _t:
                items_lst = _t
        admin_navi.save_file(block, items_lst)
    msg = ''
    if '' != next_page:
        if '' != answer['msg']:
            msg = answer['msg']
            flash(msg)
        return redirect(next_page)
    else:
        answer['msg'] = msg
        return json.dumps(answer)


@mod.route('/navigation/block/delete', methods=['POST'])
@requires_auth
def navigation_remove_block():
    answer = {'msg': '', 'data': None, 'state': 404}

    field = 'code'
    code = ''
    if request.form[field]:
        code = request.form[field]

    app_cfg = app_api.get_app_config()
    admin_navi = AdminNavigation()
    answer['state'] = 500
    answer['msg'] = 'Отсутствует описание навигационных блоков'
    has_block = False
    blocks_lst = admin_navi.get_navi_blocks()
    if blocks_lst:
        answer['state'] = 300
        answer['msg'] = 'Навигационный блок с кодом {} отсутствует!' . format(code)
        codes_lst = [blk['code'] for blk in blocks_lst]
        has_block = code in codes_lst # есть ли блок который пытаемся удалить
        has_childs = False
        if has_block:
            _childs = admin_navi.get_sections_navi(code)
            has_childs = 0 < len(_childs) # проверяем наличие детей
        if not has_childs:
            _t = []
            for blk in blocks_lst:
                if blk['code'] == code:
                    has_block = True
                    continue
                _t.append(blk)
            blocks_lst = _t
            admin_navi.save_file('navi_blocks', blocks_lst)
            admin_navi.remove_file(code) # удаляем файл так как удаляем блок у которого нет детей
        else:
            has_block = False # чтобы не переписывать код
            answer['state'] = 300
            answer['msg'] = 'Навигационный блок с кодом {} имеет дочернии ссылки!'.format(code)
    if has_block:
        # надо проверить есть ли файл с ссылками - если есть то
        # пробежаться по ссылкам в файле и выбрать их коды
        # искать коды среди блоков и повторить процедуру
        answer['state'] = 200
        answer['msg'] = ''
        answer['data'] = code
    return json.dumps(answer)


@mod.route('/navigation/block/save', methods=['POST'])
@requires_auth
def navigation_save_block():
    """"""
    answer = {'msg': '', 'data': None, 'state': 404}
    app_cfg = app_api.get_app_config()
    admin_navi = AdminNavigation()
    block_data = {}
    block_data = admin_navi.get_link_tpl()

    next_page = ''
    field = 'next_page'
    if request.form[field]:
        next_page = request.form[field]

    field = 'NaviBlockName'
    if request.form[field]:
        block_data['label'] = request.form[field]
    field = 'NaviBlockCode'
    if request.form[field]:
        block_data['code'] = request.form[field]
    field = 'NaviBlockLink'
    if request.form[field]:
        block_data['href'] = request.form[field]

    if '' == block_data['code']:
        msg = 'Не указан код блока навигации!'
        if '' != next_page:
            flash(msg)
            return redirect(url_for(next_page))
        else:
            answer['state'] = 400
            answer['msg'] = msg
            return json.dumps(answer)

    answer['state'] = 300
    answer['msg'] = 'Навигационный блок с кодом {} уже существует!' . format(block_data['code'])
    blocks_lst = admin_navi.get_navi_blocks()
    field = 'NaviCode'
    old_code = ''
    if request.form[field]:
        old_code = request.form[field]
    def_blocks = admin_navi.get_default_blocks()
    if blocks_lst:
        has_block = False
        update_blocks = False
        for blk in blocks_lst:
            if blk['code'] == old_code:
                has_block = True
                break
        if not has_block:
            answer['state'] = 200
            answer['msg'] = ''
            answer['data'] = block_data
            block_data['srtid'] = len(blocks_lst) + 1
            block_data['id'] = len(blocks_lst) + 1
            blocks_lst.append(block_data)
            update_blocks = True
        else:
            answer['state'] = 200
            answer['msg'] = ''
            _t = []
            for blk in blocks_lst:
                if blk['code'] == old_code:
                    # print('Find code in list')
                    blk['label'] = block_data['label']
                    if old_code not in def_blocks:
                        blk['code'] = block_data['code']
                    blk['href'] = block_data['href']
                    update_blocks = True
                _t.append(blk)
            if _t:
                blocks_lst = _t
            # теперь надо переименовать файл блока
            if old_code not in def_blocks:
                admin_navi.rename_file(old_code, block_data['code'])
        if update_blocks:
            admin_navi.save_file('navi_blocks', blocks_lst)
    msg = ''
    if '' != next_page:
        if '' != answer['msg']:
            msg = answer['msg']
            flash(msg)
        return redirect(url_for(next_page))
    else:
        answer['msg'] = msg
        return json.dumps(answer)
# } Navigation


@mod.route('/section', defaults={'code': '', 'sub_item': ''}, methods=['GET'], strict_slashes=False)
@mod.route('/section/<code>', defaults={'sub_item': ''}, methods=['GET'], strict_slashes=False)
@mod.route('/section/<code>/<sub_item>', methods=['GET'], strict_slashes=False)
@requires_auth
def section_view(code, sub_item):
    """
    Функция общей обработки запросов к административному интерфейсу
    :param code: Код секции
    :param sub_item: Код подпункта
    :return:
    """
    tmpl_vars = {}
    # tmpl_vars['project_name'] = 'Semantic PLM'
    tmpl_vars['title'] = 'Административный интерфейс'
    tmpl_vars['page_title'] = 'Административный интерфейс портала'
    tmpl_vars['page_side_title'] = 'Содержание раздела'

    admin_navi = AdminNavigation()
    # горизонтальная навигация административного интерфейса
    # пункт который вшит в код - настройки
    # пункт имеет единственный подпункт - навигация по административному интерфейсу
    tmpl_vars['sections'] = []
    tmpl_vars['navi'] = []
    # собрать навигацию
    tmpl_vars['sections'] = admin_navi.get_sections()
    # print('host', request.host)
    # print('endpoint', request.endpoint)
    # print('url', request.url)
    # print('full_path', request.full_path)
    # print('path', request.path)
    # print('module', request.module) # ???????
    current_section = admin_navi.get_current_section(request)
    if current_section is None:
        if '' == code:
            current_section = tmpl_vars['sections'][0]
        else:
            current_section = admin_navi.get_section_by_code(code)
    if current_section['code'] != code:
        current_section = admin_navi.get_section_by_code(code)
    # теперь займемся отрисовкой секции
    tmpl_vars['page_title'] = current_section['label']
    tmpl_vars['navi'] = admin_navi.get_sections_navi(current_section['code'])
    current_subitem = None
    if tmpl_vars['navi']:
        if '' == sub_item:
            current_subitem = tmpl_vars['navi'][0]
        else:
            for it in tmpl_vars['navi']:
                if it['code'] == sub_item:
                    current_subitem = it
                    break
    else:
        # hook hook hook
        if 'Configurator' == current_section['code']:
            # return url_for('configurator.config_editor')
            tmpl_vars['navi'] = []
            conf_list = ConfiguratorUtils.get_configurator_navi()
            for ci in conf_list:
                tpl = AdminNavigation.get_link_tpl()
                tpl['label'] = ci['label']
                tpl['href'] = url_for(ConfiguratorUtils.get_webeditor_endpoint(), config_name=ci['href'])
                tpl['roles'] = ci['roles']
                tpl['code'] = ci['code']
                tmpl_vars['navi'].append(tpl)
    if current_subitem is not None:
        tmpl_vars['page_title'] += ':' + current_subitem['label']
    return app_api.render_page(AdminConf.get_root_tpl(), **tmpl_vars)


@mod.route('/interfaceData', methods=['GET', 'POST'])
@mod.route('/interfaceData/', methods=['GET', 'POST'])
@requires_auth
def interface_data():
    portal_cfg = app_api.get_app_config()  # get_config_util()(AdminConf.CONFIGS_PATH)
    _conf = AdminUtils.get_portal_config()
    interface = {}
    interface['interface'] = {
        'close': 'Закрыть',
        'save': 'Сохранить',
        'delete': 'Удалить',
        'edit': 'Редактировать',
        'list': 'Список',
        'close': 'Закрыть',
        'upload': 'Загрузить',
        'update': 'Обновить'
    }
    interface['header'] = interface['title'] = 'Административный интерфейс портала'
    interface['navMenu'] = [
        {'label': 'Пользователи','pageLabel': 'Пользователи портала','code': 'PortalUsers','targetBlkID': 'NaviPageBox','isStarted': True,'extModule': True},
        {'label': 'Страницы','pageLabel': 'Страницы портала','code': 'PortalPages','targetBlkID': 'NaviPageBox','isStarted': False},
        {'label': 'Роли','pageLabel': 'Роли пользователей портала','code': 'UserRoles','targetBlkID': 'NaviPageBox','isStarted': False},
        {'label': 'Файлы','pageLabel': 'Файлы портала','code': 'PortalFiles','targetBlkID': 'NaviPageBox','isStarted': False,'extModule': True},
        {'label': 'Новости','pageLabel': 'Новости портала','code': 'PortalNews','targetBlkID': 'NaviPageBox','isStarted': True,'extModule': True},
        {'label': 'Журнал авторизации','pageLabel': 'Журнал авторизации портала','code': 'PortalUAccLog','targetBlkID': 'NaviPageBox','isStarted': False,'extModule': True},
        {'label': 'Инструменты','pageLabel': 'Инструменты портала','code': 'PortalTools','targetBlkID': 'NaviPageBox','isStarted': False,'extModule': True},
    ]
    interface['authPhrase'] = 'Для получения доступа авторизуйтесь пожалуйста, <a href="#{href}">войти</a>!'
    interface['logoutBtn'] = 'Выход'
    interface['Errors'] = {
        'navi': {
            '100': 'Не удалось создать блок навигации для страницы',
            '101': 'Не известно из чего стряпать навигационный блок!',
            '102': 'Не удалось определить контейнер для блока навигации!',
            '103': 'Не указан контейнер для навигационного блока!',
            '104': 'Не существует пункта с указанным кодом'
        }
    }

    # $phpini =  ini_get_all();

    interface['Pages'] = {
        'PortalUsers': {
            'minLoginLength': _conf.get('users.Login.minLen'), # portalApp::getInstance()->getSetting('main.Info.login.minLen'),
            'minPaswdLength': _conf.get('users.Secret.minLen'), # portalApp::getInstance()->getSetting('main.Info.pswd.minLen'),
            'Errors': {
                '100': 'Неизвестный идентификатор(#{id}) закладки для открытия!',
                '101': 'Не заполнено обязательное поле',
                '102': 'Поле "#{field}" незаполнено или имеет неверный формат или количество символов меньше минимального',
                '103': 'Поле "#{field}" или его подтверждение незаполнено!',
                '104': 'Поле "#{field}" незаполнено!',
                '105': 'Пароль и Подтверждение пароля несовпадают!',
                '106': 'Длина пароля меньше минимальной',
                '107': 'Не корректный формат',
                '108': 'Не верный формат точки возврата!',
                '109': 'Не указан идентификатор таба для определения ключа пользователя!'
            },
            'Msgs': { 'del': 'Вы действительно хотите удалить пользователя' },
            'interface': {
                'title': 'Пользователи портала',
                'close': 'Закрыть',
                'save': 'Сохранить',
                'delete': 'Удалить',
                'edit': 'Редактировать',
                'list': 'Список',
                'addUser': 'Создать пользователя',
                'newUser': 'Новый пользователь',
                'fio': 'ФИО',
                'login': 'Логин',
                'password': 'Пароль',
                'email': 'Email',
                'roles': 'Роли',
                'user': 'Пользователь',
                'field': 'Поле',
                'nofill': 'незаполнено',
                'nofill': 'или его подтверждение незаполнено',
                'nofill': 'незаполнено или имеет неверный формат или количество символов меньше минимального',
                'table': [
                    {'sTitle':  'Действия', 'sName':  'Actions', 'mData': 'Actions','sWidth': '68px', 'sClass': 'row-actions', 'bSortable':  False},
                    {'sTitle':  'ID', 'sName':  'ID', 'mData': 'ID', 'bVisible':  False, 'sClass': 'usr-id', 'bSortable':  False},
                    {'sTitle':  'ФИО', 'sName':  'FIO', 'mData': 'FIO', 'sClass': 'usr-fio'},
                    {'sTitle':  'Логин', 'sName':  'Login', 'mData': 'Login', 'sClass': 'usr-login'},
                    {'sTitle':  'Email', 'sName':  'Email', 'mData': 'Email', 'sClass': 'usr-email'},
                    {'sTitle':  'Роли', 'sName':  'Roles', 'mData': 'Roles', 'sClass': 'usr-roles', 'bSortable':  False}
                ]
            },
        },
        'PortalPages': {
            'Errors': { '100': 'Не верный формат точки возврата!'},
            'Msgs': { 'del': 'Вы действительно хотите удалить страницу'},
            'interface': {
                'title': 'Страницы портала',
                'close': 'Закрыть',
                'save': 'Сохранить',
                'delete': 'Удалить',
                'edit': 'Редактировать',
                'addPage': 'Добавить страницу',
                'page': 'Страница',
                'newPage': 'Новая страница',
                'pageName': 'Наименование страницы',
                'pageCode': 'Код страницы',
                'pageAddr': 'Адрес страницы',
                'pageDescr': 'Описание страницы',
                'roles': 'Роли',
            },
        },
        'UserRoles': {
            'Errors': { '100': 'Не верный формат точки возврата!'},
            'Msgs': { 'del': 'Вы действительно хотите удалить роль'},
            'interface': {
                'title': 'Роли пользователей портала',
                'close': 'Закрыть',
                'save': 'Сохранить',
                'delete': 'Удалить',
                'edit': 'Редактировать',
                'role': 'Роль',
                'newRole': 'Новая роль',
                'addRole': 'Добавить роль',
                'roleName': 'Наименование роли',
                'avalablePages': 'Доступные страницы',
                'users': 'Пользователи',
            },
        },
        'PortalFiles': {
            'Errors': { '100': 'Не верный формат точки возврата!'},
            'Msgs': { 'delFile': 'Вы действительно хотите удалить файл',
                    'delDir': 'Вы действительно хотите удалить директорию'
            },
            'interface': {
                'title': 'Файлы портала',
                'dirStructure': 'Структура директорий',
                'close': 'Закрыть',
                'save': 'Сохранить',
                'upload': 'Загрузить',
                'delete': 'Удалить',
                'update': 'Обновить',
                'edit': 'Редактировать',
                'list': 'Список',
                'type': 'Тип',
                'file': 'файл',
                'dir': 'директория',
                'addFile': 'Добавить файл',
                'selectFiles': 'Выберите файлы',
                'uploadFiles': 'Загрузить файлы',
                'addDir': 'Добавить директорию',
                'createDir': 'Создать директорию',
                'delFile': 'Удалить файл',
                'delDir': 'Удалить директорию',
                'nameDir': 'Наименование директории',
                'nameFile': 'Наименование файла',
                'name': 'Наименование',
                'path': 'Путь',
                'maxFileSizeLbl': 'Максимальный размер файла',
                'maxFileSize': '20', # ini_get('upload_max_filesize'),
                'maxFilesUploadLbl': 'Максимальное количество файлов',
                'maxFilesUpload': '20' # get_cfg_var('max_file_uploads')
            },
            'grid': {}
        }
    }
    # print(interface['Pages']['PortalFiles']['interface']['path'])
    # /* Файлы портала */
    """
    interface['Pages']['PortalFiles']['grid']['columns'] = {
        {'name': 'Toolbar','index': 'Toolbar','label': '-','width': '60px','sortable': False},
        {'name': 'Type','index': 'Type','label': interface['Pages']['PortalFiles']['interface']['type'],'hidden': True,'sortable': False},
        {'name': 'Name','index': 'Name','label': interface['Pages']['PortalFiles']['interface']['name']},
        {'name': 'Path','index': 'Path','label': interface['Pages']['PortalFiles']['interface']['path']}
    }
    # """
        # /* Файлы портала */
        # /* Новости портала */
    interface['Pages']['PortalNews']={
        'Errors': { '100': 'Не верный формат точки возврата!'},
        'Msgs': {
            'delFile': 'Вы действительно хотите удалить файл',
            'delDir': 'Вы действительно хотите удалить директорию'
        },
        'interface': {
            'header': 'Заголовок',
            'title': 'Новости портала',
            'news': 'Новость',
            'newsList': 'Список новостей',
            'sect': 'Раздел',
            'addNews': 'Добавить новость',
            'addSect': 'Добавить раздел',
            'createSect': 'Создать директорию',
            'createNews': 'Создать новость',
            'delNews': 'Удалить новость',
            'delSect': 'Удалить раздел',
            'nameSect': 'Наименование раздела',
            'nameNews': 'Наименование новости',
            'PubDate': 'Дата публикации',
            'CreateDate': 'Дата создания',
            'Text': 'Текст',
        }
    }
    # /* Новости портала */
    # /* Журнал авторизации */
    interface['Pages']['PortalUAccLog']={
        'Errors': { '100': 'Не верный формат точки возврата!'},
        'Msgs': {},
        'interface': {
            'header': 'Заголовок',
            'title': 'Журнал авторизации на портале',
            'rec': 'Запись',
            'recsList': 'Список записей',
            'AuthDate': 'Дата авторизации',
            'AuthTime': 'Время авторизации',
            'user': 'Пользователь',
            'login': 'Логин'
        }
    }
    # /* Журнал авторизации */
    # /* Инструменты портала */
    interface['Pages']['PortalTools']={
        'Errors': { '100': 'Не верный формат точки возврата!'},
        'Msgs': {},
        'interface': {
            'title': 'Инструменты портала'

        }
    }
    # /* Инструменты портала */
    return json.dumps(interface)




def get_executable_files():
    query = """SELECT ?cron_lbl ?cron_file WHERE {
        ?mod osplm:hasPathToCronExecutableFile ?mod_uri .
        ?mod_uri rdfs:label ?cron_lbl .
        ?mod_uri osplm:value ?cron_file .
        }"""

    executable_files = app_api.get_mod_manager().query(query)
    # {"text" : <label>, "value" : <file>}
    executable_files = [{"text" : str(item['cron_lbl']) + " - " + str(item['cron_file']), "value" : str(item['cron_file'])} for item in executable_files]

    return executable_files


@mod.route('/cron')
@requires_auth
def cron():
    return app_api.render_page('admin_mgt/cron.html', crons = Jobs("cron").get_job_data())


@mod.route('/cron_item/<cron_item>', methods=["GET", "POST"])
@mod.route('/cron_item/', methods=["GET", "POST"])
@requires_auth
def cron_item(cron_item = ''):
    template = 'admin_mgt/cron_item.html'

    job = Jobs("cron")
    if not cron_item:
        cron_item = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

    if request.method == 'GET':
        return app_api.render_page(template, cron_item = cron_item, values = job.get_job_object(cron_item), executable_files = get_executable_files(), alert_message = "")

    elif request.method == 'POST':
        if 'save' in request.form:
            try:
                if request.form['cron_item']:
                        active = request.form['active'] if 'active' in request.form and request.form['active'] else '0'
                        values = {"name" : request.form['name'], "period" : request.form['period'], "action" : request.form['action'], "active" : active}

                        # невалидный период
                        if not CronSlices.is_valid(values['period']):
                            return app_api.render_page(template, cron_item = request.form['cron_item'], values = job.get_job_object(request.form['cron_item']), executable_files = get_executable_files(), alert_message = "Период невалидный!")

                        # файл не существует
                        if not os.path.exists(os.path.join(app.config['APP_ROOT'], "app", values['action'])) or not os.path.isfile(os.path.join(app.config['APP_ROOT'], "app", values['action'])):
                            return app_api.render_page(template, cron_item = request.form['cron_item'], values = job.get_job_object(request.form['cron_item']), executable_files = get_executable_files(), alert_message = "Файл не существует!")


                        job.edit_job_object(request.form['cron_item'], values)
                        cron_reload(job)
            except:
                print("При изменении возникла ошибка!")

        if 'delete' in request.form:
            try:
                cron = CronTab(user=True)
                cron.remove_all(comment=request.form['cron_item'])
                cron.write()

                job.delete_job_object(request.form['cron_item'])
            except:
                print("При изменении возникла ошибка!")


        return redirect(url_for('portal_management.cron'))


def cron_reload(job):
    # Это настройка пути до python для сервера
    python_path = app.venv_exec if hasattr(app, 'venv_exec') else sys.executable

    cron_data = job.get_job_data()
    cron = CronTab(user=True)

    for item in cron_data:
        cron.remove_all(comment=item)
        if cron_data[item]['active'] == '1':
            PERIOD = cron_data[item]['period']
            if CronSlices.is_valid(PERIOD):
                action = cron_data[item]['action'].strip()
                if action.startswith("/") or action.startswith("\\"):
                    action = action[1:]
                COMMAND = python_path + " " + os.path.join(app.config['APP_ROOT'], "app", action)
                cron_job = cron.new(command = COMMAND, comment = item)
                cron_job.setall(PERIOD)
            else:
                print("NOT VALID PERIOD!!!")

    cron.write()






def job_by_script(action):
    log = os.path.join(app.config['APP_DATA_PATH'], "logs", "job_by_script.log")
    with open(log, "w", encoding="utf-8") as f:
        f.write("")

    script = os.path.join(app.config['APP_ROOT'], "app", action)
    data = ExtendProcesses.run(script, [], errors = log)



@mod.route('/schedule')
@requires_auth
def schedule_main():
    from app.app_api import tsc_query
    return app_api.render_page('admin_mgt/schedule.html', schedules = Jobs("schedule").get_job_data())



@mod.route('/schedule_item/<schedule_item>', methods=["GET", "POST"])
@mod.route('/schedule_item/', methods=["GET", "POST"])
@requires_auth
def schedule_item(schedule_item = ''):
    template = 'admin_mgt/schedule_item.html'

    job = Jobs("schedule")
    if not schedule_item:
        schedule_item = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

    if request.method == 'GET':
        return app_api.render_page(template, schedule_item = schedule_item, values = job.get_job_object(schedule_item), executable_files = get_executable_files(), alert_message = "")

    elif request.method == 'POST':
        if 'save' in request.form:
            try:
                if request.form['schedule_item']:
                    active = request.form['active'] if 'active' in request.form and request.form['active'] else '0'
                    values = {"name" : request.form['name'], "period" : request.form['period'], "action" : request.form['action'], "active" : active}
                    
                    # невалидный период
                    if not CronSlices.is_valid(values['period']):
                        return app_api.render_page(template, schedule_item = request.form['schedule_item'], values = job.get_job_object(request.form['schedule_item']), executable_files = get_executable_files(), alert_message = "Период невалидный!")

                    # файл не существует
                    if not os.path.exists(os.path.join(app.config['APP_ROOT'], "app", values['action'])) or not os.path.isfile(os.path.join(app.config['APP_ROOT'], "app", values['action'])):
                        return app_api.render_page(template, schedule_item = request.form['schedule_item'], values = job.get_job_object(request.form['schedule_item']), executable_files = get_executable_files(), alert_message = "Файл не существует!")

                    # чтобы изменить задание - сначала удаляем его, потом создаем заново
                    try:
                        current_app.apscheduler.remove_job(values['name'])
                    except:
                        pass

                    minute, hour, day, month, day_of_week = values['period'].split(' ')
                    current_app.apscheduler.add_job(id = values['name'], func=job_by_script, trigger="cron", day_of_week=day_of_week, month=month, day=day, hour=hour, minute=minute, second="0", args=[values['action']])

                    job.edit_job_object(request.form['schedule_item'], values)

            except:
                print("При изменении возникла ошибка!")


        if 'delete' in request.form:
            try:
                current_app.apscheduler.remove_job(request.form['schedule_item'])
                job.delete_job_object(request.form['schedule_item'])
            except:
                print("При изменении возникла ошибка!")


        return redirect(url_for('portal_management.schedule_main'))

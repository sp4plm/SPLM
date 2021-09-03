# -*- coding: utf-8 -*-
"""
Модуль предназначен для административного интерфейса портала
"""

import os
import json
import subprocess
from math import ceil

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask_login import current_user, login_user, logout_user
from flask_login import login_required
from werkzeug.urls import url_parse
from app import db, app_api, CodeHelper, mod_manager
from app.module_mgt.manager import Manager
from .admin_utils import AdminUtils, AdminConf
from .mod_api import ModApi
from .admin_navigation import AdminNavigation
from .decorators import requires_auth


from .forms import LoginForm # , RegisterForm

from app.admin_mgt.models.user import User, EmbeddedUser
if app_api.is_app_module_enabled('user_mgt'):
    # print('catch user module')
    from app.user_mgt.models.users import User

mod = Blueprint(AdminConf.MOD_NAME, __name__, url_prefix=AdminConf.MOD_WEB_ROOT,
                static_folder=AdminConf.get_web_static_path(),
                template_folder=AdminConf.get_web_tpl_path())

mod.add_app_template_global(ModApi.get_root_tpl, name='admin_root_tpl')
# добавить навигацию по секциям
mod.add_app_template_global(request, name='flask_request')
mod.add_app_template_global(AdminUtils.get_admin_sections, name='admin_sections')
mod.add_app_template_global(AdminUtils.get_admin_section_navi, name='admin_section_navi')
mod.add_app_template_global(AdminUtils.get_current_sectionin_tpl, name='admin_current_section')
mod.add_app_template_global(AdminUtils.get_current_subitem_tpl, name='admin_current_subitem')


# для начала опишем системную обработку перед любым запросом


@mod.route('/', methods=['GET'])
@mod.route('/index', methods=['GET'])
@requires_auth
def index():
    # проверяем тип авторизации
    # стартуем сессию для пользователя

    tmpl_vars = {}
    # tmpl_vars['project_name'] = 'Semantic PLM'
    tmpl_vars['title'] = 'Административный интерфейс'
    tmpl_vars['page_title'] = 'Административный интерфейс портала'
    tmpl_vars['page_side_title'] = 'Содержание раздела'
    admin_navi = AdminNavigation()
    sections = admin_navi.get_sections()
    if sections:
        tmpl_vars['current_section'] = sections[0]
    # tmpl_vars['page_side_title'] = 'Содержание раздела'

    # print('host', request.host)
    # print('endpoint', request.endpoint)
    # print('url', request.url)
    # print('full_path', request.full_path)
    # print('path', request.path)
    # print('module', request.module) # ???????
    return render_template(AdminConf.get_root_tpl(), **tmpl_vars)

# { Navigationset_authorisation_method


@mod.route('/navigation', methods=['GET'], strict_slashes=False)
@requires_auth
def admin_navigation():
    """"""
    sect_code = 'PortalSettings'
    subitem_code = 'PortalNaviTool'
    tmpl_vars = {}
    # tmpl_vars['project_name'] = 'Semantic PLM'
    tmpl_vars['title'] = 'Административный интерфейс'
    tmpl_vars['page_title'] = 'Административный интерфейс портала'
    tmpl_vars['page_side_title'] = 'Содержание раздела'

    admin_navi = AdminNavigation()
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
    tmpl_vars['save_action'] = url_for('admin_mgt.navigation_save_block')
    tmpl_vars['navi_blocks'] = admin_navi.get_navi_blocks()
    return render_template('admin_navigation.html', **tmpl_vars)


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
    file_name = 'navi_blocks.json'
    file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
    content = CodeHelper.read_file(file_path)
    has_block = False
    catch_item = False
    curr_blk = None
    curr_point = None
    if content:
        blocks_lst = json.loads(content)
        for blk in blocks_lst:
            if blk['code'] == block:
                curr_blk = blk
                has_block = True
                break

    if has_block:
        tmpl_vars['navi_block'] = curr_blk
        tmpl_vars['page_title'] += curr_blk['label']
        # теперь будем искать файл имя которого равно коду блока
        block_file = curr_blk['code'] + '.json'
        block_path = os.path.join(AdminConf.DATA_PATH, 'navi', block_file)
        block_content = CodeHelper.read_file(block_path)
        if block_content:
            items_lst = json.loads(block_content)
            items_lst = _sort_items(items_lst, attr='srtid')
            tmpl_vars['block_items'] = items_lst
            if items_lst:
                for it in items_lst:
                    if item == it['code']:
                        curr_point = it
                        break

    tpl_name = 'navigation.html'
    if item:
        tpl_name = 'navigation_item.html'
        tmpl_vars['save_action'] = url_for('admin_mgt.navigation_save_item')
        tmpl_vars['user_roles'] = []
        if app_api.is_app_module_enabled('user_mgt'):
            users_api = app_api.get_mod_api('user_mgt')
            tmpl_vars['user_roles'] = users_api.get_roles()
        tmpl_vars['link_selector'] = 'link_selector.html'
        tmpl_vars['parent_navi_code'] = block
        tmpl_vars['current_navi_code'] = item

    if curr_point:
        curr_point['roles_'] = []
        if curr_point['roles']:
            curr_point['roles_'] = curr_point['roles'].split(',')

    tmpl_vars['back_url'] = url_for('admin_mgt.edit_navigation', block=block)
    tmpl_vars['curr_blk'] = curr_blk
    tmpl_vars['curr_point'] = curr_point

    return render_template(tpl_name, **tmpl_vars)


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
    mods_lst = mod_manager.get_available_modules()
    if mods_lst:
        for modx in mods_lst:
            _mod = {'name': '', 'label': '', 'links': []}
            _mod['name'] = modx
            _mod['label'] = modx
            _mod['links'] = mod_manager.get_mod_open_urls(modx)
            modules.append(_mod)


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
    file_name = 'navi_blocks.json'
    file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
    content = CodeHelper.read_file(file_path)
    answer['state'] = 300
    answer['msg'] = 'Навигационный блок с кодом {} отсутствует!' . format(block)
    has_block = False
    if content:
        # сперва проверяем что блок навигации существует
        blocks_lst = json.loads(content)
        for blk in blocks_lst:
            if blk['code'] == block:
                has_block = True
                break

    # блок с куказанным кодом существует
    has_item = False
    if has_block:
        file_name = block + '.json'
        file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
        answer['state'] = 300
        answer['msg'] = 'Пункт навигации с кодом {} отсутствует!' . format(item)
        # обрабатываем файл блока
        content = CodeHelper.read_file(file_path)
        if content:
            """"""
            # получили содержимое файла блока
            items_lst = json.loads(content)
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
            old_srtid = same_sort['srtid'] - direct
            for it in items_lst:
                if it['code'] == item:
                    it['srtid'] = new_srtid
                if it['code'] == same_sort['code']:
                    it['srtid'] = old_srtid
                _t.append(it)
            items_lst = _t

            content = ''
            content = json.dumps(items_lst)
            CodeHelper.write_to_file(file_path, content, mod='w')

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
    file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
    content = CodeHelper.read_file(file_path)
    answer['state'] = 300
    answer['msg'] = 'Навигационный блок с кодом {} отсутствует!' . format(block)
    has_block = False
    if content:
        # сперва проверяем что блок навигации существует
        blocks_lst = json.loads(content)
        for blk in blocks_lst:
            if blk['code'] == block:
                has_block = True
                break

    # блок с куказанным кодом существует
    has_item = False
    if has_block:
        file_name = block + '.json'
        file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
        answer['state'] = 300
        answer['msg'] = 'Пункт навигации с кодом {} отсутствует!' . format(item)
        # обрабатываем файл блока
        content = CodeHelper.read_file(file_path)
        if content:
            """"""
            # получили содержимое файла блока
            items_lst = json.loads(content)
            _t = []
            for it in items_lst:
                if it['code'] == item:
                    has_item = True
                    continue
                _t.append(it)
            items_lst = _t
            content = ''
            content = json.dumps(items_lst)
            CodeHelper.write_to_file(file_path, content, mod='w')

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
    file_name = 'navi_blocks.json'
    file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
    content = CodeHelper.read_file(file_path)
    has_block = False
    if content:
        # сперва проверяем что блок навигации существует
        blocks_lst = json.loads(content)
        for blk in blocks_lst:
            if blk['code'] == block:
                has_block = True
                break

    # блок с куказанным кодом существует
    if has_block:
        file_name = block + '.json'
        file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
        # обрабатываем файл блока
        if not CodeHelper.check_file(file_path):
            CodeHelper.add_file(file_path)
            CodeHelper.write_to_file(file_path, '[]', mod='w')
        content = CodeHelper.read_file(file_path)
        if content:
            # получили содержимое файла блока
            items_lst = json.loads(content)
            # теперь приступаем к обработке присланных данных
            field = 'NaviItemName'
            if request.form[field]:
                block_data['label'] = request.form[field]
            field = 'NaviItemCode'
            if request.form[field]:
                block_data['code'] = request.form[field]
            field = 'NaviItemLink'
            if request.form[field]:
                block_data['href'] = request.form[field]
            field = 'NaviItemRoles'
            if request.form[field]:
                block_data['roles'] = request.form[field]

            if '' == block_data['code']:
                msg = 'Не указан код пункта навигации!'
                if '' != next_page:
                    flash(msg)
                    next_page = url_for('admin_mgt.edit_navigation', block=block, item=cur_item_code)
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
                block_data['srtid'] = len(items_lst)
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
                        block_data = it
                    _t.append(it)
                if _t:
                    items_lst = _t
            content = ''
            content = json.dumps(items_lst)
            CodeHelper.write_to_file(file_path, content, mod='w')
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
    file_name = 'navi_blocks.json'
    file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
    content = CodeHelper.read_file(file_path)
    has_block = False
    if content:
        answer['state'] = 300
        answer['msg'] = 'Навигационный блок с кодом {} отсутствует!' . format(code)
        blocks_lst = json.loads(content)
        _t = []
        for blk in blocks_lst:
            if blk['code'] == code:
                has_block = True
                continue
            _t.append(blk)
        blocks_lst = _t
        content = ''
        content = json.dumps(blocks_lst)
        CodeHelper.write_to_file(file_path, content, mod='w')
    if has_block:
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

    file_name = 'navi_blocks.json'
    file_path = os.path.join(AdminConf.DATA_PATH, 'navi', file_name)
    if not CodeHelper.check_file(file_path):
        CodeHelper.add_file(file_path)
        CodeHelper.write_to_file(file_path, '[]', mod='w')
    content = CodeHelper.read_file(file_path)
    if content:
        answer['state'] = 300
        answer['msg'] = 'Навигационный блок с кодом {} уже существует!' . format(block_data['code'])
        blocks_lst = json.loads(content)
        has_block = False
        for blk in blocks_lst:
            if blk['code'] == block_data['code']:
                has_block = True
                break
        if not has_block:
            answer['state'] = 200
            answer['msg'] = ''
            answer['data'] = block_data
            blocks_lst.append(block_data)
        else:
            field = 'NaviCode'
            if request.form[field] and request.form[field] == block_data['code']:
                answer['state'] = 200
                answer['msg'] = ''
                _t = []
                for blk in blocks_lst:
                    if blk['code'] == block_data['code']:
                        blk['label'] == block_data['label']
                        blk['code'] == block_data['code']
                        blk['href'] == block_data['href']
                    _t.append(blk)
                if _t:
                    blocks_lst = _t
        content = ''
        content = json.dumps(blocks_lst)
        CodeHelper.write_to_file(file_path, content, mod='w')
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
    # проверяем тип авторизации
    # стартуем сессию для пользователя

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
    if current_subitem is not None:
        tmpl_vars['page_title'] += ':' + current_subitem['label']
    return render_template(AdminConf.get_root_tpl(), **tmpl_vars)


@mod.route('/<modname>' , methods=['GET'])
@requires_auth
def module_base_view(modname):
    """"""
    # требуется определить по имени url зарегистрированного модуля


@mod.route('/configure/db', methods=['GET'])
@mod.route('/db_reconfigure', methods=['GET'])
@requires_auth
def local_db_reconfigure():
    """"""
    # проверка что DB неинициализирована - flask db init
    cmd = 'flask db init'
    app_root_dir = app_api.get_app_root_dir()
    migrate_dir = os.path.join(os.path.dirname(app_root_dir), 'migrations')
    versions_dir = os.path.join(migrate_dir, 'versions')
    errors = None
    output = None
    steps = []
    is_init = False
    if os.path.exists(migrate_dir) and os.path.isdir(migrate_dir)\
        and os.path.exists(versions_dir) and os.path.isdir(versions_dir):
        """ будем считать что директория инициализирована"""
        is_init = True
    else:
        """ запускаем инициализацию """
        cmd_args = cmd.split(' ')
        run_cmd = subprocess.Popen(cmd_args)
        output, errors = run_cmd.communicate()
        is_init = True
        if errors:
            is_init = False
            return errors
    if is_init:
        scripts = [it.name for it in os.scandir(versions_dir)]
        # создаем комментарий о дате реконфигурации
        cmt = 'DB autoreconfiguration ' + AdminUtils.get_dbg_now()
        # создаем скрипт реконфигурации
        cmd = 'flask db migrate -m'
        cmd_args = cmd.split(' ')
        cmd_args.append('"' + cmt + '"')
        run_cmd = subprocess.Popen(cmd_args)
        output, errors = run_cmd.communicate()
        scripts1 = [it.name for it in os.scandir(versions_dir)]
        if errors:
            return errors
        # выполняем реконфигурацию
        cmd = 'flask db upgrade'
        if 0 < len(scripts1) - len(scripts):
            cmd_args = cmd.split(' ')
            run_cmd = subprocess.Popen(cmd_args)
            output, errors = run_cmd.communicate()
            if errors:
                return errors
            steps.insert(0, 'DB upgrade done!')
        steps.insert(0, 'Create migration scripts!')
        steps.insert(0, 'DB initialization done!')
    steps_str = ''
    if steps:
        steps_str = '<br />'.join(steps)
        steps_str = '<hr />' + steps_str
    return 'Reconfiguration complite!' + steps_str


@mod.route('/configure/navigation', methods=['GET'])
@requires_auth
def configure_navigation():
    """"""
    steps_str = ''
    """
    требуется создать основной файл для реестра блоков навигации
    
    """
    return 'Navigation configuration complite!' + steps_str


# """
@mod.route('/signin', methods=['GET', 'POST'])
@mod.route('/login', methods=['GET', 'POST'])
def login():
    # print(request.environ)
    if current_user.is_authenticated:
        # правильную страницу надо определять в настройках
        # redirect to defautl page from settings
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        # try to log in by local admin
        is_local_admin = False
        secret = form.secret.data
        if User.is_local_admin(form.username.data):
            user = User.auth_admin(form.username.data, form.secret.data)
            is_local_admin = True
        else:
            user = User.query.filter_by(login=form.username.data).first()
            portal_cfg = AdminUtils.get_portal_config()
            # если авторизовываемся во внешнем сервисе, то:
            if 'local' != portal_cfg.get('main.Auth.type'):
                # получить драйвер авторизации
                portal_auth = AdminUtils.get_auth_provider() # AuthProvider()
                # попытаться авторизоваться во внешнем сервисе
                # при успешной авторизации получить данные пользователя
                if portal_auth.login(form.username.data, secret):
                    # если такого пользователя нет, то требуется создать и выбрать заново
                    auth_user = portal_auth.get_user(form.username.data)
                    spec_key = 'password'
                    # hack - если поиск пустой а пользователь валидный и авторизовался
                    if not isinstance(auth_user, dict):
                        _t = {'name': '', 'login': '', 'email':''}
                        _t['name'] = form.username.data
                        _t['login'] = form.username.data
                        _t['email'] = form.username.data + '@company.local'
                        from hashlib import sha1
                        _t[spec_key] = ''
                        base = _t['email'] + secret + '//'
                        _t[spec_key] = sha1(base.encode()).hexdigest()
                        auth_user = _t
                    if not user:
                        new_user_data = {}
                        new_user_data['name'] = auth_user['name']
                        new_user_data['login'] = auth_user['login']
                        new_user_data[spec_key] = auth_user[spec_key]
                        new_user_data['email'] = auth_user['email']
                        new_user_data['roles'] = []
                        # print('new user')
                        try:
                            user = User(**new_user_data)
                            user.set_password(new_user_data[spec_key])
                            db.session.add(user)
                            db.session.commit()
                        except:
                            user = None
                    # пароль локального пользователя будет отличаться от введеного в форму
                    # следовательно его следует заменить на правильный!!!
                    # перезапрашиваем данные пользователя
                    secret = auth_user[spec_key]
                    user = User.query.filter_by(login=form.username.data).first()
                else:
                    user = None
        # print(user)
        if user is None or not user.check_password(secret):
                flash('Invalid username or password')
                return redirect(url_for('admin_mgt.login'))
        login_user(user, remember=form.remember_me.data)
        # добавим в лог запись об успешной авторизации пользователя
        _auth_logger = AdminUtils.get_auth_logger()
        _str = ''
        _now = AdminUtils.get_now()
        _str = '['+_now.strftime("%Y-%m-%d")+'] ['+_now.strftime("%H:%M:%S")+'] ['+form.username.data+']'+"\n"
        _auth_logger.write(form.username.data)
        # перенаправляем на требуюмую страницу
        # https://habr.com/en/post/346346/ look
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            # правильней из настроек брать URL для перенаправления на стартовую
            # redirect to defautl page from settings
            next_page = '/'
            if not app_api.check_in_registred_urls(next_page):
                next_page = url_for('admin_mgt.index')
        if is_local_admin:
            next_page = url_for('admin_mgt.index')
        return redirect(next_page)
    return render_template("/login.html", title='Авторизация', form=form,
                           page_title='Авторизация')
# """


@mod.route('/logout')
def logout():
    logout_user()
    # redirect to defautl page from settings
    return redirect('/')


@mod.route('/interfaceData', methods=['GET', 'POST'])
@mod.route('/interfaceData/', methods=['GET', 'POST'])
@requires_auth
def interface_data():
    portal_cfg = app_api.get_config_util()(AdminConf.CONFIGS_PATH)
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

    # $phpini =  ini_get_all(;
    interface['Pages'] = {
        'PortalUsers': {
            'minLoginLength': 8, # portalApp::getInstance()->getSetting('main.Info.login.minLen'),
            'minPaswdLength': 8, # portalApp::getInstance()->getSetting('main.Info.pswd.minLen'),
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


@mod.route('/PortalSettings/Configs/<config_name>', defaults={'config_name': ''}, methods=['GET'])
@requires_auth
def edit_settings_view(config_name):
    """
    Функция создает страницу редактирования ini файла
    :param config_name: имя ini файла из директории data/cfg в директории модуля
    :return: сформированный шаблон страницы
    """
    tmpl_vars = {}
    # tmpl_vars['project_name'] = 'Semantic PLM'
    tmpl_vars['title'] = 'Административный интерфейс'
    tmpl_vars['page_title'] = 'Настройки портала: ' + config_name
    tmpl_vars['page_side_title'] = 'Содержание раздела'
    work_dir = AdminConf.CONFIGS_PATH
    files_list = [fi.name for fi in os.scandir(work_dir)]
    for fi in files_list:
        lp = fi.rfind('.')
        name = fi[:lp]
        if name == config_name:
            break
    data_file = os.path.join(work_dir, fi)
    # превращаем словарь в HTML
    edit_data = AdminUtils.ini2dict(data_file)
    # первичные ключи это секции - Вопрос где хранить натменование секций????
    # вторичные ключи - имена полей
    tmpl_vars['edit_data'] = edit_data
    return render_template('config_editor.html', **tmpl_vars)

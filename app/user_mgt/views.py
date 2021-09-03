# -*- coding: utf-8 -*-

import json
import os

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from flask.views import MethodView
from flask_allows import Permission, Requirement
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app_api
from app.user_mgt.user_conf import UserConf
from app.user_mgt.models.users import db, User
from app.user_mgt.models.roles import Role
# теперь надо получить API административного модуля
admin_mod_api = None
admin_mod_api = app_api.get_mod_api('admin_mgt')

MOD_NAME = 'users'
mod = Blueprint(MOD_NAME, __name__, url_prefix=UserConf.MOD_WEB_ROOT,
                static_folder=UserConf.get_web_static_path(),
                template_folder=UserConf.get_web_tpl_path())

mod.add_app_template_global(admin_mod_api.get_root_tpl, name='admin_root_tpl')

_auth_decorator = app_api.get_auth_decorator()

#MOD_DIR = os.path.join(app.config['APP_DATA_PATH'], 'mod_' + MOD_NAME)

# надо зарегистрировать ссылку на административный интерфейс

# { Start administrative interface


@mod.route('/manage/roles', methods=['GET'])
@_auth_decorator
def roles_page():
    navi_data = []
    # navi_data = get_admin_navi('user_roles_list')

    # uq = Role.query
    # print(uq)
    return render_template("manage_roles.html", title=u"Список ролей пользователя",
                           page_title=u'Список ролей пользователя')


@mod.route('/manage', methods=['GET'])
@_auth_decorator
def users_page():
    navi_data = []
    # navi_data = get_admin_navi('users_list')

    # uq = User.query
    # print(uq)
    return render_template("manage_users.html", title=u"Список пользователей",
                           page_title=u'Список пользователей')


@mod.route('/profile', methods=['GET'])
@_auth_decorator
def home():
    app_cfg = app_api.get_app_config()
    debug_role = app_cfg.get('main.Info.debugRole')
    cur_prj = app_cfg.get('main.Info.project')
    auth_type = app_cfg.get('main.Auth.type')
    ext_adm_role = app_cfg.get('main.Info.extAdminRole')
    is_ext_admin = False
    use_debug_mode = False
    use_debug_role = False

    if g.user:
        # data_admin_role = app_cfg.get('main.DataStorage.adminRole')
        # data_oper_role = app_cfg.get('main.DataStorage.operRole')
        # if g.user.has_role(data_oper_role):
        #     """"""
        # if g.user.has_role(data_admin_role):
        #     """"""
        if g.user.has_role(debug_role):
            """"""
            use_debug_role = True
        if g.user.has_role(ext_adm_role):
            """"""
            is_ext_admin = True

    if session:
        debug_key = app_cfg.get('main.Info.debugModeSesKey')
        if debug_key in session:
            use_debug_mode = session[debug_key]

    return render_template("profile.html", user=g.user, ext_admin=is_ext_admin,
                           auth_type=auth_type, cur_project=cur_prj, has_debug_role=use_debug_role,
                           debug_mode=use_debug_mode)


@mod.route('/list', methods=['POST'])
@_auth_decorator
def users_list():
    answer = {}
    page = 1 # get the requested page
    limit = 20 # get how many rows we want to have into the grid
    sidx = 'login' # get index row - i.e. user click to sort
    sord = 'ASC' # get the direction
    search_flag = False

    if request.method == "POST":
        page = int(request.form['page'])
        limit = int(request.form['rows'])
        sidx = request.form['sidx']
        sord = request.form['sord']
        search_flag = not ('false' == request.form['_search']) # инверсия от значения

    offset = limit * page - limit
    total = User.query.count()
    data_list = []
    # '''
    if search_flag:
        q = ''
        query_condition = jqgrid_filters_to_sql(request.form['filters'])
    else:
        q = ''
        qfilter = {}
        # qfilter[User[sidx]] = 'anton'
        query_result = User.query.all()
        # print('Users.views.users_list say: query result', query_result)
    # '''
    for user in query_result:
        # print('get users list type', type(user))
        # print(user.to_dict())
        tbl_row = {"toolbar": ''}
        tbl_row['ID'] = user.id
        tbl_row['login'] = user.login
        tbl_row['email'] = user.email
        roles = [x.name for x in user.roles]
        # print(roles)
        tbl_row['roles'] = roles
        data_list.append(tbl_row)

    answer['limit'] = limit
    answer['page'] = page
    answer['rows'] = data_list
    answer['records'] = len(answer['rows'])
    answer['total'] = total

    return json.dumps(answer)


def jqgrid_filters_to_sql(filters):
    condition = ''
    # filters	{"groupOp":"AND","rules":[{"field":"name","op":"cn","data":"15-22"}]}

    return condition


@mod.route('/dialog/<type>', methods=['GET'])
@_auth_decorator
def user_dialog(type):
    template_name = 'dialog'
    if 'edit' == type: template_name = 'dialog'
    if 'view' == type: template_name = 'view_info'

    return render_template(template_name + ".html")


@mod.route('/getModuleData/', methods=['GET', 'POST'])
@_auth_decorator
def users_page_data():
    # portalApp::getInstance()->getSetting('main.Info.login.minLen'),
    # portalApp::getInstance()->getSetting('main.Info.pswd.minLen'),
    answer = {
            'minLoginLength': 8,
            'minPaswdLength': 8,
            'Errors': {
                '100':'Неизвестный идентификатор(#{id}) закладки для открытия!',
                '101':'Не заполнено обязательное поле',
                '102':'Поле "#{field}" незаполнено или имеет неверный формат или количество символов меньше минимального',
                '103':'Поле "#{field}" или его подтверждение незаполнено!',
                '104':'Поле "#{field}" незаполнено!',
                '105':'Пароль и Подтверждение пароля несовпадают!',
                '106':'Длина пароля меньше минимальной',
                '107':'Не корректный формат',
                '108':'Не верный формат точки возврата!',
                '109':'Не указан идентификатор таба для определения ключа пользователя!',
                '110':'Поле "#{field}" или его подтверждение несовпадают!',
            },
            'Msgs':{ 'del':'Вы действительно хотите удалить пользователя',
                            'chgPass':'Пароль успешно изменен!' },
            'interface':{
                'title':'Пользователи портала',
                'close':'Закрыть',
                'save':'Сохранить',
                'delete':'Удалить',
                'edit':'Редактировать',
                'list':'Список',
                'addUser':'Создать пользователя',
                'newUser':'Новый пользователь',
                'fio':'ФИО',
                'login':'Логин',
                'password':'Пароль',
                'newpassword':'Новый пароль',
                'oldpassword':'Старый пароль',
                'email':'Email',
                'roles':'Роли',
                'user':'Пользователь',
                'field':'Поле',
                'nofill':'незаполнено',
                'nofill_confirm':'или его подтверждение незаполнено',
                'nofill_mismatch':'незаполнено или имеет неверный формат или количество символов меньше минимального',
                'exportXML':'XML export',
                'table':[
                    {'sTitle': 'Действия', 'sName': 'Actions', 'mData':'Actions','sWidth':'68px', 'sClass':'row-actions', 'bSortable': False},
                    {'sTitle': 'ID', 'sName': 'ID', 'mData':'ID', 'bVisible': False, 'sClass':'usr-id', 'bSortable': False},
                    {'sTitle': 'ФИО', 'sName': 'FIO', 'mData':'FIO', 'sClass':'usr-fio'},
                    {'sTitle': 'Логин', 'sName': 'Login', 'mData':'Login', 'sClass':'usr-login'},
                    {'sTitle': 'Email', 'sName': 'Email', 'mData':'Email', 'sClass':'usr-email'},
                    {'sTitle': 'Роли', 'sName': 'Roles', 'mData':'Roles', 'sClass':'usr-roles', 'bSortable': False},
                ],
            },
            'grid':{ 'columns':[]},
            'templates':{}
    }
    answer['grid']['columns'] = [
        {'name': 'Actions', 'index': 'Actions', 'label': 'Действия', 'width': '68px', 'sortable': False},
        {'name': 'ID', 'index': 'ID', 'label': 'ID', 'hidden': True, 'width': '60px', 'sortable':False},
        {'name': 'FIO', 'index': 'FIO', 'label': 'ФИО', 'width': '60px', 'sortable': True},
        {'name': 'Login', 'index': 'Login', 'label': 'Логин', 'sortable': True},
        {'name': 'Email', 'index': 'Email', 'label': 'Email', 'sortable': True},
        {'name': 'Roles', 'index': 'Roles', 'label': 'Роли', 'sortable': False}
    ]

    return json.dumps(answer)


@mod.route('/save/', methods=['POST'])
@_auth_decorator
def save_user():
    answer = {'msg': '', 'data': None, 'state': 404}
    # {"ID":"","TYPE":"","FIO":"","Login":"","Password":"","PasswordCheck":"","Email":"","Roles":""}
    user_data = {}
    if request.method == "POST":
        user_id = 0
        if request.form['ID']:
            user_id = int(request.form['ID'])
            if 0 < user_id:
                user_data['id'] = user_id
        field = 'FIO'
        if request.form[field]:
            user_data['name'] = request.form[field]
        field = 'Login'
        if request.form[field]:
            user_data['login'] = request.form[field]
        field = 'Password'
        if request.form[field]:
            user_data['password'] = request.form[field]
        field = 'Email'
        if request.form[field]:
            user_data['email'] = request.form[field]

        # возможно надо переделать механизм приведения
        # имен элементов формы и свойств класса User
        field = 'Roles[]'
        # print(request.form.to_dict(flat=False))
        if field in request.form:
            user_data['roles'] = []
            # все значения полей под тменами полей делает списками
            # требуется если для одного поля требуется обработать несколько значений
            form_dict = request.form.to_dict(flat=False)
            for item in form_dict[field]:
                if '' == item:
                    continue
                item = User.str_to_node(item)
                user_data['roles'].append(item)
            form_dict = None

        try:
            if 0 < user_id:
                # print('Users.views.save_user say: update user info')
                user = User.query.get(user_id)
                # print('save user get by id type', type(user))
                # print('save user get by id ', user)
                # print('save user get by id as dict ', user.to_dict())
                # user.to_log('test log')
                # print('get user by ID ', user_id)
                user.name = user_data['name']
                # print('set name', user_data['name'])
                user.email = user_data['email']
                # print('set email', user_data['email'])
                user.login = user_data['login']
                # print('set login', user_data['login'])
                if 'roles' in user_data:
                    user.roles = user_data['roles']
                    # print('Users.views.save_user say: set links', user_data['roles'])
                    # print('Users.views.save_user say: links is set to object', user.roles)
                    # user.to_log('set roles links')
                if 'password' in user_data and "" != user_data['password']:
                    user.set_password(user_data['password'])
                    # print('set name', user_data['password'])
            else:
                # print('new user')
                user = User(**user_data)
                user.set_password(user_data['password'])
                db.session.add(user)
            """
            user = User(name=form.name.data, email=form.email.data, \
                        password=generate_password_hash(form.password.data))
            # """
            # Insert the record in our database and commit it
            # print('session commit')
            db.session.commit()
            # теперь преобразумем ссылки в словари
            if 0 < len(user_data['roles']):
                t = []
                for link in user_data['roles']:
                    t.append(link.to_dict())
                user_data['roles'] = None
                user_data['roles'] = t
            answer['data'] = user_data
            answer['data']['password'] = ''
            answer['state'] = 200
        except Exception as e:
            answer['msg'] = 'Can not save user: ' + str(e)
            answer['Msg'] = 'Can not save user: ' + str(e)
            answer['state'] = 500
    return json.dumps(answer)


@mod.route('/changePass/', methods=['POST'])
@_auth_decorator
def change_user_secret():
    """"""
    answer = {'msg': '', 'data': None, 'state': 404}
    if request.method == "POST":
        """"""
        app_cfg = app_api.get_app_config()
        auth_type = app_cfg.get('main.Auth.type')
        answer['msg'] = 'Метод аутентификации на портале не позволяет менять пароль'
        if 'local' == auth_type:
            """"""
            user_id = int(request.form['ID'])
            user_data = {}
            if 0 < user_id:
                answer['state'] = 500
                answer['msg'] = 'Ошибка при попытке установить новый пароль пользователя'
                try:
                    user = User.query.get(int(user_id))
                except Exception as ex:
                    answer['msg'] = 'Get user exception:' + str(ex)
                field = 'NewPassword'
                answer['msg'] = 'Не указан новый пароль'
                if field in request.form and "" != request.form[field]:
                    """"""
                    answer['msg'] = 'Не верный пароль'
                    if user.check_password(request.form['PasswordOld']):
                        """"""
                        answer['msg'] = 'Ошибка при попытке установить новый пароль пользователя'
                        user_data['password'] = request.form[field]
                if 'password' in user_data and '' != user_data['password']:
                    try:
                        user.set_password(user_data['password'])
                        db.session.commit()
                        answer['state'] = 200
                        answer['msg'] = ''
                    except Exception as ex:
                        answer['msg'] = 'Не удалось назначить новый пароль!'
                        answer['state'] = 500
    return json.dumps(answer)


@mod.route('/toggleDebugMode/<flag>', methods=['GET'])
@_auth_decorator
def toggle_debug_mode(flag):
    """"""
    answer = {'msg': '', 'data': None, 'state': 404}
    if request.method == "GET":
        """"""
        app_cfg = app_api.get_app_config()
        use_debug_role = False
        debug_role = app_cfg.get('main.Info.debugRole')
        if g.user:
            if g.user.has_role(debug_role):
                """"""
                use_debug_role = True
        if session and use_debug_role:
            debug_key = app_cfg.get('main.Info.debugModeSesKey')
            session[debug_key] = int(flag)
            answer['state'] = 200
            answer['msg'] = ''
    return json.dumps(answer)


@mod.route('/delete/<uid>', methods=['GET', 'POST'])
@_auth_decorator
def remove_user(uid):
    answer = {'msg': '', 'data': None, 'state': 404}
    if "" != uid:
        user_id = int(uid)
    if "" == uid and request.method == "POST":
        user_id = request.form['ID']
    """
    """
    answer['msg'] = 'Не удалось удалить пользователя с идентификатором  "%s"!' % user_id
    answer['Msg'] = 'Не удалось удалить пользователя с идентификатором  "%s"!' % user_id
    if 0 < user_id:
        try:
            user = User.query.get(int(user_id))
            # db.session.delete(user)
            user.deleteme()
            db.session.commit()
            answer['msg'] = 'Пользователь id="%s" удален!' % user_id
            answer['Msg'] = 'Пользователь id="%s" удален!' % user_id
            answer['State'] = 200
        except:
            answer['msg'] = 'Не удалось удалить пользователя с идентификатором  "%s"!' % user_id
            answer['Msg'] = 'Не удалось удалить пользователя с идентификатором  "%s"!' % user_id
    return json.dumps(answer)


@mod.route('/getInfo/', methods=['POST'])
@_auth_decorator
def user_info():
    answer = {'msg': '', 'data': None, 'state': 404}
    if request.method == "POST":
        # get post data on MultiDict in werkzeug(Flask) docs
        user_id = int(request.form['ID'])
        if 0 < user_id:
            try:
                user = User.query.get(user_id)
                answer['data'] = {'id': user.id, 'login': user.login, 'name': user.name, 'email': user.email,
                                  'roles': []}
                if 0 < len(user.roles):
                    answer['data']['roles'] = [x.to_dict() for x in user.roles]
                answer['State'] = 200
            except:
                answer['msg'] = 'Пользователь с идентификатором "%s" не найден!' % user_id
                answer['Msg'] = 'Пользователь с идентификатором "%s" не найден!' % user_id

    return json.dumps(answer)


@mod.route('/removeSelection', methods=['POST'])
@_auth_decorator
def remove_users():
    answer = {'msg': '', 'data': None, 'state': 404}
    return json.dumps(answer)

# { roles block


@mod.route('/roles/getList', methods=['POST'])
@_auth_decorator
def roles_list():
    answer = {'msg': '', 'data': None, 'state': 404}
    answer['data'] = []
    try:
        roles = Role.query.all()
        if 0 < len(roles):
            for role in roles:
                n = {'id': '', 'name': '', 'code': '', 'descr': ''}
                n['id'] = role.id
                n['name'] = role.name
                n['code'] = role.code
                n['descr'] = role.descr
                answer['data'].append(n)
        answer['state'] = 200;
    except:
        answer['state'] = 500
        answer['msg'] = 'Не удалось получить список ролей!'
        answer['Msg'] = 'Не удалось получить список ролей!'
    return json.dumps(answer)


@mod.route('/roles/getInfo', methods=['POST'])
@_auth_decorator
def role_info():
    answer = {'msg': '', 'data': None, 'state': 404}
    role_id = int(request.form.get('ID'))
    try:
        role = Role.query.get(role_id)
        answer['data'] = {'name': role.name, 'ID': role.id, 'Code': role.code, 'descr': role.descr,
                          'Pages': [], 'Users': []}
        users = role.get_nodes_related_to_me()
        # print(role)
        # print(users)
        answer['data']['myLinks'] = users
        answer['state'] = 200
    except:
        answer['state'] = 500
        answer['msg'] = 'Не удалось получить роль с идентификатором "%s"' % role_id
        answer['Msg'] = 'Не удалось получить роль с идентификатором "%s"' % role_id
    return json.dumps(answer)


@mod.route('/roles/delete', methods=['GET', 'POST'])
@_auth_decorator
def remove_role():
    answer = {'msg': '', 'data': None, 'state': 404}
    role_id = 0
    role_id = int(request.form['ID'])
    try:
        if 0 < role_id:
            # Update the record in our database
            role = Role.query.get(role_id)
            db.session.delete(role)
            # and commit it
            db.session.commit()
            answer['state'] = 200
    except Exception as e:
        answer['msg'] = 'Can not save role: ' + str(e)
        answer['Msg'] = 'Can not save role: ' + str(e)
        answer['state'] = 500
    return json.dumps(answer)


@mod.route('/roles/save', methods=['POST'])
@_auth_decorator
def save_role():
    answer = {'msg': '', 'data': None, 'state': 404}
    role_data = {}
    role_id = 0
    role_id = int(request.form['ID'])
    if 0 < role_id:
        role_data['id'] = role_id
    role_data['name'] = request.form['Name']
    role_data['code'] = request.form['Code']
    role_data['descr'] = ''
    if request.form['Pages[]']:
        # разбираемся с сылками на страницы
        k = 1
    if request.form['Users[]']:
        # разбираемся с сылками на пользователей
        j = 2
    try:
        if 0 < role_id:
            # Update the record in our database
            role = Role.query.get(role_id)
            role.name = role_data['name']
            role.code = role_data['code']
            role.descr = role_data['descr']
        else:
            # Insert the record in our database
            role = Role(**role_data)
            db.session.add(role)
        # and commit it
        db.session.commit()
        # теперь надо добавить id
        role_data['id'] = role.id
        answer['data'] = role_data
        answer['state'] = 200
    except Exception as e:
        answer['msg'] = 'Can not save role: ' + str(e)
        answer['Msg'] = 'Can not save role: ' + str(e)
        answer['state'] = 500
    return json.dumps(answer)
# } roles block

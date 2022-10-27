# -*- coding: utf-8 -*-
import os

from flask import Blueprint, request, redirect, url_for
from app import app, app_api
from flask_login import login_required

from app.admin_mgt.mod_api import ModApi

from app.query_mgt.query import Query

MOD_NAME = 'query'

mod = Blueprint(MOD_NAME, __name__, url_prefix='/portal/manager', template_folder="templates", static_folder="static")

mod.add_app_template_global(app_api.get_app_root_tpl, name='app_root_tpl')
mod.add_app_template_global(ModApi.get_root_tpl, name='admin_root_tpl')

module_name = os.path.basename(mod.root_path)

_auth_decorator = app_api.get_auth_decorator()

@mod.route('/')
@_auth_decorator
def sparqt_manager(blueprint_mod_name = MOD_NAME, module_name = module_name):
	return app_api.render_page('/query_mgt/files.html', files = Query(module_name).get_list_sparqt(), module = blueprint_mod_name)


@mod.route('/file/<file>', methods=["GET", "POST"])
@mod.route('/file/', methods=["GET", "POST"])
@_auth_decorator
def sparqt_file(file = '', blueprint_mod_name = MOD_NAME, module_name = module_name):
	if request.method == 'GET':
		_can_remove = False
		_can_remove = Query(module_name).can_remove(file)
		return app_api.render_page('/query_mgt/templates.html', templates = Query(module_name).get_templates_names_sparqt(file), file = file,
								   module = blueprint_mod_name, can_delete=_can_remove)
	elif request.method == 'POST':
		if 'save' in request.form:
			if request.form['file'] and not os.path.exists(Query(module_name).get_full_path_sparqt(request.form['file'])):
				Query(module_name).edit_file_object_sparqt(request.form['file'], {})
			else:
				Query(module_name).logger.error("Can't save sparqt file")

		elif 'delete' in request.form:
			Query(module_name).delete_file_object_sparqt(request.form['file'])
			
		return redirect(url_for(blueprint_mod_name + '.sparqt_manager'))



@mod.route('/<file>/template/<template>', methods=["GET", "POST"])
@mod.route('/<file>/template/', methods=["GET", "POST"])
@_auth_decorator
def sparqt_template(file, template = '', blueprint_mod_name = MOD_NAME, module_name = module_name):
	if 'save' in request.form:
		if request.form['template']:
			if (template == request.form['template']) or (not template and request.form['template'] not in Query(module_name).get_templates_names_sparqt(file)):
				# согласно новой концепции сохранять редактируемый файл требуется в директорию общего конфига
				if request.form['txt']:
					Query(module_name).edit_template_sparqt(file, request.form['template'], [request.form['cmt'], request.form['vars'], request.form['txt']])
			else:
				Query(module_name).logger.error("Can't save sparqt template \"" + request.form['template'] + "\" in file \"" + file + "\"")

		else:
			Query(module_name).logger.error("Can't save sparqt template in file \"" + file + "\"")
		return redirect(url_for(blueprint_mod_name + '.sparqt_file', file = file))

	elif 'delete' in request.form:
		Query(module_name).delete_template_sparqt(file, request.form['template'])
		return redirect(url_for(blueprint_mod_name + '.sparqt_file', file = file))

	else:
		cmt, var, txt = Query(module_name).get_template_sparqt(file, template)
		_can_remove = False
		_can_remove = Query(module_name).can_remove_template(file, template)
		return app_api.render_page('/query_mgt/edit.html', file = file, template = template, cmt = cmt, vars = var, txt = txt,
								   module = blueprint_mod_name, can_delete=_can_remove)




@mod.route('/logs', methods=['GET'])
@_auth_decorator
def showlogs():
    logdir = app_api.get_logs_path()
    result = ""
    try:
        with open( os.path.join(logdir, "Query.log"), "r" ) as f:
            content = f.read()
            result = content.replace("\n","<br>")
            f.close()
    except:
        pass

    return app_api.render_page('/query_mgt/logs.html',result = result)





# Чтобы использовать в другом модуле нужно импортировать апи
# query_mod_api = app_api.get_mod_api('query_mgt')
# потом вызываем функцию create_sparqt_manager с заданными параметрами 
# Пример - query_mod_api.create_sparqt_manager("my_custom_sparqt", mod, MOD_NAME)
# В dublin.ttl добавляем <SUBJECT> <http://splm.portal.web/osplm#hasPathForSPARQLquery> "<DIR_NAME>"^^<http://www.w3.org/2001/XMLSchema#string> .
# Где вместо <SUBJECT> - uri модуля, <DIR_NAME> - папка от корня модуля где будут хранится шаблоны
def create_sparqt_manager(URL, blueprint_mod):
	"""
	Метод создает три функции-маршрута для данного модуля: sparqt_manager, sparqt_file, sparqt_template

	URL - наш url по которому будет SPARQTManager
	blueprint_mod - экземпляр класса blueprint в файле views текущего модуля
	"""
	url_file = '/' + URL + '_file/'
	url_template = '/' + URL + '_template/'

	# имя blueprint
	blueprint_mod_name = blueprint_mod.name
	# имя папки модуля
	module_name = os.path.basename(blueprint_mod.root_path)

	from app.query_mgt import views as query_manager

	@blueprint_mod.route('/' + URL, methods=['GET', 'POST'])
	# @login_required
	def sparqt_manager():
		return query_manager.sparqt_manager(blueprint_mod_name, module_name)


	@blueprint_mod.route(url_file + '<file>', methods=["GET", "POST"])
	@blueprint_mod.route(url_file, methods=["GET", "POST"])
	# @login_required
	def sparqt_file(file = ''):
		return query_manager.sparqt_file(file, blueprint_mod_name, module_name)


	@blueprint_mod.route('/<file>/' + url_template + '<template>', methods=["GET", "POST"])
	@blueprint_mod.route('/<file>/' + url_template, methods=["GET", "POST"])
	# @login_required
	def sparqt_template(file, template = ''):
		return query_manager.sparqt_template(file, template, blueprint_mod_name, module_name)

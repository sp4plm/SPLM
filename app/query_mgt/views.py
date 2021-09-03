# -*- coding: utf-8 -*-
import os

from flask import Blueprint, render_template, request, redirect, url_for
from app import app, app_api
from flask_login import login_required

from app.admin_mgt.mod_api import ModApi

from app.query_mgt.query import Query

MOD_NAME = 'query'


mod = Blueprint(MOD_NAME, __name__, url_prefix='/portal/manager', template_folder="templates", static_folder="static")

mod.add_app_template_global(app_api.get_app_root_tpl, name='app_root_tpl')
mod.add_app_template_global(ModApi.get_root_tpl, name='admin_root_tpl')



@mod.route('/')
#@login_required
def manager():
	return render_template('files.html', files = Query.get_list_sparqt())


@mod.route('/file/<file>', methods=["GET", "POST"])
@mod.route('/file/', methods=["GET", "POST"])
#@login_required
def file(file = ''):
	if request.method == 'GET':
		return render_template('templates.html', templates = Query.get_templates_names_sparqt(file), file = file)
	elif request.method == 'POST':
		if 'save' in request.form:
			if request.form['file'] and not os.path.exists(Query.get_full_path_sparqt(request.form['file'])):
				Query.edit_file_object_sparqt(request.form['file'], {})
			else:
				print("!")

		elif 'delete' in request.form:
			Query.delete_file_object_sparqt(request.form['file'])
			
		return redirect(url_for('query.manager'))



@mod.route('/<file>/template/<template>', methods=["GET", "POST"])
@mod.route('/<file>/template/', methods=["GET", "POST"])
#@login_required
def template(file, template = ''):
	if 'save' in request.form:
		if request.form['template']:
			if (template == request.form['template']) or (not template and request.form['template'] not in Query.get_templates_names_sparqt(file)):
				Query.edit_template_sparqt(file, request.form['template'], [request.form['cmt'], request.form['vars'], request.form['txt']])
			else:
				print("!!!")
		else:
			print("!!")
		return redirect(url_for('query.file', file = file))

	elif 'delete' in request.form:
		Query.delete_template_sparqt(file, request.form['template'])
		return redirect(url_for('query.file', file = file))

	else:
		cmt, var, txt = Query.get_template_sparqt(file, template)
		return render_template('edit.html', file = file, template = template, cmt = cmt, vars = var, txt = txt)

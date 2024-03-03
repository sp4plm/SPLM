# -*- coding: utf-8 -*-
import os

from flask import Blueprint, request, redirect, url_for, jsonify
from app import app_api

from app.admin_mgt.mod_api import ModApi

from app.query_mgt.query import Query

import random
import string

from .mod_api import ModApi as QueryModApi

MOD_NAME = 'query'

mod = Blueprint(MOD_NAME, __name__, url_prefix='/query', template_folder="templates", static_folder="static")

mod.add_app_template_global(app_api.get_app_root_tpl, name='app_root_tpl')
mod.add_app_template_global(ModApi.get_root_tpl, name='admin_root_tpl')

module_name = os.path.basename(mod.root_path)

_auth_decorator = app_api.get_auth_decorator()

# Создаем редактор sparqt файлов для модуля с урлом "/sparqt"
# Место хранения sparqt-файлов описано в dublin.ttl
QueryModApi.create_sparqt_manager("/sparqt", mod)


@mod.route('/test_query', methods=['POST'])
@_auth_decorator
def test_query():
	"""
	Метод позволяет проверить сохраняемый sparqt запрос на соответствие синтаксису.
	Запрос отправляется к хранилищу.

	:return: request_code 
	"""
	onto = "onto"
	# имитируем подстановку переменных в запрос
	# где PREF = URI онтологии onto
	PREF = ""
	_onto_api = app_api.get_mod_api('onto_mgt')
	prefixes = _onto_api.get_all_prefixes()
	if onto in prefixes:
		PREF = prefixes[onto]
	params = {"PREF" : PREF}
	# получаем переменные c ajax
	_txt = request.values['txt']
	_vars =  request.values['vars']

	# из переменных собираем запрос, также как в Query()
	var_s = _vars.split(",")
	dict_var_s = {}
	if _vars:
		for var in var_s:
			var = var.split("=")
			dict_var_s[var[0]] = {"mark":"#{" + var[0] + "}","default": var[1]}

	for item in dict_var_s:
		pattern = dict_var_s[item]['mark']
		if item in params and params[item] is not None:
			_txt = _txt.replace(pattern, params[item])
		elif 'default' in dict_var_s[item] and dict_var_s[item]['default']:
			_txt = _txt.replace(pattern, dict_var_s[item]['default'])
		else:
			_txt = _txt.replace(pattern, '?' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15)))
	_query = _txt

	result = Query().query(_query)
	if isinstance(result, list):
		return jsonify({}), 200
	else:
		return jsonify({}), 400

@mod.route('/logs', methods=['GET'])
@_auth_decorator
def showlogs():
	"""
	Метод отображает содержимое Query.log

	:return: html-страница
	"""
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

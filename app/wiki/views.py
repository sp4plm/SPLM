# -*- coding: utf-8 -*-
import os

from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required

from app import app, app_api

MOD_NAME = 'wiki'
mod = Blueprint(MOD_NAME, __name__, url_prefix='/' + MOD_NAME, template_folder="templates")

from app.admin_mgt.mod_api import ModApi

mod.add_app_template_global(app_api.get_app_root_tpl, name='app_root_tpl')
mod.add_app_template_global(ModApi.get_root_tpl, name='admin_root_tpl')

from app.wiki.page import *
import markdown2

import re
from urllib.parse import urlparse

from flask_login import current_user

@mod.route('/', strict_slashes=False)
#@login_required
def wiki():
	'''
	Метод возвращает список доступных wiki страниц
	:return:
	'''
	return render_template('pages.html', pages = get_list_pages())


@mod.route('/page_id/<page_id>',  methods=["GET", "POST"], strict_slashes=False)
@mod.route('/page_id/',  methods=["GET", "POST"], strict_slashes=False)
#@login_required
def page(page_id = ""):
	'''
	Единный метод crud модели для page
	:param page_id:
	:return:
	'''
	if request.method == 'GET':
		if request.args.get("do") == "edit":
			return render_template('page_edit.html', page_id = page_id, page = get_page(page_id))
		if not page_id:
			return render_template('page_edit.html', page_id = '', page = '')
		return render_template('page.html', page = compile_wiki(get_page(page_id)))

	elif request.method == 'POST':
		if 'save' in request.form:
			# user_id = current_user.get_id()
			# print(user_id)
			edit_page(request.form['page_id'], request.form['page'])
		elif 'delete' in request.form:
			delete_page(page_id)
		return redirect(url_for('wiki.wiki'))



def compile_wiki(text):
	'''
	Метод компилирует wiki код в html
	:param text:
	:return:
	'''

	# компилируем ссылки
	url_pattern = r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"
	for url in re.findall(url_pattern, text):
		text = re.sub(url, urlparse(url).path, text)

	compile_text = markdown2.markdown(text)
	return compile_text


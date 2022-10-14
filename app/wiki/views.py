# -*- coding: utf-8 -*-
import os

from flask import Blueprint, request, redirect, url_for
from flask_login import login_required

from app import app, app_api

MOD_NAME = 'wiki'
url_prefix = '/' + MOD_NAME
mod = Blueprint(MOD_NAME, __name__, url_prefix='/', template_folder="templates")

from app.admin_mgt.mod_api import ModApi

mod.add_app_template_global(app_api.get_app_root_tpl, name='app_root_tpl')
mod.add_app_template_global(ModApi.get_root_tpl, name='admin_root_tpl')

from app.wiki.page import *
import markdown2

import re
from urllib.parse import urlparse

from flask_login import current_user

from .prompt import _help

_auth_decorator = app_api.get_auth_decorator()

@mod.route(url_prefix, strict_slashes=False)
@_auth_decorator
def wiki():
	'''
	Метод возвращает список доступных wiki страниц
	:return:
	'''
	return app_api.render_page('pages.html', pages = get_list_pages())


@mod.route(url_prefix + '/page_id/<page_id>',  methods=["GET", "POST"], strict_slashes=False)
@mod.route(url_prefix + '/page_id/',  methods=["GET", "POST"], strict_slashes=False)
@_auth_decorator
def page(page_id = ""):
	'''
	Единный метод crud модели для page
	:param page_id:
	:return:
	'''
	if request.method == 'GET':
		if request.args.get("do") == "edit":
			page_data = get_page_data(page_id)
			title = page_data['title'] if 'title' in page_data else ""
			return app_api.render_page('page_edit.html', page_id = page_id, page = page_data['text'], is_navigation = page_data['is_navigation'], page_title = title, help = _help())
		if not page_id:
			return app_api.render_page('page_edit.html', page_id = '', page = '', is_navigation = '', page_title = '', help = _help())

		return redirect(url_for('wiki.wiki'))

	elif request.method == 'POST':
		if 'save' in request.form:
			# user_id = current_user.get_id()
			is_navigation = request.form['is_navigation'] if 'is_navigation' in request.form and request.form['is_navigation'] else '0'
			values = {'text' : request.form['page'], "is_navigation" : is_navigation, 'title' : request.form['page_title']}
			edit_page(request.form['page_id'], values)
		elif 'delete' in request.form:
			delete_page(page_id)
		return redirect(url_for('wiki.wiki'))



@mod.route('/wiki_page_id/<page_id>',  methods=["GET"], strict_slashes=False)
@_auth_decorator
def show_page(page_id = ""):
	'''
	Метод отдает wiki страницу на просмотр
	:param page_id:
	:return:
	'''
	if request.method == 'GET':
		page = get_page_data(page_id)
		title = page['title'] if 'title' in page else ""
		compile_text = compile_wiki(page['text'], title)
		is_toc = bool(int(page['is_navigation']))
		toc = create_toc(compile_text) if is_toc else ""

		return app_api.render_page('page.html', page = compile_text, is_navigation = is_toc, toc = toc, title = title)



def compile_wiki(text, title):
	'''
	Метод компилирует wiki код в html
	:param text:
	:return:
	'''

	# компилируем ссылки
	# url_pattern = r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"
	# for url in re.findall(url_pattern, text):
	# 	text = re.sub(url, urlparse(url).path, text)

	compile_text = markdown2.markdown(text)
	compile_text = "<h1>" + title + "</h1>" + compile_text
	return compile_text


def create_toc(text):
	_headers = re.findall(r'<h[2-6]>(.+)</h\d>', text)

	toc = '<ul class="page_toc">' + ''.join(['<li><a href="' + '#' + '">' + name + '</a></li>' for name in _headers]) + '</ul>'
	return toc



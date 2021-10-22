# -*- coding: utf-8 -*-
"""
Модуль предназначен для предоставление функциональности текстового поиска
"""

import os
import json

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug.utils import secure_filename
from app import app
from werkzeug.urls import url_parse
from flask_login import login_required

from app.utilites.code_helper import CodeHelper
from app.utilites.some_config import SomeConfig
from app.search_mgt.portal_search import PortalSearch

from app.search_mgt.search_conf import SearchConf

MOD_NAME = SearchConf.MOD_NAME
mod = Blueprint(MOD_NAME, __name__, url_prefix='/' + MOD_NAME, template_folder=SearchConf.get_mod_tpl_path(), static_folder=SearchConf.get_mod_static_path())

MOD_DATA_PATH = SearchConf.get_mod_data_path()
if not os.path.exists(MOD_DATA_PATH):
    os.mkdir(MOD_DATA_PATH)


@mod.route('' , methods=['POST', 'GET'], strict_slashes=False)
@login_required
def search():
    tmpl_vars = {}
    search_obj = PortalSearch()
    uname = 'anonymous'

    if g.user:
        uname = g.user.login
    search_obj.set_current_user(uname)
    search_obj.read_request_args(request)

    tmpl_vars = search_obj.run()
    tmpl_vars['title'] = "Поиск по данным портала"
    tmpl_vars['page_title'] = "Результаты поиска"
    tmpl_vars['base_url'] = url_for('search_mgt.search', **tmpl_vars['paging_vars'])
    tmpl_vars['request_args'] = request.args

    return render_template("/search.html", **tmpl_vars)


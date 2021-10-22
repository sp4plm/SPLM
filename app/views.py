# -*- coding: utf-8 -*-

from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from app import app_api

mod = Blueprint('app_views', __name__, url_prefix='')

# теперь надо получить API административного модуля
admin_mod_api = None
admin_mod_api = app_api.get_mod_api('admin_mgt')


_auth_decorator = app_api.get_auth_decorator()


@mod.route('/')
@_auth_decorator
def portal_root_view():
    tmpl_vars = {}
    tmpl_vars['title'] = 'Главная страница портала'
    tmpl_vars['page_title'] = ''
    tmpl_vars['page_side_title'] = ''
    tmpl_vars['navi_block'] = {}

    tpl_name = app_api.get_app_root_tpl()

    return render_template(tpl_name, **tmpl_vars)

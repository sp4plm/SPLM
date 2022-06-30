# -*- coding: utf-8 -*-

from flask import Blueprint, request, flash, g, session, redirect, url_for
from app import app_api
from app.utilites.portal_navi import PortalNavi

mod = Blueprint('app_views', __name__, url_prefix='')

# теперь надо получить API административного модуля
admin_mod_api = None
admin_mod_api = app_api.get_mod_api('admin_mgt')


_auth_decorator = app_api.get_auth_decorator()


@mod.route('/')
@_auth_decorator
def portal_root_view():
    # _mod_manager = app_api.get_mod_manager()
    # _start_url = _mod_manager.get_start_url()
    _start_url = PortalNavi.get_start_url()
    if '/' != _start_url:
        return redirect(_start_url)
    tmpl_vars = {}
    tmpl_vars['title'] = 'Главная страница портала'
    tmpl_vars['page_title'] = ''
    tmpl_vars['page_side_title'] = ''
    tmpl_vars['navi_block'] = {}

    tpl_name = app_api.get_app_root_tpl()
    tpl_name = PortalNavi.get_start_tpl()
    return app_api.render_page(tpl_name, **tmpl_vars)

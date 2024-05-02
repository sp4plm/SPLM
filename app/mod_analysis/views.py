# -*- coding: utf-8 -*-

import os

import plotly.utils
from flask import Blueprint, request, flash, g, session, redirect, url_for
from app.app_api import tsc_query
from app import app_api
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import json
from numpy import nan

onto_mod_api = app_api.get_mod_api('onto_mgt')
qry_mod_api = app_api.get_mod_api('query_mgt')

url_prefix='/analysis'
MOD_NAME = 'analysis'
mod = Blueprint(MOD_NAME, __name__, url_prefix='/',
                static_folder=os.path.join(os.path.dirname(__file__),'static'),
                static_url_path='analysis',
                template_folder=os.path.join(os.path.dirname(__file__),'templates'))

_auth_decorator = app_api.get_auth_decorator()

@mod.route(url_prefix)
@_auth_decorator
def startPage():

    page_path = [{'href': 'analysis', 'label' : 'Аналитика'}]
    pref_unquote = "http://www.co-ode.org/ontologies/pizza/pizza.owl#"

    query_1 = tsc_query( 'mod_analysis.analysis.attributes', {'PREF': pref_unquote } )
    query_2 = tsc_query( 'mod_analysis.analysis.toppings', {'PREF': pref_unquote } )
    query_3 = tsc_query( 'mod_analysis.analysis.hierarchy', {'PREF': pref_unquote } )

    df = pd.DataFrame( query_1 )
    df2 = pd.DataFrame( query_2 )
    df4 = pd.DataFrame( query_3 )
    df[['price', 'size']] = df[['price', 'size']].apply( pd.to_numeric )
    df.columns = ['Имя','Цена','Размер']

    df4[['count']] = df4[['count']].apply( pd.to_numeric )
    df4 = df4.replace( r'^\s*$', nan, regex=True )

    fig1 = px.bar(df, x="Имя", y="Цена", text_auto=True)
    fig2 = px.bar(df, x="Имя", y="Размер", text_auto=True)
    fig3 = px.pie(df2, values="cnt", names="topping", hole=.2)
    fig3.layout.height = 600
    fig4 = px.sunburst(df4, path=['short_cls', 'short_cls2', 'short_cls3'], values='count')
    fig4.layout.height = 800

    fig1_json = json.dumps(fig1,cls=plotly.utils.PlotlyJSONEncoder)
    fig2_json = json.dumps(fig2,cls=plotly.utils.PlotlyJSONEncoder)
    fig3_json = json.dumps(fig3,cls=plotly.utils.PlotlyJSONEncoder)
    fig4_json = json.dumps(fig4,cls=plotly.utils.PlotlyJSONEncoder)

    fig1_js = """
    <script>
        (function($){
            if(typeof void null!==typeof Plotly){
            Plotly.newPlot('plt_bar1',%s);
            }
        })(jQuery);
    </script>
    """ % fig1_json

    fig2_js = """
    <script>
        (function($){
            if(typeof void null!==typeof Plotly){
            Plotly.newPlot('plt_bar2',%s);
            }
        })(jQuery);
    </script>
    """ % fig2_json

    fig3_js = """
    <script>
        (function($){
            if(typeof void null!==typeof Plotly){
            Plotly.newPlot('plt_pie3',%s);
            }
        })(jQuery);
    </script>
    """ % fig3_json

    fig4_js = """
    <script>
        (function($){
            if(typeof void null!==typeof Plotly){
            Plotly.newPlot('plt_sun4',%s);
            }
        })(jQuery);
    </script>
    """ % fig4_json

    return app_api.render_page(mod.name + "/index.html",
                               heading = "Графические отчеты",
                               fig1=fig1_js,
                               fig2=fig2_js,
                               fig3=fig3_js,
                               fig4=fig4_js,
                               page_path=page_path)
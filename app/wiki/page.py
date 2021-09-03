# -*- coding: utf-8 -*-
import os
import json
import multiline
from app import app
from flask import url_for

WIKI_JSON = os.path.join(app.config['APP_ROOT'], "app", "wiki", "data", "pages.json")

def get_data():
    '''
    Метод возвращает содержимое файла WIKI_JSON
    :return: data
    '''
    with open(WIKI_JSON, "r", encoding="utf-8") as f:
        data = multiline.load(f, multiline=True)

    return data


def edit_data(pages):
    '''
    Метод кладет значение pages в WIKI_JSON
    :param pages:
    '''
    with open(WIKI_JSON, "w", encoding="utf-8") as f:
        json_text = json.dumps(pages, indent='\t', ensure_ascii=False)
        json_text = json_text.replace('\\n', '\n').replace('\\r', '')
        f.write(json_text)



def get_pages():
    '''
    Метод возвращает словарь типа {page_id : page_url, ..... }
    :return: pages
    '''
    pages = get_data()
    pages = {key : url_for('wiki.page', page_id = key) for key in list(pages.keys())}
    return pages


def get_pages_info():
    '''
    Метод возвращает словарь типа {page_url : page_title, ..... }
    :return: pages
    '''
    pages = get_data()
    pages = {url_for('wiki.page', page_id = key) : pages[key]['title'] if 'title' in pages[key] else key for key in list(pages.keys())}
    return pages


def get_list_pages():
    '''
    Метод возвращает список page_id
    :return: pages
    '''
    pages = get_data()
    pages = list(pages.keys())
    pages.sort()
    return pages


def get_page(page_id):
    '''
    Метод возвращает разметку text для страницы page_id
    :param page_id:
    :return: text
    '''
    pages = get_data()
    return pages[page_id]['text']


def edit_page(page_id, text):
    '''
    Метод редактирует разметку text для страницы page_id
    :param page_id:
    :param text:
    '''
    pages = get_data()
    try:
        if page_id not in pages:
            pages[page_id] = {}
        pages[page_id]['text'] = text
    except:
        pass
    edit_data(pages)


def delete_page(page_id):
    '''
    Метод удаляет страницу page_id
    :param page_id:
    '''
    pages = get_data()
    try:
        pages.pop(page_id)
    except:
        pass
    edit_data(pages)



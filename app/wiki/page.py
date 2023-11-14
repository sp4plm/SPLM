# -*- coding: utf-8 -*-
import os
import json
import multiline
from app import app
from flask import url_for


MODULE_FOLDER = os.path.basename(os.path.dirname(os.path.abspath(__file__)))

# создаем папку в app/data
data_folder = os.path.join(app.config['APP_DATA_PATH'], MODULE_FOLDER)
if not os.path.exists(data_folder):
    try: os.mkdir(data_folder)
    except: pass

# создаем файл pages.json
WIKI_JSON = os.path.join(data_folder, "pages.json")
if not os.path.exists(WIKI_JSON):
    with open(WIKI_JSON, "w", encoding="utf-8") as f:
        f.write("{}")


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
    pages_keys = list(pages.keys())
    pages_keys.sort()

    result = [{'id' : page, 'title' : pages[page]['title'] if 'title' in pages[page] else ""} for page in pages_keys]
    return result


def get_page_data(page_id):
    '''
    Метод возвращает данные для страницы page_id
    :param page_id:
    :return: text
    '''
    pages = get_data()
    return pages[page_id]


def edit_page(page_id, data):
    '''
    Метод редактирует данные data для страницы page_id
    :param page_id:
    :param data:
    '''
    pages = get_data()
    try:
        if page_id not in pages:
            pages[page_id] = {}
        for item in data:
            pages[page_id][item] = data[item]    
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



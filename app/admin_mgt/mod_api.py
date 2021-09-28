# -*- coding: utf-8 -*-
import os

from app.admin_mgt.admin_conf import AdminConf
from app.admin_mgt.models.node_object import NodeObject
from app.admin_mgt.models.user import EmbeddedUser
from app.admin_mgt.models.links import Link
from app.admin_mgt.admin_utils import AdminUtils


class ModApi(AdminConf):
    _class_file = __file__
    _debug_name = 'AdminModApi'

    @staticmethod
    def get_base_model():
        # очень странное поведение:
        # если раскоментировать последующие строки - проект незапустится не смотря на импорт
        # возникает ошибка reference before assigned
        # if 'NodeObject' not in globals():
        #     class NodeObject:
        #         __abstract__ = True
        #         _links={}

        return NodeObject

    @staticmethod
    def get_embedded_user():
        """
        Функция возвращает класс встроенного пользователя
        :return:
        """
        return EmbeddedUser

    @staticmethod
    def get_link_object():
        """
        Функция возвращает класс для организации связей в базе данных
        :return:
        """
        return Link

    @staticmethod
    def get_app_root_tpl():
        """
        Тестовый метод для заглушки корневого шаблона приложения
        :return: string
        """
        return '_test_base.html'

    @staticmethod
    def get_root_tpl():
        pth = ''
        # pth += AdminConf.MOD_NAME
        # pth += os.path.sep
        # pth += os.path.basename(AdminConf.get_web_tpl_path())
        # pth += os.path.sep
        pth += AdminConf.get_root_tpl()
        return pth

    @staticmethod
    def get_config_path():
        pth = ''
        if os.path.exists(AdminConf.CONFIGS_PATH):
            pth = AdminConf.CONFIGS_PATH
        else:
            pth = os.path.join(AdminConf.SELF_PATH, 'defaults', 'cfg')
        return pth

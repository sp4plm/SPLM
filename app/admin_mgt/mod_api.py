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
        """
        Метод возвращает базовый класс для моделей

        :return: класс NodeObject
        :rtype: class
        """
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
        Метод возвращает класс встроенного пользователя

        :return: класс EmbeddedUser
        :rtype: class
        """
        return EmbeddedUser

    @staticmethod
    def get_link_object():
        """
        Метод возвращает класс для организации связей в базе данных

        :return: класс Link
        :rtype: class
        """
        return Link

    @staticmethod
    def get_app_root_tpl():
        """
        Тестовый метод для заглушки корневого шаблона приложения

        :return: имя файла тестового наблона
        :rtype: str
        """
        return '_test_base.html'

    @staticmethod
    def get_root_tpl():
        """
        Метод возвращает базовый имя базового шаблона для административного интерфейса

        :return: имя файла шаблона
        :rtype: str
        """
        pth = ''
        # pth += AdminConf.MOD_NAME
        # pth += os.path.sep
        # pth += os.path.basename(AdminConf.get_web_tpl_path())
        # pth += os.path.sep
        pth += AdminConf.get_root_tpl()
        return pth

    @staticmethod
    def get_config_path():
        """
        Метод возвращает абсолютный путь к директории с файлами конфигурации

        :return: абсолютный путь
        :rtype: str
        """
        pth = ''
        # if os.path.exists(AdminConf.CONFIGS_PATH) and os.listdir(AdminConf.CONFIGS_PATH):
        #     pth = AdminConf.CONFIGS_PATH
        # else:
        pth = os.path.join(AdminConf.SELF_PATH, AdminConf.INIT_DIR_NAME, AdminConf.CONF_DIR_NAME)
        return pth

    @staticmethod
    def set_portal_theme(theme_id):
        """
        Метод устанавливает актуальную тему на портале по ее идентификатору theme_id

        :param str theme_id: идентификатор темы для плагина Flask_Themes 2
        :return: True если тема установлена для портала, False в противном случае
        :rtype: bool
        """
        flg = False
        # get_app_config().get('main.Interface.Theme')
        _full_key = 'main.Interface.Theme'
        _conf = AdminUtils.get_portal_config()
        _old_theme = _conf.get(_full_key)
        file_name = _full_key.split('.')[0]
        # теперь надо получить файл конфига
        from .configurator_utils import ConfiguratorUtils
        conf_file = ConfiguratorUtils.get_conf_file(file_name)
        if os.path.exists(conf_file):
            _main_conf = AdminUtils.ini2dict(conf_file)
            _k = _main_conf
            splited = _full_key.split('.')[1:] # отрезаем файл
            for step in splited:
                if step == splited[-1]:
                    _k[step] = theme_id
                else:
                    _k = _k[step]
            flg = AdminUtils.dict2ini(conf_file, _main_conf)
        return flg

    def get_ext_func_navi(self, _user):
        """
        Метод возвращает список ссылок дополнительной функциональности для пользователя _user.
        Если пользователю _user назначена роль extended_admin, то добавляется ссылка для скачивания лога авторизации.
        Если пользователь _user является администратором портала, то добавляется ссылка для перехода в административный интерфейс.

        :param object _user: экземпляр класса модели пользователя
        :return: список ссылок
        :rtype: list
        """
        _lst = []
        """
        <li><a href="/portal/uacclog/export/excel/">Access log export</a></li>
        дополнительно ссылку на административный интерфейс для рута
        """
        if _user is not None and hasattr(_user, 'has_role'):
            from flask import url_for
            _conf = AdminUtils.get_portal_config()
            _i = 1
            ext_adm_role = _conf.get('users.Roles.extAdminRole')
            if _user.has_role(ext_adm_role):
                _ti = self.__get_link_tpl()
                _ti['id'] = _i
                _ti['srtid'] = _i
                _ti['roles'] = ext_adm_role
                _ti['label'] = 'Экспорт лога авторизации пользователей'
                _ti['href'] = url_for('portal.__export_users_log')  # '/portal/uacclog/export/excel/'
                _ti['code'] = 'ExportAccessLog'
                _lst.append(_ti)
                _i += 1
                pass
            _mad_role = '_ur_' + os.path.dirname(__file__)
            if _user.has_role(_mad_role):
                _ti = self.__get_link_tpl()
                _ti['id'] = _i
                _ti['srtid'] = _i
                _ti['roles'] = _mad_role
                _ti['label'] = 'Административный интерфейс'
                _ti['href'] = url_for(AdminConf.MOD_NAME + '.index')  # '/portal'
                _ti['code'] = 'PortalAdminLink'
                _lst.append(_ti)
                _i += 1
                pass
        return _lst

    @staticmethod
    def __get_link_tpl():
        """
        Вспомогательный private метод возвращающий шаблон элемента навигации

        :return: шаблон элемента навигации
        :rtype: dict
        """
        tpl = {}
        tpl = {"id": 0, "label": "", "rules": "", "href": "", "parid": 0, "srtid": 1,
               "page": [], "icon": "", "thumb": "", "descr": "",
               "url_func": "", "code": "", "roles": ""}
        return tpl

    def get_portal_mode_util(self):
        """
        Метод возвращает утиллиту для работы с режимами портала.

        :return: утиллита для работы с режимами портала
        :rtype: PortalModeUtil
        """
        from app.admin_mgt.portal_mode_util import PortalModeUtil
        try:
            _util = PortalModeUtil()
        except Exception as ex:
            _msg = self._debug_name + '.get_portal_mode_util.Exception: ' + str(ex)
            print(_msg)
            raise Exception(_msg)
        return _util

    def get_portal_version(self):
        """
        Функция возвращает идентификатор версии портала.

        :return: version
        :rtype: str
        """

        _v = ''
        _v = AdminUtils.get_build_version()
        return _v

# -*- coding: utf-8 -*-
import os
from datetime import datetime
import ldap3
import configparser

from .mod_utils import ModUtils


class Driver():
    _class_file = __file__
    _debug_name = 'LDAPAuthDriver'
    _type = 'LDAP'
    _conf_ext = 'ini'
    _conf_root = 'ldap'
    _servers = ModUtils().get_mod_servers_path()
    _logs = os.path.join(_conf_root, 'logs')

    def __init__(self, config_root=''):
        self._vars = {}
        self._errors = {}
        self._conn = None
        self._servers_confs_path = self._servers
        self._logon_name = ''
        self._is_active_directory = False
        self._dyn_search_filter = ''
        if os.path.exists(config_root) and os.path.isdir(config_root):
            self._conf_root = config_root
            self._servers = os.path.join(self._conf_root, 'servers')
            self._logs = os.path.join(self._conf_root, 'logs')

        # checked servers for instance
        self._checked_DCs = []
        # logining find user
        self._logining_find_user = None
        self._user_cDC = None  # описание сервера к которому смог забиндится пользователь
        self._errors2log = []

    def set_logs_dir(self, _pth):
        """
        Метод для изменения директории файлов логирования
        так как изначально директория располагается рядом с конфигурацией
        :param str _pth: путь к директории для хранения логов для данного драйвера
        :return: None
        """
        if _pth and os.path.exists(_pth) and os.path.isdir(_pth):
            _mod_name = ModUtils().get_mod_name()
            if _mod_name not in _pth.split(os.path.sep):
                _pth = os.path.join(_pth, _mod_name)
                try: os.mkdir(_pth)
                except: pass
            self._logs = str(_pth)

    def _get_ulog_name(self, _func_name='login'):
        _name = self._logon_name + '-' + _func_name
        _name += '-' + ModUtils().formated_time_mark('%Y%m%d')
        _name += '.log'
        return _name

    def _dump_errors(self):
        pass
        # проверка создания файла лога с функцией и именем пользователя
        # создаем файл лога с именем пользователя
        # если
        if self._errors2log:
            if not os.path.exists(self._logs):
                try: os.mkdir(self._logs)
                except: pass
            _log = os.path.join(self._logs, self._get_ulog_name())
            _txt = os.linesep.join(self._errors2log)
            with open(_log, 'w', encoding='utf8') as fp:
                fp.write(_txt)

    def _clear_logs(self):
        if os.path.exists(self._logs):
            _items = os.scandir(self._logs)
            for _fi in _items:
                _nfi = _fi.name
                if _nfi.startswith(self._logon_name + '-'):
                    os.unlink(os.path.join(self._logs, _nfi))

    def _log_error(self, _message=''):
        if '' == _message:
            _message = 'Undefined error!'
            if self._errors and 'last_error' in self._errors and self._errors['last_error']:
                _message = self._errors['last_error']
        _time = ModUtils().formated_time_mark()
        _line = '[' + _time + '] ' + _message
        self._errors2log.append(_line)

    def login(self, u_name, u_secret):
        flg = False
        self._logining_find_user = None # для инициализации и сброса
        self._logon_name = u_name
        if not self._check_DCs():
            # write to log - No available servers
            # print(self._debug_name +'.login->No available servers')
            self._log_error(self._debug_name +'.login->No available servers')
            self._dump_errors()  # так как выпадаем до конца функции
            return flg
        DC_conf = self._get_user_DC(u_name, u_secret)
        if not DC_conf:
            # не получили конфигурацию сервера для пользователя
            # print(self._debug_name +'.login->No server configuration for user: ', u_name)
            self._log_error(self._debug_name +'.login->No server configuration for user: ' + str(u_name))
            self._dump_errors()  # так как выпадаем до конца функции
            return flg
        # пытаемся соединиться
        self.connect(DC_conf)
        u_name = self.format_uname(u_name) # не знаю как по ссылке менять значение
        flg = self.ldap_login(u_name, u_secret)
        if flg:
            # теперь будем искать пользователя
            # чтобы проверить его группу на соответствие условия доступа
            ldap_user = None
            ldap_user = self.search_ldap_user(self._logon_name)
            self._logining_find_user = ldap_user
            if ldap_user:
                flg = True
            else:
                flg = False
                if self._conn is not None:
                    if self._conn.bound and not self._conn.closed:
                        self._logining_find_user = self.__cook_connection_user()
        if not flg:
            self._dump_errors()
        else:
            self._clear_logs()
        return flg

    def __check_logining_login(self, _2check):
        _flg = False
        if not self._logining_find_user:
            return _flg
        if 'login' in self._logining_find_user:
            if self._is_active_directory:
                _2check = str(_2check) + '@'
            else:
                _2check = 'uid=' + str(_2check) + ','
            _flg = self._logining_find_user['login'].startswith(_2check)
        else:
            server = self._var_get('CurrentServer')
            if server is not None:
                login_field = server['Attributes']['Login']
                _flg = self._logining_find_user[login_field] == _2check
            else:
                _flg = self._logining_find_user['uid'] == _2check
        return _flg

    def get_user(self, login):
        data = None
        w = None
        # переменная заполняется методом логин
        if self.__check_logining_login(login):
            w = self._logining_find_user
        if w is None:
            w = self.search_ldap_user(login)
        server = self._var_get('CurrentServer')
        if w and server:
            data = {}
            data = self.__cook_fake_user(login)
            data['login'] = login
            data['name'] = ''
            str1 = ''
            str2 = ''
            if server['Attributes']['Firstname'] in w and w[server['Attributes']['Firstname']]:
                str1 = w[server['Attributes']['Firstname']]
            if server['Attributes']['Lastname'] in w and w[server['Attributes']['Lastname']]:
                str2 = w[server['Attributes']['Lastname']]
            if str2:
                str1 += ' ' + str2
            if '' == str1:
                str1 = login
            data['name'] = str1
            str1 = ''
            data['email'] = ''
            if server['Attributes']['Email'] in w and w[server['Attributes']['Email']]:
                str1 = w[server['Attributes']['Email']]
            if '' == str1:
                str1 = self.cook_fake_mail(login)
            data['email'] = str1
            data['password'] = self.cook_usecret(data, 'password')
        return data

    def __cook_fake_user(self, login):
        _fake = {}
        _fake['login'] = login
        _fake['name'] = login
        _fake['email'] = self.cook_fake_mail(login)
        _fake['password'] = self.cook_usecret(_fake, 'password')
        return _fake

    def cook_usecret(self, data, field):
        secret = ''
        login = data['login']
        base = self.cook_fake_mail(login)
        from hashlib import sha1
        secret = sha1(base.encode()).hexdigest()
        return secret

    def cook_fake_mail(self, login):
        fake = ''
        server = self._var_get('CurrentServer')
        domain = server['Directory']['Domen']
        if '' == domain:
            base_dn = server['Directory']['BaseDN']
            domain = self.get_domain_from_base_dn(base_dn)
        fake = '{}@{}'.format(login, domain)
        return fake

    def __cook_connection_user(self):
        _u = {}
        if self._conn is not None:
            _u['login'] = self._conn.user
            ldap_attributes = self.get_ldap_attributes()
            if ldap_attributes:
                for _a in ldap_attributes:
                    _u[_a] = ''
        return _u

    def search_ldap_user(self, login):
        u_name, u_domain = self.parse_uses_username(login)
        server = self._var_get('CurrentServer')
        user = None
        if server is not None:
            base_dn = server['Directory']['BaseDN']
            search_filter = server['Directory']['Filter']
            login_field = server['Attributes']['Login']
            if '' == search_filter:
                search_filter = '({}={})'.format(login_field, u_name)
            else:
                search_filter = search_filter.rstrip(')')
                search_filter = search_filter.lstrip('(')
                search_filter = '(&({})({}={}))'.format(search_filter, login_field, u_name)
            ldap_attributes = []
            ldap_attributes = self.get_ldap_attributes()
            if self._conn is not None:
                self._dyn_search_filter = search_filter
                search_result = None
                try:
                    self._conn.search(base_dn, search_filter, attributes=ldap_attributes)
                    if self._conn.last_error:
                        print(self._debug_name + '.search_ldap_user -> after search self._conn.last_error: ', str(self._conn.last_error))
                        self._log_error(self._debug_name + '.search_ldap_user -> after search self._conn.last_error: ' + str(self._conn.last_error))
                    if self._conn.entries:
                        search_result = self._conn.entries
                except Exception as ex:
                    print(self._debug_name +'.search_ldap_user Error: ', ex)
                    self._log_error(self._debug_name +'.search_ldap_user Exception: ' + str(ex))
                    if self._conn.last_error:
                        print(self._debug_name + '.search_ldap_user -> self._conn.last_error(on Exception): ', str(self._conn.last_error))
                        self._log_error(self._debug_name + '.search_ldap_user -> self._conn.last_error(on Exception): ' + str(self._conn.last_error))
                if search_result:
                    user = self.search_result_format(search_result)
        return user

    def result_record_to_dict(self, record, attrs=None):
        if attrs is None:
            attrs = self.get_ldap_attributes()
        result = {}
        for att in attrs:
            result[att] = str(record[att]) if record[att] else ''
        return result

    def search_result_format(self, data):
        result = None
        if data:
            attrs = self.get_ldap_attributes()
            self._var_set('attrs', attrs)
            result = []
            for item in data:
                result.append(self.result_record_to_dict(item))
        if result is not None and 1 == len(result):
            result = result[0]
        return result

    def get_ldap_attributes(self):
        server = self._var_get('CurrentServer')
        attrs = []
        if server:
            k = 'Attributes'
            if k in server and server[k]:
                for att in server[k]:
                    attrs.append(server[k][att])
        return attrs

    def ldap_login(self, u_name, u_secret):
        flg = False
        # print(self._debug_name + '.ldap_login: call')
        if self._conn is not None:
            try:
                _flg = self._conn.rebind(u_name, u_secret)
                flg = _flg
            except Exception as ex:
                print(self._debug_name + '.ldap_login.Exception: ' + str(ex))
                if self._conn.last_error:
                    print(self._debug_name + '.ldap_login -> self._conn.last_error: ', str(self._conn.last_error))
                flg = False
        if not flg:
            self._log_error(self._debug_name + '.ldap_login.resutl -> FAIL!')
        return flg

    def format_uname(self, uname, server=None):
        if server is None:
            server = self._var_get('CurrentServer')
        if self.is_active_directory(server):
            u_name, u_domain = self.parse_uses_username(uname)
            domain = server['Directory']['Domen']
            if '' == domain:
                base_dn = server['Directory']['BaseDN']
                domain = self.get_domain_from_base_dn(base_dn)
            uname = '{}@{}'.format(u_name, domain)
        else:
            base_dn = server['Directory']['BaseDN']
            uname = 'uid={},{}'.format(uname, base_dn)
        return uname

    def is_active_directory(self, server=None):
        if server is not None:
            flg = True if 1==server['Info']['ActiveDirectory'] or '1'==server['Info']['ActiveDirectory'] else False
        else:
            flg = self._is_active_directory
        return flg

    def connect(self, server_cfg=None):
        version = 3
        host = ''
        port = 389
        if server_cfg is None:
            server_cfg = self.get_actual_server()
        if not server_cfg:
            return None
        host = server_cfg['Info']['Host']
        port = server_cfg['Info']['Port']
        version = server_cfg['Info']['Version']
        ldaps = server_cfg['Info']['LDAPS']
        self._is_active_directory = True if (1==server_cfg['Info']['ActiveDirectory'] or '1'==server_cfg['Info']['ActiveDirectory']) else False
        if 'on' == ldaps.lower():
            host = 'ldaps://' + host
        try:
            self._conn = self._ldap_connect(host, port)
            self._var_set('CurrentServer', server_cfg)
        except Exception as ex:
            print(self._debug_name + '.connect.Exception: ', str(ex))
            self._conn = None

    def get_actual_server(self):
        server = None
        # print(self._debug_name + '.get_actual_server')
        if self._checked_DCs:
            available = self._checked_DCs
            # print(self._debug_name + '.get_actual_server: use _checked_DCs')
            server = available[0]
        else:
            servers = self._get_servers()
            if servers:
                for srv in servers:
                    host = srv['Info']['Host']
                    port = srv['Info']['Port']
                    if self._check_server_connect(host, port):
                        if srv not in self._checked_DCs:
                            # print(self._debug_name +'._check_DCs add new checked server -> ' + str(datetime.now()))
                            self._checked_DCs.append(srv)
                        server = srv
        return server

    def _get_user_DC(self, login, pswd):
        user_DC = None
        u_name, u_domain = self.parse_uses_username(login)
        user_DC = self.get_dcconf_by_domain(u_domain)
        """
        Если не смогли по домену найти конфигурацию сервера по домену пользователя
        пытаемся выполнить поиск по доступным серверам через ldap_login
        """
        if not user_DC:
            servers = self.get_available_servers()
            if servers:
                for srv in servers:
                    host = srv['Info']['Host']
                    port = srv['Info']['Port']
                    try:
                        self.connect(srv)
                        if self._conn is not None:
                            u_name = self.format_uname(login, srv)
                            if self.ldap_login(u_name, pswd):
                                user_DC = srv
                                break
                    except Exception as ex:
                        print(self._debug_name +'._get_user_DC: Exception ', ex)
                        user_DC = None

        return user_DC

    def get_dcconf_by_domain(self, str_domain):
        srv_conf = None
        servers = []
        if not str_domain:
            return srv_conf
        servers = []
        servers = self.get_available_servers()
        if 0 < len(servers):
            for srv in servers:
                domain = srv['Directory']['Domen']
                if str_domain == domain:
                    srv_conf = srv
                    break
                else:
                    domain = self.get_domain_from_base_dn(srv['Directory']['BaseDN'])
                    if str_domain == domain:
                        srv_conf = srv
                        break
                    else:
                        domain = srv['Info']['Name']
                        if str_domain == domain:
                            srv_conf = srv
                            break
        servers = None
        return srv_conf

    def get_domain_from_base_dn(self, base_dn):
        domain = ''
        key = 'DC'
        dc_pos = base_dn.find(key)
        if -1 < dc_pos:
            str1 = base_dn[dc_pos:]
            splita = str1.split(',')
            for pair in splita:
                key_val = pair.split('=')
                domain += '.' + key_val[1]
            domain = domain[1:]
        return domain

    @staticmethod
    def parse_uses_username(uname):
        delim = ''
        pos_un = -1
        pos_d = -1
        u_name = ''
        u_domain = ''
        if -1 < uname.find('@'):
            delim = '@'
            pos_un = 0
            pos_d = 1
        if -1 < uname.find('\\'):
            delim = '\\'
            pos_un = 1
            pos_d = 0
        if '' != delim:
            uname_list = uname.split(delim)
            if (-1 < pos_un and pos_un < len(uname_list)) \
                and (-1 < pos_d and pos_d < len(uname_list)):
                u_name = uname_list[pos_un]
                u_domain = uname_list[pos_d]
        else:
            if '' != uname:
                u_name = uname
        return [u_name, u_domain]

    def _check_DCs(self):
        flg = False
        cnt = 0
        servers = self._get_servers()
        if 0 < len(servers):
            for srv in servers:
                host = srv['Info']['Host']
                port = srv['Info']['Port']
                if self._check_server_connect(host, port):
                    if srv not in self._checked_DCs:
                        self._checked_DCs.append(srv) #  сохраняем проверенные
                    cnt += 1
        if 0 < cnt:
            flg = True
        return flg

    def _get_servers(self):
        servers = []
        # if os.path.exists(self._servers_confs_path) \
        #     and os.path.isdir(self._servers_confs_path):
        #     files = os.scandir(self._servers_confs_path)
        #     for fI in files:
        #         try:
        #             srv_conf = self.ini2dict(os.path.join(self._servers_confs_path, fI.name))
        #             servers.append(srv_conf)
        #         except:
        #             # что-то не так с файлом конфигурации сервера
        #             continue
        servers = ModUtils().get_servers()
        self._count_DC_conf = len(servers)
        return servers

    def _ldap_connect(self, host, port):
        self._init_errors()
        port = int(port)
        server = ldap3.Server(host, port=port)
        conn = None
        try:
            conn = ldap3.Connection(server)
        except Exception as ex:
            print(self._debug_name + '._ldap_connect->ldap3.Connection(server).Exception: ', str(ex))
            if conn and conn.last_error:
                self._errors['last_error'] = conn.last_error
            conn = None

        if conn and conn.last_error:
            self._errors['last_error'] = conn.last_error
            print(self._debug_name + '._ldap_connect->last_error: ', str(conn.last_error))
        return conn

    def _init_errors(self):
        self._errors = {}

    def get_available_servers(self):
        servers = []
        available = []
        # print(self._debug_name + '.get_available_servers: call')
        if self._checked_DCs:
            available = self._checked_DCs
            # print(self._debug_name + '.get_available_servers: use _checked_DCs')
        else:
            servers = self._get_servers()
            if 0 < len(servers):
                # print(self._debug_name + '.get_available_servers: check from _get_servers')
                for srv in servers:
                    host = srv['Info']['Host']
                    port = srv['Info']['Port']
                    if self._check_server_connect(host, port):
                        if srv not in self._checked_DCs:
                            self._checked_DCs.append(srv) #  сохраняем проверенные
                        available.append(srv)
        return available

    def _check_server_connect(self, host, port):
        flg = False
        # print(self._debug_name + '._check_server_connect: call')
        try:
            conn = self._ldap_connect(host, port)
            _bind_flg = conn.bind()
            # print(self._debug_name + '._check_server_connect bind:', _bind_flg)
            # Возможно нужно будет делать простой запрос поиска
            _unbind_flg = conn.unbind()
            # print(self._debug_name + '._check_server_connect unbind:', _unbind_flg)
            flg = True
        except Exception as ex:
            print(self._debug_name + '._check_server_connect Exception:', ex)
            print(self._debug_name + '._check_server_connect Exception (connect to):', 'host: %s | port: %s' % (host, port))
            flg = False
        # print(self._debug_name + '._check_server_connect: result -> ', flg)
        return flg

    def set_servers_conf_path(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            self._servers_confs_path = path
            return True
        else:
            return False

    def _var_set(self, var, data):
        self._vars_init()
        self._vars[var] = data

    def _var_get(self, var):
        if not self._var_chek(var):
            raise Exception(self._debug_name + '._var_get: Undefined variable "{}"'.format(var))
        return self._vars.get(var)

    def _var_chek(self, var):
        if 0 == len(self._vars):
            return False
        return var in self._vars

    def _vars_init(self):
        if not isinstance(self._vars, dict):
            self._vars = {}

    @staticmethod
    def ini2dict(file_path):
        data = None
        if os.path.exists(file_path) and os.path.isfile(file_path):
            base_name = os.path.basename(file_path)
            _parser = configparser.ConfigParser()
            # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
            _parser.optionxform = str
            _parser.read(file_path, encoding='utf8')
            data = {}
            for section in _parser:
                # ConfigParser add DEFAULT section
                # if DEFAULT -> continue
                if 'DEFAULT' == section:
                    continue
                data[section] = Driver._section_to_dict(_parser[section])
        return data

    @staticmethod
    def _section_to_dict(section):
        d = {}
        for k in section:
            if Driver._option_is_section(k):
                ssk = Driver._parse_section_key(k)
                if ssk[0] not in d:
                    d[ssk[0]] = {}
                if ssk[1] not in d[ssk[0]]:
                    d[ssk[0]][ssk[1]] = {}
                d[ssk[0]][ssk[1]] = section[k]
            else:
                d[k] = section[k]
        return d

    @staticmethod
    def _option_is_section(name):
        return -1 < name.find('[') and name.endswith(']')

    @staticmethod
    def _parse_section_key(section_key):
        ssk = section_key.split('[')
        ssk[1] = ssk[1].rstrip(']')
        return ssk

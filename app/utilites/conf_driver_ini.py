from os import path as opath
import configparser


class ConfigDriverIni:

    def __init__(self, file_name=''):
        self._file_name = ''
        self._parser = None # configparser.ConfigParser
        if file_name:
            self.set_file(file_name)

    def get(self, key_list):
        val = None
        self._init_parser()
        # по идее первый элемент ключа это секция
        if self._parser.has_section(key_list[0]):
            val = self._section_to_dict(self._parser[key_list[0]])
            t = key_list[1:]
            for k in t:
                if k not in val:
                    k = k.lower()
                if isinstance(val, dict) and k in val:
                    val = val[k]
        return val

    def set_file(self, file_name):
        if opath.exists(file_name) and opath.isfile(file_name):
            self._file_name = file_name

    def _init_parser(self):
        if self._parser is None:
            self._parser = configparser.ConfigParser()
            self._parser.optionxform = str
        self._parser.read(self._file_name, encoding='utf8')

    def to_dict(self):
        data = None
        if opath.exists(self._file_name) and opath.isfile(self._file_name):
            base_name = opath.basename(self._file_name)
            fn_list = base_name.split('.')
            if 'ini' == fn_list[1]:
                self._init_parser()
                data = {}
                for section in self._parser:
                    # ConfigParser add DEFAULT section
                    # if DEFAULT -> continue
                    if 'DEFAULT' == section:
                        continue
                    data[section] = self._section_to_dict(self._parser[section])
        return data

    def _section_to_dict(self, section):
        d = {}
        for k in section:
            if self._option_is_section(k):
                ssk = self._parse_section_key(k)
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

# -*- coding: utf-8 -*-
import os


class CodeHelper:
    _class_file = __file__
    _debug_name = 'CodeHelper'

    @staticmethod
    def write_to_file(file_path, istr='', mod='a'):
        if CodeHelper.check_file(file_path):
            CodeHelper.__write_to_file(file_path, mod, istr)
            return True
        return False

    @staticmethod
    def remove_file(file_path):
        if CodeHelper.check_file(file_path):
            os.unlink(file_path)
            return not CodeHelper.check_file(file_path)
        return False

    @staticmethod
    def add_file(file_path):
        CodeHelper.__write_to_file(file_path)
        return not CodeHelper.check_file(file_path)

    @staticmethod
    def read_file(file_path, mod='r'):
        txt = ''
        if CodeHelper.check_file(file_path):
            txt = CodeHelper.__read_from_file(file_path, mod)
        return txt

    @staticmethod
    def get_file(file_path, mod='r'):
        fp = None
        if CodeHelper.check_file(file_path):
            fp = open(file_path, mod, encoding="utf-8")
        return fp

    @staticmethod
    def __write_to_file(file_path, mod='w', idata=''):
        with open(file_path, mod, encoding="utf-8") as file_p:
            file_p.write(idata)

    @staticmethod
    def __read_from_file(file_path, mod='r'):
        idata = None
        with open(file_path, mod, encoding="utf-8") as file_p:
            idata = file_p.read()
        return idata

    @staticmethod
    def check_dir(dir_path):
        return CodeHelper.check_fs_item(dir_path) and os.path.isdir(dir_path)

    @staticmethod
    def is_empty_dir(dir_path):
        if not CodeHelper.check_dir(dir_path):
            raise Exception('Directory "{}" does not exists!'.format(dir_path))
        flist = CodeHelper.get_dir_content(dir_path)
        return (0 == len(flist))

    @staticmethod
    def get_dir_content(dir_path):
        content = []
        if CodeHelper.check_dir(dir_path):
            _t = os.scandir(dir_path)
            content = [fi.name for fi in _t]
        return content

    @staticmethod
    def check_file(file_path):
        return CodeHelper.check_fs_item(file_path) and os.path.isfile(file_path)

    @staticmethod
    def check_fs_item(item_path):
        return os.path.exists(item_path)

    @staticmethod
    def get_mime4file_ext(file_ext):
        mime = ''
        mimes = {}
        mimes['xml'] = 'text/xml'
        mimes['ttl'] = 'text/turtle'
        mimes['txt'] = 'text/plain'
        mimes['rq'] = 'application/sparql-query'
        mimes['nt'] = 'text/plain'
        mimes['nq'] = 'text/x-nquads'
        mimes['nqx'] = 'application/x-extended-nquads'
        mimes['trig'] = 'application/trig'
        if file_ext in mimes:
            mime = mimes[file_ext]
        return mime

    @staticmethod
    def str_to_hash(some_str):
        from hashlib import sha1
        return sha1(some_str.encode('utf-8')).hexdigest()

    @staticmethod
    def dict_combine(_keys, _vals):
        _t = {}

        def _get_val(_kv):
            if _kv < len(_vals):
                return _vals[_kv]
            else:
                return ''
        _i = 0
        for _k in _keys:
            _t[_k] = _get_val(_i)
            _i +=1

        return _t

    @staticmethod
    def translit_rus_string(ru_str):
        """
        матрица составлена согласно:
        https://ru.wikipedia.org/wiki/%D0%A2%D1%80%D0%B0%D0%BD%D1%81%D0%BB%D0%B8%D1%82%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D1%8F_%D1%80%D1%83%D1%81%D1%81%D0%BA%D0%BE%D0%B3%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D0%B0_%D0%BB%D0%B0%D1%82%D0%B8%D0%BD%D0%B8%D1%86%D0%B5%D0%B9
        :param ru_str:
        :return:
        """
        res = ''
        rusAlph = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т',
                   'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я',
                   'а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т',
                   'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я'
                   ]
        engAlph = ['A', 'B', 'V', 'G', 'D', 'E', 'E', 'Zh', 'Z', 'I', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S',
                   'T', 'U', 'F', 'Kh', 'Ts', 'Ch', 'Sh', 'Shch', 'Ie', 'Y', '', 'E', 'Iu', 'Ia',
                   'a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'i', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 's',
                   't', 'u', 'f', 'kh', 'ts', 'ch', 'sh', 'shch', 'ie', 'y', '', 'e', 'iu', 'ia'
                   ]
        # теперь перебираем строку - ищем в руском символ берем индекс и по индексу подставляем значение из латинского
        str_len = len(ru_str)
        for ix in range(0, str_len):
            char = ru_str[ix]
            if char in rusAlph:
                idx = rusAlph.index(char)
                res += engAlph[idx]
            else:
                res += char
        return res

    @staticmethod
    def get_counters_object():
        class Counters:
            _class_file = __file__

            def __init__(self):
                self._d = {}

            def enc(self, name):
                if name not in self._d:
                    self._d[name] = 0
                self._d[name] += 1

            def dec(self, name):
                if name not in self._d:
                    self._d[name] = 0
                self._d[name] -= 1

            def get(self, name):
                if name in self._d:
                    return self._d[name]
                return 0

        return Counters()

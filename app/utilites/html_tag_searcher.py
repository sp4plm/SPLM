import re
from os import path as ospath


class HtmlTagSearcher:
    _class_file = __file__
    _debug_name = 'HtmlTagSearcher'
    _start_tag = '(&lt;|<)'
    _quote = '(&quot;|\")'
    _not_quote = '[^\"]+'

    def __init__(self):
        self.marks = []
        self._compiled_marks = []

    def has_any_marks(self, file_path):
        flg = False
        # возможно нужна проверка на тип файлового содержимого - только текст
        if not ospath.exists(file_path) or not ospath.isfile(file_path):
            return flg
        with open(file_path, 'r', encoding='utf-8') as fp:
            mark = self._compile_global_mark()
            data = re.findall(mark, fp.read(), flags=re.I & re.U)
            if data:
                flg = True
        return flg

    def has_marks(self, file_path):
        res = {}
        # возможно нужна проверка на тип файлового содержимого - только текст
        if not ospath.exists(file_path) or not ospath.isfile(file_path):
            return res
        self._compile_marks()
        for mark in self._compiled_marks:
            if not mark:
                continue  # пропускаем пустоту
            data = None
            with open(file_path, 'r', encoding='utf-8') as fp:
                data = re.findall(mark, fp.read(), flags=re.I & re.U)
            if data:
                res[self._mark2tag(mark)] = data
        return res

    def _compile_marks(self):
        if self.marks:
            for mark in self.marks:
                compiled = self._compile_mark(mark)
                if compiled:
                    self._compiled_marks.append(self.mark2re(compiled))

    def _compile_mark(self, mark_obj):
        # {'tag': '', 'attribute': '' }
        compiled = ''
        if self.is_tag_mark(mark_obj):
            # надо определить значение атрибута регуляркой [^\"]*
            # сейчас не участвует &quot;
            compiled = '((&lt;|<){tag}.+{attribute}=(&quot;|\")(.+)(&quot;|\")(.*)/?(&gt;|>))'.format(**mark_obj)
        return compiled

    def _mark2tag(self, mark):
        mark_obj = self._mark_disassembly(mark)
        if self.is_tag_mark(mark_obj):
            return mark_obj['tag']
        else:
            return mark

    def _mark_disassembly(self, mark):
        """"""
        _test = str(mark)
        start_pos = _test.find(')')
        stop_pos = _test.find('.')
        tag = _test[start_pos+1:stop_pos]
        start_pos = _test.find('+')
        stop_pos = _test.find('=')
        attr = _test[start_pos+1:stop_pos]
        mark_obj = {'tag': '', 'attribute': '' }
        mark_obj['tag'] = tag
        mark_obj['attribute'] = attr
        return mark_obj

    def _compile_global_mark(self):
        res = None
        compiled_list = [self._compile_mark(mark_obj) for mark_obj in self.marks if self.is_tag_mark(mark_obj)]
        if compiled_list:
            optimized_list = [mark_obj for mark_obj in compiled_list if mark_obj]
        if optimized_list:
            res = '(' + '|'.join(optimized_list) + ')'
        return self.mark2re(res)

    @staticmethod
    def mark2re(str_mark):
        return r'' + str(str_mark)

    def add_mark(self, tag_mark):
        if HtmlTagSearcher.is_tag_mark(tag_mark):
            self.marks.append(tag_mark)
            return True
        return False

    def set_marks(self, marks_list):
        if marks_list:
            self.marks = marks_list
            return True
        return False

    def get_marks(self):
        return self.marks

    def clear_compiled(self):
        self._compiled_marks = []

    def drop_marks(self):
        self.marks = []

    @staticmethod
    def is_tag_mark(mark_obj):
        flg = False
        # {'tag': '', 'attribute': '' }
        if isinstance(mark_obj, dict) \
                and 'tag' in mark_obj and mark_obj['tag'] \
                and 'attribute' in mark_obj and mark_obj['attribute']:
            flg = True
        return flg

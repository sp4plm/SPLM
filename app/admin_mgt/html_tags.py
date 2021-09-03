# -*- coding: utf-8 -*-


class HtmlTags:
    _class_file = __file__
    _debug_name = 'HtmlTags'

    @staticmethod
    def gen(name, attrs={}, content=''):
        html = ''
        if '' != name:
            name = HtmlTags.service_clear(name)
            if '' != content:
                content = HtmlTags.service_clear(content, False)
            attrs_str = ''
            attrs_str = HtmlTags.dict_to_str(attrs)
            if attrs_str:
                attrs_str = ' ' + attrs_str
            html = '<{}{}>{}</{}>' .format(name, attrs_str, content, name)
        return html

    @staticmethod
    def dict_to_str(src):
        res = ''
        _t1 = []
        if isinstance(src, dict):
            for an, av in src.items():
                an = HtmlTags.service_clear(an)
                if not isinstance(av, str):
                    if isinstance(av, list):
                        av = HtmlTags.list_to_str(av)
                    else:
                        av = str(av)
                av = HtmlTags.service_clear(av, False)
                _t1.append(an + '="' + av + '"')
        if _t1:
            res = ' '.join(_t1)
        return res

    @staticmethod
    def list_to_str(src, breaker=', '):
        res = ''
        _t1 = []
        if isinstance(src, list):
           _t1 = [HtmlTags.service_clear(x, False) for x in src]
        if _t1:
            res = breaker.join(_t1)
        return res

    @staticmethod
    def service_clear(src, strict=True):
        if strict:
            src = src.replace('<', '').replace('>', '').replace('"', '')
        else:
            src = src.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quote;')
        return src

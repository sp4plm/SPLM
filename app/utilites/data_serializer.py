# -*- coding: utf-8 -*-
import pickle


class DataSerializer:
    _class_file = __file__
    _debug_name = 'DataSerializer'

    @staticmethod
    def restore(self, file_name):
        fdata = None
        with open(file_name, 'rb') as fp:
            fdata = pickle.load(fp)
        return fdata

    @staticmethod
    def dump(self, file_name, fdata):
        with open(file_name, 'wb') as fp:
            pickle.dump(fdata, fp, pickle.HIGHEST_PROTOCOL)
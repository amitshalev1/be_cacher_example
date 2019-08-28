# -*- coding: utf-8 -*-
import pickle

def save(filename,to_save,protocol=pickle.HIGHEST_PROTOCOL):
    with open(filename, 'wb') as handle:
        pickle.dump(to_save, handle, protocol=protocol)


def load(filename):
    with open(filename, 'rb') as handle:
        to_return = pickle.load(handle)    
    return to_return


def test():
    return "asdasdasd"
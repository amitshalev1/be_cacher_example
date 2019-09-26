# -*- coding: utf-8 -*-
import pickle
import sys

def save(filename,to_save,protocol=pickle.HIGHEST_PROTOCOL):
    with open(filename, 'wb') as handle:
        pickle.dump(to_save, handle, protocol=protocol)


def load(filename,encoding='latin1'):
    if sys.version_info.major==2:
        with open(filename, 'rb') as handle:
                to_return = pickle.load(handle)
    else:
        with open(filename, 'rb') as handle:
                to_return = pickle.load(handle,encoding=encoding)                                    
    return to_return



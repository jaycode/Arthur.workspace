import os, sys, inspect
import pdb
import glob
import importlib
import string

# This needs to be included here to ensure path loaded from arthur library directory.
base_path = os.path.realpath(
    os.path.abspath(
        os.path.join(
            os.path.split(
                inspect.getfile(
                    inspect.currentframe()
                )
            )[0]
        )
    )
)

def get_clustering_algorithms():
    """Returns list of clusterers.
    """
    modules = []
    for filepath in glob.iglob(os.path.join(base_path, 'clusterer', '*.py')):
        name = __module_from_filepath(filepath)
        if name:
            modules.append(name)
    return modules

def get_clusterer_class(algo):
    if os.path.exists(os.path.join(base_path, 'clusterer', ('%s.py' % algo))):
        module = importlib.import_module("clusterer.%s" % (algo))
        return getattr(module, __camelize(algo))
    else:
        raise IOError('Clusterer not found')

def __module_from_filepath(filepath):
    path = os.path.normpath(filepath)
    path_r = path.split(os.sep)
    filename = path_r[len(path_r)-1]
    module = os.path.splitext(filename)[0]
    if module[0] != '_':
        return module

def __camelize(value):
    """Camelize a variable name.

    e.g. 'dumb_clusterer' to "DumbClusterer".

    >>> __camelize('dumb_clusterer')
    'DumbClusterer'

    """
    return "".join(string.capwords(x) for x in value.split("_"))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
import os
import glob
import pdb

def get_package(command):
    """Decides if command resides inside a package.
    """
    package = ''
    for cur_package, module in get_package_module_pairs():
        if module == command:
            package = cur_package
    return package


def get_package_module_pairs():
    """Iterates over all module/pair inside app/mod_cmd/commands/**/*.py
    """
    sets = []
    for filepath in glob.iglob('app/mod_cmd/commands/**/*.py'):
        pair = __yield_from_filepath(filepath)
        if pair is not None:
            yield pair

def get_base_package_module_pairs():
    """Iterates over all module/pair inside app/mod_cmd/commands/*.py
    """
    sets = []
    for filepath in glob.iglob('app/mod_cmd/commands/*.py'):
        pair = __yield_from_filepath(filepath)
        if pair is not None:
            yield pair

def __yield_from_filepath(filepath):
    path = os.path.normpath(filepath)
    path_r = path.split(os.sep)
    package = path_r[len(path_r)-2]
    filename = path_r[len(path_r)-1]
    module = os.path.splitext(filename)[0]
    if module[0] != '_':
        return (package, module)

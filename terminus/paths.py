import os
from pathlib import Path

def rm_tree(path):
    '''
    Recursive directory removal using pathlib

    path: str, pathlib.Path
        The directory path to recursively delete
    '''

    path = Path(path)
    for child in path.glob('*'):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)

    path.rmdir()

    return

# -----------------------------------------------------------------------------
# TODO: The following methods need to be refatored to use pathlib, as well as
# accept modules as inputs for them to solve the pathing

def make_dir(d):
    '''
    Makes dir if it does not already exist

    d: str, pathlib.Path
    '''

    if isinstance(d, Path):
        d = str(d.resolve())

    if not os.path.exists(d):
        os.makedirs(d)

    return

def get_base_dir():
    '''
    base dir is parent repo dir
    '''
    module_dir = get_module_dir()
    return os.path.dirname(module_dir)

def get_module_dir():
    return os.path.dirname(__file__)

def get_test_dir():
    base_dir = get_base_dir()
    return os.path.join(base_dir, 'tests')

BASE_DIR = get_base_dir()
MODULE_DIR = get_module_dir()
TEST_DIR = get_test_dir()

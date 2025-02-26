import os
import shutil
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

def copy_tree(src, dst, overwrite=False, raise_existing_error=True):
    '''
    Recursive directory copy, with optional overwrite

    Parameters
    ----------
    src: str, Path
        The source directory path to copy
    dst: str, Path
        The destination directory path to copy to
    overwrite: bool
        Whether to overwrite files in the destination directory
    raise_existing_error: bool
        Whether to raise an error if the destination file already exists and
        overwrite is False
    '''

    src = Path(src)
    dst = Path(dst)

    if not dst.exists():
        dst.mkdir(parents=True)
    
    for item in src.iterdir():
        src_item = item
        dst_item = dst / item.name
        
        if src_item.is_dir():
            copy_tree(
                src_item, dst_item, overwrite=overwrite,
                raise_existing_error=raise_existing_error
                )
        else:
            if dst_item.exists():
                if (overwrite is False) and (raise_existing_error is True):
                    raise FileExistsError(
                        f'{dst_item} already exists and overwrite=False'
                    )
            shutil.copy2(src_item, dst_item)

    return

# -----------------------------------------------------------------------------
# TODO: The following methods need to be refatored to use pathlib, as well as
# accept modules as inputs for them to solve the pathing

def make_dir(d: str | Path | None, exists_ok: bool = True) -> None: 
    '''
    Makes dir if it does not already exist.

    Parmeters
    ---------
    d: str, Path
        The directory path to create
    exists_ok: bool; default=True
        Whether to raise an error if the directory already exists. Default is
        True.
    '''

    # this can occasionally happen if insufficient parsing is done before
    # calling this method; usually it is most useful to ignore
    if d is None:
        return

    if isinstance(d, Path):
        d = str(d.resolve())

    if not os.path.exists(d):
        os.makedirs(d)
    elif not exists_ok:
        raise FileExistsError(
            f'{d} already exists and exists_ok=False'
            )

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

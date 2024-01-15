from typing import Any

def check_type(name: str, arg: Any, allowed_types: Any | Tuple):
    '''
    Check if the passed arg is of the allowed types

    name: str
        Name of the arg
    arg: any
        The arg in question
    allowed_types: type; tuple of types
        The required type or tuple of allowed types
    '''

    if isinstance(allowed_types, tuple):
        err_msg = f'{name} must be one of {allowed_types}!'
    else:
        err_msg = f'{name} must be a {allowed_types}!'

    if not isinstance(arg, allowed_types):
        raise TypeError(err_msg)

    return

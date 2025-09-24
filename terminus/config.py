from __future__ import annotations

import yaml
import re
import dataclasses
import numpy as np
import os, datetime, dataclasses, enum, uuid, decimal
from pathlib import Path, PurePath
from collections.abc import Mapping, Sequence

def read_yaml(yaml_file):
    '''
    current package has a problem reading scientific notation as
    floats; see
    https://stackoverflow.com/questions/30458977/yaml-loads-5e-6-as-string-and-not-a-number
    '''

    loader = yaml.SafeLoader
    loader.add_implicit_resolver(
        u'tag:yaml.org,2002:float',
        re.compile(u'''^(?:
        [-+]?(?:[0-9][0-9_]*)\\.[0-9_]*(?:[eE][-+]?[0-9]+)?
        |[-+]?(?:[0-9][0-9_]*)(?:[eE][-+]?[0-9]+)
        |\\.[0-9_]+(?:[eE][-+][0-9]+)?
        |[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\\.[0-9_]*
        |[-+]?\\.(?:inf|Inf|INF)
        |\\.(?:nan|NaN|NAN))$''', re.X),
        list(u'-+0123456789.'))

    with open(yaml_file, 'r') as stream:
        # return yaml.safe_load(stream) # see above issue
        return yaml.load(stream, Loader=loader)

def write_yaml(yaml_dict: dict, yaml_outfile: str, clobber: bool=False):
    '''
    yaml_dict: dict
        The dictionary to save to a yaml config file
    yaml_outfile: str
        The path of the output config file
    clobber: bool
        Whether to overwrite the file if it already exists
    '''

    # some helper methods to handle annoyances with variable references and a few
    # common python types
    class NoAliasDumper(yaml.SafeDumper):
        # Prevent &id / *id anchors
        def ignore_aliases(self, data):
            return True

    def _to_plain(obj):
        """Deep-convert to plain Python types safe for YAML/JSON."""
        # dataclasses
        if dataclasses.is_dataclass(obj):
            obj = dataclasses.asdict(obj)

        # pydantic v2 / v1
        if hasattr(obj, "model_dump"):
            obj = obj.model_dump()
        elif hasattr(obj, "dict") and callable(obj.dict):
            obj = obj.dict()

        # pathlib / os.PathLike -> str
        if isinstance(obj, (PurePath, os.PathLike)):
            return os.fspath(obj)

        # enum -> its value (or name if you prefer)
        if isinstance(obj, enum.Enum):
            return obj.value

        # uuid -> str
        if isinstance(obj, uuid.UUID):
            return str(obj)

        # decimal -> float (or str if you want exact text)
        if isinstance(obj, decimal.Decimal):
            return float(obj)

        # numpy scalars / arrays
        if np is not None:
            if isinstance(obj, np.generic):
                return obj.item()
            if isinstance(obj, np.ndarray):
                return obj.tolist()

        # datetime/date/time -> ISO
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
            return obj.isoformat()

        # mappings (dict-like, including subclasses)
        if isinstance(obj, Mapping):
            # Force string keys; YAML allows non-str keys but it complicates consumers
            return {str(k): _to_plain(v) for k, v in obj.items()}

        # sets & tuples -> lists
        if isinstance(obj, (set, tuple)):
            return [_to_plain(v) for v in obj]

        # sequences (but not strings/bytes)
        if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
            return [_to_plain(v) for v in obj]

        # basic scalar stays as-is (int/float/str/bool/None)
        return obj

    yaml_outfile = Path(yaml_outfile)

    if yaml_outfile.exists():
        if clobber is False:
            raise ValueError(f'{yaml_outfile} already exists! Set clobber=True to overwrite')
        else:
            yaml_outfile.unlink()

    plain = _to_plain(yaml_dict)

    # helper method to handle representation errors for the next YAML write call
    def _find_first_unrepresentable(x, path=""):
        """Return (path, typename, preview) for the first value yaml can't represent."""
        try:
            yaml.dump(x, Dumper=NoAliasDumper)
            return None  # whole object is representable
        except yaml.representer.RepresenterError:
            pass

        if isinstance(x, dict):
            for k, v in x.items():
                p = f"{path}.{k}" if path else str(k)
                bad = _find_first_unrepresentable(v, p)
                if bad:
                    return bad
        elif isinstance(x, (list, tuple, set)):
            for i, v in enumerate(x):
                p = f"{path}[{i}]" if path else f"[{i}]"
                bad = _find_first_unrepresentable(v, p)
                if bad:
                    return bad

        # Leaf (or non-container) that still fails
        return (path or "<root>", type(x).__name__, repr(x)[:200])

    try:
        with open(yaml_outfile, 'w', encoding='utf-8') as f:
            yaml.dump(
                plain,
                f,
                Dumper=NoAliasDumper,   # Safe dumper + no anchors
                sort_keys=False,
                default_flow_style=False,
                allow_unicode=True,
            )
    except yaml.representer.RepresenterError:
        where, typ, preview = _find_first_unrepresentable(plain)
        raise TypeError(
            f"YAML serialization failed at {where} (type {typ}). "
            f"Example value: {preview}"
        )

    return

def recursive_update(d: dict, u: dict) -> dict:
    '''
    Recursively update a dictionary with another dictionary, similarly to dict.update()

    d: dict
        The dictionary to update
    u: dict
        The dictionary to update with

    returns:
    d: dict
        The updated dictionary
    '''

    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = recursive_update(d.get(k, {}), v)
        else:
            d[k] = v

    return d

def check_req_params(config, params, defaults):
    '''
    Ensure that certain required parameters have their values set to
    something either than the default after a configuration file is read.
    This is needed to allow certain params to be set either on the command
    line or config file.

    config: An object that (potentially) has the param values stored as
    attributes
    params: List of required parameter names
    defaults: List of default values of associated params
    '''

    for param, default in zip(params, defaults):
        # Should at least be set by command line arg defaults, but double check:
        if (not hasattr(config, param)) or (getattr(config, param) == default):
            e_msg = f'Must set {param} either on command line or in passed config!'
            raise Exception(e_msg)

    return

def check_req_fields(config: dict, req: list, name: str=None):
    '''
    Check that all required fields are present in the config. If not, raise an error

    config: dict
        The configuration dictionary to check
    req: list of str or tuples
        A list of required field names, or tuples in the format of (name, type)
    name: str
        The name of the config type, for extra print info
    '''

    for entry in req:
        if isinstance(entry, str):
            field = entry
            field_type = None
        elif isinstance(entry, tuple):
            if len(entry) != 2:
                raise ValueError('req tuple must be in the format of (name, type)')
            field = entry[0]
            field_type = entry[1]

        if not field in config:
            raise ValueError(f'{name}config must have field {field}')
        if field_type is not None:
            if not isinstance(config[field], field_type):
                raise TypeError(f'{name}config[{field}] must be a {field_type}')

    return

def parse_config(config: dict, req: list=None, opt: dict=None, name: str=None, allow_unregistered: bool=False, set_defaults=True) -> dict:
    '''
    config: dict
        A configuration dictionary to parse
    req: list of str or tuples
        A list of required field names, or tuples in the format of ('name': type)
    opt: dict
        A dictionary in the format of {'name': default_value} or {'name': (type, default_value)}
    name: str
        Name of config type, for extra print info
    allow_unregistered: bool
        Set to allow fields not registered as a req or optional field
    set_defaults: bool
        Whether to explicitly set all optional fields to their registered default if they are not present in the config
    '''

    if (config is not None) and (not isinstance(config, dict)):
        raise TypeError('config must be a dict')
    if (req is not None)  and (not isinstance(req, list)):
        raise TypeError('req must be a list')
    if (opt is not None) and (not isinstance(opt, dict)):
        raise TypeError('opt must be a dict!')

    if name is None:
        name = ''
    else:
        name = name + ' '

    if req is None:
        req = []
    if opt is None:
        opt = {}

    # ensure all req fields are present
    check_req_fields(config, req, name=name)

    # now check for fields not in either
    if allow_unregistered is False:
        for field in config:
            if (not field in req) and (not field in opt):
                raise ValueError(f'{field} not a valid field for {name}config!')

    # set defaults for any optional field not present in config
    if set_defaults is True:
        for field, value in opt.items():
            if field not in config:
                if isinstance(value, tuple):
                    if len(value) != 2:
                        raise ValueError('opt tuple must be in the format of (type, default_value)')
                    field_type = value[0]
                    default = value[1]

                    if not isinstance(default, field_type):
                        raise TypeError(f'{name}config[{field}] must be a {field_type}')
                else:
                    field_type = None
                    default = value

                if field_type is not None:
                    if not isinstance(default, field_type):
                        raise TypeError(f'{name}config[{field}] registered default must be a {field_type}')
                config[field] = default

    return config

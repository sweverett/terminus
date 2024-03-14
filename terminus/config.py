import yaml
import re
from pathlib import Path

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

    yaml_outfile = Path(yaml_outfile)
    if yaml_outfile.exists():
        if clobber is False:
            raise ValueError(f'{yaml_outfile} already exists! Set clobber=True to overwrite')
        else:
            yaml_outfile.unlink()

    with open(yaml_outfile, 'w') as yaml_file:
        yaml.dump(yaml_dict, yaml_file, default_flow_style=False)

    return

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

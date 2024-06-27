import subprocess
import os
from pathlib import Path

def export_all_conda_envs(out_dir='conda_envs', vb=True):
    '''
    Export all conda environments to yaml files in the out_dir

    TODO: Make --from-history and --no-builds optional, but usually the best
    choice
    '''

    # Get a list of all conda environments
    envs = subprocess.check_output(
        ['conda', 'env', 'list']
        ).decode().split('\n')
    
    # Filter out environment names
    env_names = [
        line.split()[0] for line in envs if line and not line.startswith('#') and 'envs' in line
        ]
    
    # Create a directory to store the YAML files
    os.makedirs(out_dir, exist_ok=True)
    
    # Export each environment to a YAML file
    for env in env_names:
        yaml_file = os.path.join('conda_envs', f'{env}.yaml')

        if vb is True:
            print(f'Writing {env} to {yaml_file}')

        with open(yaml_file, 'w') as f:
            subprocess.run(
                [
                    'conda',
                    'env',
                    'export',
                    '-n', env,
                    '--from-history',
                    '--no-builds'
                ], stdout=f
                )
    
        # Read the YAML file, modify it, and write it back
        with open(yaml_file, 'r') as f:
            lines = f.readlines()
    
        with open(yaml_file, 'w') as f:
            for line in lines:
                if 'defaults' not in line and not line.startswith('prefix:'):
                    f.write(line)
    
    if vb is True:
        print(
            "All environments have been exported to the 'conda_envs' directory."
            )

    return
